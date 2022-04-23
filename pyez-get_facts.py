from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
import uname_pass

UID = uname_pass.username 
PWD = uname_pass.password

array_device_list = []

file_device_list = open('juniper_model_all.list', 'r')
for line in file_device_list:
     line = str(line).split(' ')
     array_device_list.append({'hostname':line[0], 'ip_address':str(line[1]).strip()})

for i in range(len(array_device_list)):
     try:
          with Device(host=array_device_list[i]['ip_address'], password=PWD, user=UID, normalize=True) as current_device:
               pprint('main() - facts about ' + str(current_device.facts['hostname']) + ' are:\n')
               pprint(current_device.facts)
     except Exception as e:
          print ('thrown exception: ' + str(e))
          continue
