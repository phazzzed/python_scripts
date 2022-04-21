from operator import truediv
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from pprint import pprint
from lxml import etree
import sys
import uname_pass 


def ingressLSR(label_lsr_list):
    UID = uname_pass.username 
    PWD = uname_pass.password 

    ip_ingressLSR = sys.argv[1]
    destination_L3VPN = sys.argv[2] 
    destination_subnet = sys.argv[3]

    log_file = open('log_ingressLSR.txt', 'w')

    protocol_next_hop_filter = 'route-table/rt/rt-entry/protocol-nh/to'

    with Device(host=ip_ingressLSR, password=PWD, user=UID, normalize=True) as dev_ingressLSR:

        print('ingressLSR() - succesfully connected to: ' + str(ip_ingressLSR))

        # consult the L3VPN table for the destination subnet
        # get the active path of the egress LSR
        xmloutRIBVPN = dev_ingressLSR.rpc.get_route_information(table=destination_L3VPN,destination=destination_subnet, extensive=True,exact=True)
        log_file.write('raw xml data returned - \n' + etree.tostring(xmloutRIBVPN, encoding='unicode', pretty_print=True))
        ip_egressLSR = str(xmloutRIBVPN.findtext(protocol_next_hop_filter)).strip()
        print('ingressLSR() - egress LSR of LSP detected: ' +  str(ip_egressLSR))

        # get the transport label to reach the egress LSR & loopback of the next router along the LSP
        # we could get interface address but an ACL may block it so good practice to use lo0
        # we are expecting 1 entry
        xmloutput_LDP = dev_ingressLSR.rpc.get_ldp_path_information(destination=ip_egressLSR)

    ip_nextLSR = xmloutput_LDP.findtext('ldp-path/ldp-inlib-session').strip()
    ip_nextLSR = str(ip_nextLSR).split(':')

    label_toReachNextLSR = xmloutput_LDP.findtext('ldp-path/ldp-inlib-label').strip()
    print('ingressLSR() - transport label {0} to reach {1} which is the next LSR along this LSP'.format(label_toReachNextLSR, ip_nextLSR[0]))

    ingress_dict = {"next_LSR_IP" : ip_nextLSR[0], "label" : label_toReachNextLSR}

    label_lsr_list.append(ingress_dict)

    print(label_lsr_list)

    return ip_egressLSR
    
# this function is only invoked on the transit LSR
# this is recursive so this should be looped through while within the transit LSR
def transitLSR(ip_egressLSR, label_lsr_list):
     UID = uname_pass.username 
     PWD = uname_pass.password 

     ip_currentLSR = label_lsr_list[-1]['next_LSR_IP']
     
     with Device(host=ip_currentLSR, password=PWD, user=UID, normalize=True) as dev_currentLSR:
     
        print('transitLSR() - succesfully connected to: ' + str(ip_currentLSR))
        # get the transport label to reach the egress LSR & loopback of the next router along the LSP
        # we could get interface address but an ACL may block it so good practice to use lo0
        # we are expecting 1 entry
        xmlOutputLDP = dev_currentLSR.rpc.get_ldp_path_information(destination=ip_egressLSR)
        
     ip_nextLSR = xmlOutputLDP.findtext('ldp-path/ldp-inlib-session').strip()
     ip_nextLSR = str(ip_nextLSR).split(':')

     label_toReachNextLSR = xmlOutputLDP.findtext('ldp-path/ldp-inlib-label').strip()
            
     print('transitLSR() - transport label: {0} to reach {1} which is the next LSR along this  LSP'.format(label_toReachNextLSR, ip_nextLSR[0]))
     print('transitLSR() - successfully disconnected from: ' + str(ip_currentLSR))

     ingress_dict = {"next_LSR_IP" : ip_nextLSR[0], "label" : label_toReachNextLSR}

     label_lsr_list.append(ingress_dict)

     print(label_lsr_list)
     
     # php is enabled so if we are going to forward a label of 3, break out to main function 
     if label_toReachNextLSR == '3':
         print('transitLSR() - as label is ' + str(label_toReachNextLSR) + ' so ' + str(ip_nextLSR[0]) + ' is the last hop. recursion stopped and falling back to main')
         return
     else:
        print('transitLSR() - as label is ' + str(label_toReachNextLSR) + '. continuing recursive loop')
        transitLSR(ip_egressLSR, label_lsr_list)

    
def egressLSR(ip_egressLSR):
    UID = uname_pass.username 
    PWD = uname_pass.password 

    destination_L3VPN = sys.argv[2] 
    destination_subnet = sys.argv[3]

    with Device(host=ip_egressLSR, password=PWD, user=UID, normalize=True) as dev_egressLSR:

        print('egressLSR() - succesfully connected to: ' + str(ip_egressLSR))
        xml_output_L3VPN_FIB = dev_egressLSR.rpc.get_forwarding_table_information(vpn=destination_L3VPN)

    list_of_FIB_entries = xml_output_L3VPN_FIB.findall('.//rt-entry')
    for fib_entry in list_of_FIB_entries:
        if fib_entry.findtext('rt-destination') in str(destination_subnet):
            print('egressLSR() - entry: {0} outgoing interface: {1}' .format(fib_entry.findtext('rt-destination').strip(), fib_entry.findtext('nh/via'.strip())))

    print('egressLSR() - successfully disconnected from: ' + str(ip_egressLSR))

def main():
    UID = uname_pass.username 
    PWD = uname_pass.password 

    ip_ingressLSR = sys.argv[1]
    destination_L3VPN = sys.argv[2] 
    destination_subnet = sys.argv[3]

    label_lsr_list = []

    print('main() - L3VPN selected: ' + str(destination_L3VPN))
    print('main() - Subnet selected: ' + str(destination_subnet))

    ip_egressLSR = ingressLSR(label_lsr_list)

    label_toReachNextLSR = label_lsr_list[-1]['label']
    ip_nextLSR = label_lsr_list[-1]['next_LSR_IP']
    
    if label_toReachNextLSR != '3':
        print('main() - detected label ' + str(label_toReachNextLSR) + ' - entering transitLSR function')
        transitLSR(ip_egressLSR, label_lsr_list)
    else:
        print('main() - detected label 3 so ' + str(ip_nextLSR) + ' is the egress LSR. not entering recursive TransitLSR function')

    egressLSR(ip_egressLSR)


if __name__ == "__main__":
    main()

