from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
from lxml import etree
import sys
import uname_pass

UID = uname_pass.username 
PWD = uname_pass.password 

with open(sys.argv[1], 'r') as f:
     lines = [line.rstrip('\n') for line in f]

route_table = sys.argv[2] 

for current_device in lines:
     print('destination ip address we are attempting to login to: ' + current_device) 
     current_router = Device(host=current_device, password=PWD, user=UID, normalize=True)

     try:
          current_router.open()
     except jnpr.junos.exception.ConnectError as err:
          print('cannot connect to device: ' +  repr(err))
          continue

     route_lxml_element = current_router.rpc.get_forwarding_table_information(table=route_table)
     list_of_routes = route_lxml_element.findall('.//rt-entry')

     for route in list_of_routes:
          if route.findtext('nh/nh-type') in ('ucst', 'indr'):
               print('entry: {0} outgoing interface: {1}' .format(route.findtext('rt-destination').strip(), route.findtext('nh/via'.strip())))
     current_router.close()
     print('closed connection to: ' + str(current_router.facts['hostname']))

