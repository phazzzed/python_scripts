from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
from lxml import etree
import sys
import uname_pass
import yaml

def main():

     UID = uname_pass.username 
     PWD = uname_pass.password 

     if len(sys.argv) == 2:
          forwarding_table = sys.argv[1]
     else:
          print('!!!!!!!!!! - exiting, wrong parameters used - !!!!!!!!!!')
          print('!!!!!!!!!! - please use: ' + os.path.basename(__file__) + ' <forwarding table>')
          exit()

     loaded_device_list = yaml.safe_load(open('inventory/juniper_model-all.yaml'))

     for loaded_device in loaded_device_list['devices']:
          if loaded_device['type'] == 'router':
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , will perform a forwarding lookup')
               try:
                    with Device(host=loaded_device['ip'], password=PWD, user=UID, normalize=True) as current_device:

                         route_lxml_element = current_device.rpc.get_forwarding_table_information(table=forwarding_table)
                         list_of_routes = route_lxml_element.findall('.//rt-entry')

                         for route in list_of_routes:
                              if route.findtext('nh/nh-type') in ('ucst', 'indr'):
                                   print('entry: {0} outgoing interface: {1}' .format(route.findtext('rt-destination').strip(), route.findtext('nh/via'.strip())))
               except ConnectError as err:
                    print('!!!!!!!!!! - thrown ConnectError exception: ' + str(err))
                    continue
          else:
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , skipping forwarding table lookup')

if __name__ == '__main__':
     main()
