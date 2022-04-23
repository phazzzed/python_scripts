from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError
import uname_pass
from pprint import pprint

def main():

     UID = uname_pass.username
     PWD = uname_pass.password

     array_device_list = []

     file_device_list = open('juniper_model_all.list', 'r')
     for line in file_device_list:
          line = str(line).split(' ')
          array_device_list.append({'hostname':line[0],'ip_address':str(line[1]).strip()})

     for i in range(len(array_device_list)):
          try:
               with Device(host = array_device_list[i]['ip_address'], password=PWD, user=UID, normalize=True) as current_device:
                    current_hostname = current_device.facts['hostname']
                    print(f'********** - connected to {current_hostname} - **********')
                     
                    cu = Config(current_device)

                    rescue = cu.rescue(action='get', format='text')
                    if rescue is None:
                         print('No existing rescue configuration.')
                         print('Saving rescue configuration.')
                         cu.rescue(action='save')
                    else:
                         print('Rescue configuration found:')
                         pprint(rescue) 
               print(f'********** - exited from {current_hostname} - **********')
          except Exception as err:
               print (err)

if __name__ == '__main__':
     main()
