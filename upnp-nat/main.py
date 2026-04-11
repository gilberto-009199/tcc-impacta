#from src.app import app






try:
    import socket 
    import upnpy
    from upnpy.exceptions import SOAPError
    socket.setdefaulttimeout(1.8)
    upnp = upnpy.UPnP()

    devices = upnp.discover()

    device = upnp.get_igd()
    device.get_services()


    options = ['WANPPPConnection.1', 'WANIPConn1']
    service = None
    for opt in options:
        if opt in device.services:
            service = device[opt]
            
    service.AddPortMapping.get_input_arguments()
    print("Mapeamento antigo removido com sucesso.")

    try:

        service.DeletePortMapping(
            NewRemoteHost='',
            NewExternalPort=8080,
            NewProtocol='TCP'
        )
    except Exception as e:
        if '718' in str(e):
            print("Conflito detectado: A porta já está mapeada ou em uso.")
        else:
            raise e

    service.AddPortMapping(
        NewRemoteHost='',
        NewExternalPort=8080,
        NewProtocol='TCP',
        NewInternalPort=8080,
        NewInternalClient='192.168.0.116',
        NewEnabled=1,
        NewPortMappingDescription='Meu Servidor',
        NewLeaseDuration=0
    )
except Exception as e:
    if '718' in str(e):
        print("Conflito detectado: A porta já está mapeada ou em uso.")
    else:
        raise e


#if __name__ == "__main__":
    #app.run();

