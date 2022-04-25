import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError
import uname_pass
from pprint import pprint

def main():

     UID = uname_pass.username
     PWD = uname_pass.password

     #previously using a text file, moved to YAML format
     #array_device_list = []
     #file_device_list = open('juniper_model_all.list', 'r')
     #for line in file_device_list:
     #     line = str(line).split(' ')
     #     array_device_list.append({'hostname':line[0],'ip_address':str(line[1]).strip()})
     #for i in range(len(array_device_list)):A

     loaded_device_list = yaml.safe_load(open('inventory/juniper_model-all.yaml'))
     for loaded_device in loaded_device_list['devices']:
          try:
               with Device(host = loaded_device['ip'], password=PWD, user=UID, normalize=True) as current_device:
                    device_hostname = current_device.facts['hostname']
                    print('********** - connected to {0} - **********', device_hostname)
                     
                    with Config(current_device) as cu:
                         rescue = cu.rescue(action='get', format='text')
                         if rescue is None:
                              print('********** - no existing rescue configuration on {0}, skipping over device'.format(device_hostname))
                              continue
                         else:
                              print('********** - rescue configuration found on {0}, deleting now'.format(device_hostname))
                              cu.rescue(action='delete')
               print('********** - exited from {0} - **********'.format(device_hostname))
          except ConnectError as err:
               print ('!!!!!!!!!! - thrown ConnectError exception: ' + str(err))

if __name__ == '__main__':
     main()
