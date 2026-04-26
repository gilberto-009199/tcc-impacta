import json
import logging
import socket
import struct
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

import signal
import sys
import atexit

from app.util.IPUtil import IPUtil

logger = logging.getLogger(__name__)


MCAST_GROUP = "239.43.0.114"
MCAST_PORT = 48279
PROTO_V = 1


class _DatagramShim:
    """Compatível com o código que esperava respostas SSDP com `.headers`."""

    def __init__(self, headers: Dict[str, Any]):
        self.headers = headers


class DiscoveredPeer:
    """Peer descoberto na LAN, no formato esperado por `SSDPManager.findPeers`."""

    def __init__(self, ip: str, headers: Dict[str, Any]):
        p = headers.get("Port", 0)
        try:
            port_int = int(p)
        except (TypeError, ValueError):
            port_int = 0
        self.src_addr = (ip, port_int)
        self.datagram = _DatagramShim(headers)


def _build_announce_payload(headers: Dict[str, Any]) -> bytes:
    body: Dict[str, Any] = {"v": PROTO_V, "kind": "announce"}
    for k in (
        "Type",
        "Primary-Proxy",
        "Proxies",
        "Manufacturer",
        "Model",
        "Port",
        "Identifier",
        "Driver",
    ):
        if k in headers and headers[k] is not None:
            body[k] = headers[k]
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _parse_message(data: bytes) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(obj, dict) or obj.get("v") != PROTO_V:
        return None
    return obj


def _headers_from_announce(obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "Type": obj.get("Type", ""),
        "Primary-Proxy": obj.get("Primary-Proxy", ""),
        "Proxies": obj.get("Proxies", ""),
        "Manufacturer": obj.get("Manufacturer", ""),
        "Model": obj.get("Model", ""),
        "Port": obj.get("Port", 0),
        "Identifier": obj.get("Identifier", ""),
        "Driver": obj.get("Driver", ""),
    }


class Network:
    """Service discover via UDP multicast + resposta em unicast."""

    def __init__(self):
        self.server_running = False
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sock: Optional[socket.socket] = None
        self._headers: Dict[str, Any] = {}
        self._advertise_interval = 60
        self._lock = threading.Lock()

        logger.info("Network instanciado (multicast %s:%s)", MCAST_GROUP, MCAST_PORT)

    def _open_mcast_socket(self) -> socket.socket:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        s.bind(("", MCAST_PORT))
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(MCAST_GROUP),
            socket.inet_aton("0.0.0.0"),
        )
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("B", 1))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, struct.pack("B", 1))

        def shutdown_handler(signum, frame):
            logger.info(f"Sinal {signum} recebido, derrubando servidor multicast...")
            self.stop_server()
            import sys
            sys.exit(0)
        
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        return s

    def _send_multicast(self, payload: bytes) -> None:
        if self._sock is None:
            return
        try:
            self._sock.sendto(payload, (MCAST_GROUP, MCAST_PORT))
        except OSError as e:
            logger.warning("sendto multicast: %s", e)

    def _unicast_reply(self, addr: tuple[str, int], payload: bytes) -> None:
        if self._sock is None:
            return
        try:
            self._sock.sendto(payload, addr)
        except OSError as e:
            logger.warning("unicast reply to %s: %s", addr, e)

    def _server_loop(self) -> None:
        assert self._sock is not None
        # `start_server` já envia um beacon inicial
        next_beacon = time.monotonic() + self._advertise_interval
        while not self._stop.is_set():
            remaining = next_beacon - time.monotonic()
            timeout = 1.0 if remaining > 1.0 else max(0.05, remaining)
            self._sock.settimeout(timeout)
            try:
                data, addr = self._sock.recvfrom(65507)
            except socket.timeout:
                data = None
            except OSError as e:
                if self._stop.is_set():
                    break
                logger.warning("recv multicast: %s", e)
                data = None

            if data:
                msg = _parse_message(data)
                if msg and msg.get("kind") == "discover":
                    want = msg.get("Type")
                    with self._lock:
                        hdrs = dict(self._headers)
                    if want and hdrs.get("Type") == want:
                        self._unicast_reply(addr, _build_announce_payload(hdrs))

            if time.monotonic() >= next_beacon and not self._stop.is_set():
                with self._lock:
                    hdrs = dict(self._headers)
                if hdrs.get("Type"):
                    self._send_multicast(_build_announce_payload(hdrs))
                next_beacon = time.monotonic() + self._advertise_interval

    def start_server(self, headers, advertise_interval=60):
        self.stop_server()

        port = headers.get("Port")
        try:
            int(port)
        except (TypeError, ValueError):
            logger.error("Port inválida nos headers; não inicia multicast")
            return

        self._advertise_interval = max(5, int(advertise_interval))
        with self._lock:
            self._headers = dict(headers)

        try:
            self._sock = self._open_mcast_socket()
        except OSError as e:
            logger.error("Falha ao abrir socket multicast: %s", e, exc_info=True)
            self._sock = None
            return

        self._stop.clear()
        self._thread = threading.Thread(target=self._server_loop, name="mcast-discover", daemon=True)
        self._thread.start()
        self.server_running = True
        self._send_multicast(_build_announce_payload(dict(headers)))
        logger.info(
            "Multicast discover: ouvindo em %s:%s (beacon a cada %ss)",
            MCAST_GROUP,
            MCAST_PORT,
            self._advertise_interval,
        )

    def stop_server(self) -> None:
        self._stop.set()
        sock = self._sock
        self._sock = None
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
        self.server_running = False
        with self._lock:
            self._headers = {}
        logger.info("Multicast discover: servidor parado")

    def search_services_sync(
        self, pattern: str, wait_time: int = 6, max_responses: int = 10
    ) -> List[Any]:
        discover = json.dumps(
            {"v": PROTO_V, "kind": "discover", "Type": pattern},
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        results: List[DiscoveredPeer] = []
        seen: set[tuple[str, str, Any]] = set()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("", 0))
        except OSError as e:
            logger.error("bind socket busca: %s", e)
            s.close()
            return []

        try:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("B", 1))
        except OSError:
            pass

        local_ips = set(IPUtil.getAllLocalIPs())
        try:
            local_ips.add(IPUtil.getLocalIP())
        except Exception:
            pass

        deadline = time.monotonic() + max(1, wait_time)
        try:
            for _ in range(3):
                try:
                    s.sendto(discover, (MCAST_GROUP, MCAST_PORT))
                except OSError as e:
                    logger.warning("send discover: %s", e)
                    break

            while time.monotonic() < deadline and len(results) < max_responses:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                s.settimeout(min(0.5, remaining))
                try:
                    data, addr = s.recvfrom(65507)
                except socket.timeout:
                    continue
                except OSError as e:
                    logger.debug("recv busca: %s", e)
                    break

                msg = _parse_message(data)
                if not msg or msg.get("kind") != "announce":
                    continue
                if msg.get("Type") != pattern:
                    continue

                ip = addr[0]
                hdrs = _headers_from_announce(msg)
                ident = str(hdrs.get("Identifier", ""))
                try:
                    port_key = int(hdrs.get("Port", 0))
                except (TypeError, ValueError):
                    port_key = hdrs.get("Port", 0)
                dedupe = (ip, ident, port_key)
                if dedupe in seen:
                    continue
                seen.add(dedupe)
                results.append(DiscoveredPeer(ip, hdrs))
        finally:
            s.close()

        logger.info(
            "Multicast discover: %s resposta(s) para Type=%s",
            len(results),
            pattern,
        )
        return results

    def is_server_running(self) -> bool:
        return self.server_running
