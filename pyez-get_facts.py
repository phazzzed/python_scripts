from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
import pprint
import yaml
import uname_pass
import os

def main():

     UID = uname_pass.username 
     PWD = uname_pass.password

     #previously using a text file. moved to YAML format
     #array_device_list = []
     #file_device_list = open('juniper_model_all.list, 'r')
     #for line in file_device_list:
     #     line = str(line.split(' ')
     #     array_device_list.append({'hostname':line[0],ip_address':str(line[1].strip()})
     #for i in range(len(array_device-list)):

     loaded_device_list = yaml.safe_load(open('inventory/juniper_model-all.yaml'))
     count_device_list = len(loaded_device_list['devices'])
     device_iterator = 1
     for loaded_device in loaded_device_list['devices']:
          print('********** - currently looping through device {0} : {1} of total {2} devices'.format(device_iterator, loaded_device['hostname'], count_device_list))
          try:
               with Device(host=loaded_device['ip'], password=PWD, user=UID, normalize=True) as current_device:
                    device_hostname =  str(current_device.facts['hostname']).lower()
                    print('********** - connected to ' + device_hostname)
                    print('********** - retrieving device facts from ' + device_hostname)
                    device_facts = current_device.facts
                    print('********** - finished retrieiving device facts from ' + device_hostname)
               
               print('********** - disconnected from ' + device_hostname)
          # make more specific exception
          except Exception as e:
               print ('thrown exception: ' + str(e))
               continue

          try:
               cwd = os.getcwd()
               output_dir = cwd + '/output_pyez_get_facts'
               if os.path.exists(output_dir) == False:
                    print('********** - creating directory: ' + output_dir)
                    os.makedirs(output_dir)
          except OSError as e:
               print('!!!!!!!!!! - error making diretory: ' + str(e))

          with open(output_dir + '/' + device_hostname, 'w') as f_out:
               print('********** - begun writing the rendered output to ' + output_dir + '/' + device_hostname)
               pprint.pprint(device_facts, f_out) 
               print('********** - finished writing the rendered output to ' + output_dir + '/' + device_hostname)
          print('********** - finished looping through device {0} : {1} of total {2} devices'.format(device_iterator, loaded_device['hostname'], count_device_list))
          device_iterator += 1

if __name__ == '__main__':
     main()
