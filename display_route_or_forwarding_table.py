from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
import uname_pass
import sys

UID = uname_pass.username 
PWD = uname_pass.password

array_device_list = []

if len(sys.argv) > 2:
     option = sys.argv[1]
     if option == '-r':
          print('user chosen to view routing table')
     elif option == '-f':
          print('user chosen to view forwarding table')
     else:
          print('user has entered parameters incorrectly, exiting')
          exit()

     print('routing table selected: ' + str(sys.argv[2])) 
     client_table = sys.argv[2]
else:
     print('user has entered parameters incorrectly, exiting')  
     exit()

if((option == '-f') and (client_table=='inet.0')):
     client_table='default'
if((option == '-r') and (client_table!='inet.0')):
     client_table=client_table + '.inet.0'

file_device_list = open('juniper_model_routers.list', 'r')
for line in file_device_list:
     line = str(line).split(' ')
     array_device_list.append({'hostname':line[0], 'ip_address':str(line[1]).strip()})

for i in range(len(array_device_list)):
     try:
          with Device(host=array_device_list[i]['ip_address'], password=PWD, user=UID, normalize=True) as current_device:
               current_hostname = current_device.facts['hostname']
               print(f'********** - connected to {current_hostname} - **********')
               if option == '-r':
                    raw_xml_output = current_device.rpc.get_route_information(table=client_table)
                    filtered_entries = raw_xml_output.findall('.//rt')
               elif option =='-f':
                    raw_xml_output = current_device.rpc.get_forwarding_table_information(table=client_table,family='inet')
                    filtered_entries = raw_xml_output.findall('.//rt-entry')
               else:
                    print('this should never occur')
                    exit()
          
          #iterate through the list
          for entry in filtered_entries:
               if((entry.findtext('rt-entry/protocol-name') != 'Local') and (option == '-r')):
                    dest = entry.findtext('rt-destination')
                    via = entry.findtext('rt-entry/nh/via')
                    print(f"{dest} via {via}")

               if ((entry.findtext('nh/nh-type') in ('ucst', 'indr')) and (option == '-f')):
                     dest = entry.findtext('rt-destination')
                     via = entry.findtext('nh/via')
                     print(f"{dest} via {via}")
                          
          print(f'********** - exited from {current_hostname} - **********')
     except Exception as e:
          print ('thrown exception: ' + str(e))
          continue
