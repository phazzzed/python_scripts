from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
import uname_pass
import sys
import yaml
import os

def main():

     UID = uname_pass.username 
     PWD = uname_pass.password

     if len(sys.argv) == 3:
          option = sys.argv[1]
          if option == '-r':
               print('@@@@@@@@@@ - user chosen to get the inet routing table')
          elif option == '-f':
               print('@@@@@@@@@@ - user chosen to get the inet forwarding table')
          else:
               print('!!!!!!!!!! - exiting, user has entered neither -r or -f')
               print('!!!!!!!!!! - please use: ' + os.path.basename(__file__) + ' -r/-f <table name>')
               exit()

          print('@@@@@@@@@@ - user has chosen the following routing table: ' + str(sys.argv[2])) 
          client_table = sys.argv[2]
     else:
          print('!!!!!!!!!! - exiting, wrong number of parameters have been entered')
          print('!!!!!!!!!! - please use: ' + os.path.basename(__file__) + ' -r/-f <table name>')
          exit()

     if((option == '-f') and (client_table=='inet.0')):
          client_table='default'
     if((option == '-r') and (client_table!='inet.0')):
          client_table=client_table + '.inet.0'

     loaded_device_list = yaml.safe_load(open('inventory/juniper_model-all.yaml'))
     for loaded_device in loaded_device_list['devices']:
          if loaded_device['type'] == 'router':
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , will perform a lookup')
               try:
                    with Device(host=loaded_device['ip'], password=PWD, user=UID, normalize=True) as current_device:
                         current_hostname = current_device.facts['hostname']
                         print('********** - connected to {0}'.format(current_hostname))
                        
                         # if the user chose to get the routing table, call the RPC to get the routing table 
                         if option == '-r':
                              print('********** - sending rpc to get route table from {0}'.format(current_hostname))
                              raw_xml_output = current_device.rpc.get_route_information(table=client_table)
                              filtered_entries = raw_xml_output.findall('.//rt')
                         # if the user chose to get the forwarding table, call the RPC to get the forwarding table
                         elif option =='-f':
                              print('********** - sending rpc to get forwrding table from {0}'.format(current_hostname))
                              raw_xml_output = current_device.rpc.get_forwarding_table_information(table=client_table,family='inet')
                              filtered_entries = raw_xml_output.findall('.//rt-entry')
                         else:
                              print('!!!!!!!!!! - this should never occur')
                              exit()
               except ConnectError as err:
                     print('!!!!!!!!!! - thrown ConnectError exception: ' + str(err))
                     continue
               print('********** - disconnected from {0}'.format(current_hostname)) 

               #iterate through the list
               for entry in filtered_entries:
                    #filter through the output when the user chose to receive the routing table
                    if((entry.findtext('rt-entry/protocol-name') != 'Local') and (option == '-r')):
                         dest = entry.findtext('rt-destination')
                         via = entry.findtext('rt-entry/nh/via')
                         print(f"{dest} via {via}")
                    
                    #filter through the output when the user chose to receive the forwarding table
                    if ((entry.findtext('nh/nh-type') in ('ucst', 'indr')) and (option == '-f')):
                         dest = entry.findtext('rt-destination')
                         via = entry.findtext('nh/via')
                         print(f"{dest} via {via}")
                          
          else:
               print('********** - ' + loaded_device['hostname'] + ' is the type ' + loaded_device['type'] + ' , skipping table lookup')

if __name__ == '__main__':
     main()
