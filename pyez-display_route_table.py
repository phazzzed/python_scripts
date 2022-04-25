from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
import  uname_pass
import yaml
import sys
import os

def main():

     UID = uname_pass.username 
     PWD = uname_pass.password 
     if len(sys.argv) == 2:
          route_table = sys.argv[1]
     else:
          print('!!!!!!!!!! - exiting, wrong parameters used') 
          print('!!!!!!!!!! - please use: ' + os.path.basename(__file__) + ' <route table>')
          exit() 

     loaded_device_list = yaml.safe_load(open('inventory/juniper_model-all.yaml'))

     for loaded_device in loaded_device_list['devices']:
          
          if loaded_device['type'] == 'router':
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , will perform a route lookup')
               try:
                    with Device(host=loaded_device['ip'], password=PWD, user=UID, normalize=True) as current_device:

                         route_lxml_element = current_device.rpc.get_route_information(table=route_table)
                         list_of_routes = route_lxml_element.findall('.//rt')

                         for route in list_of_routes:
                              print('route: {0} protocol: {1}' .format(route.findtext('rt-destination').strip(), route.findtext('rt-entry/protocol-name').strip()))

               except ConnectError as err:
                    print('!!!!!!!!!! - Thrown ConnectError exception: ' + str(err))
                    continue

          else:
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , skipping route table lookup')

if __name__ == '__main__':
     main()
