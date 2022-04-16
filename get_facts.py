from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint

UID = 'eng'
PWD = 'cmn123!'

acx = ['10.126.128.4', '10.126.128.5', '10.126.144.4', '10.126.144.5']
mx = [ '10.126.128.1', '10.126.128.2', '10.126.144.1', '10.126.144.2']

for current_device in mx:
     current_router = Device(host=current_device, password=PWD, user=UID, normalize=True)

     try:
          current_router.open()
     except ConnectError as err:
          print("cannot connect to device: {0}" .format(err))
          continue

     pprint('facts about ' + str(current_router.facts['hostname']) + ' are: ' + str(current_router.facts))
     current_router.close()
     pprint('closed connection to: ' + str(current_router.facts['hostname']))

