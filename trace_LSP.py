from random import vonmisesvariate
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
from lxml import etree
import sys
import ipaddress

# this function is only invoked on the transit LSR
# this is recursive so this should be looped through while within the transit LSR
def transitLSR(v_egressLSR, v_currentLSR):
     UID = 'eng'
     PWD = 'cmn123!'
     
     #print('transitLSR() - attempting to connect to: ' + str(v_currentLSR))
     current_router = Device(host=v_currentLSR, password=PWD, user=UID, normalize=True)
     
     try:
          current_router.open()
     except jnpr.junos.exception.ConnectError as err:
          print('cannot conncet to device: ' + repr(err))
          exit()

     print('transitLSR() - succesfully connected to: ' + str(v_currentLSR))
     # get the transport label to reach the egress LSR & loopback of the next router along the LSP
     # we could get interface address but an ACL may block it so good practice to use lo0
     # we are expecting 1 entry
     v_ldp_xml_output = current_router.rpc.get_ldp_path_information(destination=v_egressLSR)
     v_nextLSR = v_ldp_xml_output.findtext('ldp-path/ldp-inlib-session').strip()
     v_nextLSR = str(v_nextLSR).split(':')

     v_outerLabel = v_ldp_xml_output.findtext('ldp-path/ldp-inlib-label').strip()
               
     print('transitLSR() - outer label: {0}, IP of the next LSR along our LSP: {1}'.format(v_outerLabel, v_nextLSR[0]))

     current_router.close()
     print('transitLSR() - successfully disconnected from: ' +str(v_currentLSR))
     
     # php is enabled so if we are going to forward a label of 3, break out to main function 
     if v_outerLabel != str('3'):
          print('transitLSR() - as label is ' + str(v_outerLabel) + '. continuing recursive loop')
          transitLSR(v_egressLSR, v_nextLSR[0])
     else:
          print('transitLSR() - as label is ' + str(v_outerLabel) + ' so ' + str(v_nextLSR[0]) + ' is the last hop. recursion stopped and falling back to main')
          return
    

UID = 'eng'
PWD = 'cmn123!'

v_ip_ingressLSR = sys.argv[1]
L3VPN = sys.argv[2] 
destination_subnet = sys.argv[3]

print('main() - L3VPN selected: ' + str(L3VPN))
print('main() - Subnet selected: ' + str(destination_subnet))

v_dev_ingressLSR = Device(host=v_ip_ingressLSR, password=PWD, user=UID, normalize=True)

try:
     v_dev_ingressLSR.open()
except jnpr.junos.exception.ConnectError as err:
     print('cannot connect to device: ' + repr(err))

print('main() - succesfully connected to: ' + str(v_ip_ingressLSR))
#ingressLSR_hname = str(v_dev_ingressLSR.facts(['hostname']))
#print('Connected to: ' + str(ingressLSR_hname))

# we only want to return the active-path
v_route_lxml_output = v_dev_ingressLSR.rpc.get_route_information(table=L3VPN,destination=destination_subnet,extensive=True,exact=True)
v_ip_egressLSR = v_route_lxml_output.findtext('route-table/rt/rt-entry/protocol-nh/to').strip()

# get protocol next hop value, expecting Loopback0 of egressLSR
print('main() - egress LSR of LSP detected: {0}' .format(v_ip_egressLSR))

# get the transport label to reach the egress LSR & loopback of the next router along the LSP
# we could get interface address but an ACL may block it so good practice to use lo0
# we are expecting 1 entry
v_ldp_xml_output = v_dev_ingressLSR.rpc.get_ldp_path_information(destination=v_ip_egressLSR)
v_nextLSR = v_ldp_xml_output.findtext('ldp-path/ldp-inlib-session').strip()
v_nextLSR = str(v_nextLSR).split(':')

v_outerLabel = v_ldp_xml_output.findtext('ldp-path/ldp-inlib-label').strip()
print('main() - outer label: {0}, IP of Next LSR along LSP: {1}'.format(v_outerLabel, v_nextLSR[0]))

v_dev_ingressLSR.close()

print('main() - successfully disconnected from: ' +str(v_ip_ingressLSR))

# recursive function, will loop through until router which does PHP 
if v_outerLabel != str('3'):
     print('main() - detected label ' + str(v_outerLabel) + ' - entering transitLSR function')
     transitLSR(v_ip_egressLSR, v_nextLSR[0])
else:
     print('main() - detected label 3 so ' + str(v_nextLSR[0]) + ' is the last hop. not entering recursive TransitLSR function')

v_dev_egressLSR = Device(host=v_ip_egressLSR, password=PWD, user=UID, normalize=True)

try:
     v_dev_egressLSR.open()
except jnpr.junos.exception.ConnectError as err:
     print('cannot connect to device: ' + repr(err))
     quit()

print('main() - succesfully connected to: ' + str(v_ip_egressLSR))
v_forwarding_lxml_element = v_dev_egressLSR.rpc.get_forwarding_table_information(vpn=L3VPN)
list_of_f_entries = v_forwarding_lxml_element.findall('.//rt-entry')


for route in list_of_f_entries:
     if route.findtext('rt-destination') in str(destination_subnet):
          print('main() - entry: {0} outgoing interface: {1}' .format(route.findtext('rt-destination').strip(), route.findtext('nh/via'.strip())))

v_dev_egressLSR.close()
print('main() - successfully disconnected from: ' + str(v_ip_egressLSR))

