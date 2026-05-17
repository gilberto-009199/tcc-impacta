import logging

from app.peer.protocol.msg.msgPieceRequest import MsgPieceRequest

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.application import Application


if __name__ == "__main__":
    logging.info("O aplicativo iniciou!")
    app = Application()
    app.config()
    app.run()

"""
if __name__ == "__main__":
    msg = MsgPieceRequest(
        identifier_file = "71bde8e2d939e1467d892d19f3d820d934e36136",
        71bde8e2d939e1467d892d19f3d820d934e36136
        170f2bb9d668a17c0bd2fd377eb8c0fc9bdad389
        4335833233324f5f9f05198dbebc6a832e9767577ecf99a6
        c05a672788040c832bd8a2ee0b5b09ec22f8a6331cbbd995ea4b
        3d7b623859cefb55598f838a7fd2983155eb7f272cb09cc942c6dd8a5d095bb4
        uRauSDRD+g9zpG8kN0XiclfAk66DKFirpHDsJYev3Ek=
        31406542f84da4fae962c9b546ec1963
        identifier_piece = 0,
        identifier_index = 0,
        buffer_length = 1048576
    )

    packet = msg.toPacket()
    print(f"Packet: {packet.hex()}")

    msg_parsed = MsgPieceRequest.ofPacket(packet)
    print(f"Parsed: {msg_parsed}")

    print(f"Original: {msg}")

    assert msg == msg_parsed, "Erro: mensagens não são iguais"


"""