from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint

UID = 'eng'
PWD = 'cmn123!'
route_table = 'inet.0'

acx = ['10.126.128.4', '10.126.128.5', '10.126.144.4', '10.126.144.5']
mx = [ '10.126.128.1', '10.126.128.2', '10.126.144.1', '10.126.144.2']

for current_device in acx:
     current_router = Device(host=current_device, password=PWD, user=UID, normalize=True)

     try:
          current_router.open()
     except ConnectError as err:
          print("cannot connect to device: {0}" .format(err))
          continue

     route_lxml_element = current_router.rpc.get_route_information()
     list_of_routes = route_lxml_element.findall('.//rt')
     for route in list_of_routes:
          print('route: {0} protocol: {1}' .format(route.findtext('rt-destination').strip(), route.findtext('rt-entry/protocol-name').strip()))
     current_router.close()
     print('closed connection to: ' + str(current_router.facts['hostname']))

