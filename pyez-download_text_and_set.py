from jnpr.junos import Device
from jnpr.junos.exception import *
import uname_pass
from lxml import etree 
import yaml
import os

def inventory(filename):
     devices = yaml.safe_load(open(filename))
     return devices

def main(devices):

     UID = uname_pass.username
     PWD = uname_pass.password

     #array_device_list = []
     formats = ['text', 'set']
      
     #moved from a text input file to YAML
     #file_device_list = open('juniper_model_all.list', 'r')
     #for line in file_device_list:
     #     line = str(line).split(' ')
     #     array_device_list.append({'hostname':line[0], 'ip_address':str(line[1]).strip()})

     for each_device in devices['devices']:
          try:
               with Device(each_device['ip'], password=PWD, user=UID,gather_facts=False) as current_device:
                    current_hostname = current_device.facts['hostname']
                    print(f'********** - connected to ' + current_hostname + ' - ' +  each_device['hostname'] + ' - **********')

                    for format_entry in formats:
                         returned_text = current_device.rpc.get_config(options={'format':format_entry})

                         try:
                              cwd = os.getcwd()
                              output_folder = cwd + '/output_pyez_download_text_and_set/' + str(format_entry)
                              if os.path.exists(output_folder) == False:
                                   print('########## - creating the folder directory ' + output_folder + ' - ##########')
                                   os.makedirs(output_folder)
                         except OSError as e:
                              print('!!!!!!!!!! - error making direcotry: ' + str(e) + ' - !!!!!!!!!!')

                         output_file = output_folder + '/' + str(current_hostname).lower() + '.' + str(format_entry)

                         with open(output_file, 'w') as w:
                               w.write(etree.tostring(returned_text).decode('utf-8'))

               print(f'********** - exited from ' + current_hostname + ' - ' + each_device['hostname'] + ' - **********')
          except Exception as e:
               print('&&&&&&&&&& - caught exception: ' + str(e) + ' - &&&&&&&&&&')
               continue 

if __name__ == '__main__':
     
     device_list = 'inventory/juniper_model-all.yaml'
     devices = inventory(device_list)
     main(devices)     
