from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys
import uname_pass

router_ip = sys.argv[1]
UID = uname_pass.username 
PWD = uname_pass.password 

command = "set system host-name TEST123"

current_router = Device(host=router_ip, password=PWD, user=UID, normalize=True)

current_router.open()

candidate = Config(current_router, mode='private')
candidate.lock()
candidate.load(command, format="set" )
candidate.diff()
if candidate.commit_check():
     candidate.commit()
else:
     candidate.rollback()

candidate.unlock()
current_router.close()

