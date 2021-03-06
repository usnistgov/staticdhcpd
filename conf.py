#Copy this file to one of the following locations, then rename it to conf.py:
#/etc/staticDHCPd/, ./conf/

#import databases.generic.Definition
from staticdhcpdlib.databases.generic import Definition
import requests
import json
import os
import sys

#For a full overview of what these parameters mean, and to further customise
#your system, please consult the configuration and scripting guides in the
#standard documentation


# Whether to daemonise on startup (you don't want this during initial setup)
DAEMON = False

#WARNING: The default UID and GID are those of root. THIS IS NOT GOOD!
#If testing, set them to your id, which you can find using `id` in a terminal.
#If going into production, if no standard exists in your environment, use the
#values of "nobody": `id nobody`
#The UID this server will use after initial setup
UID = 0
#The GID this server will use after initial setup
GID = 0

#The IP of the interface to use for DHCP traffic
#DHCP_SERVER_IP = '192.168.56.101'

PID_FILE='/var/run/staticdhcpd.pid'

# The host where this script is run
DHCP_SERVER_IP = os.environ.get("DHCP_SERVER_IP")

# LOCATION mud the MUD server lives. Change if needed.

if os.environ.get("MUD_CONTROLLER_HOST") is None or os.environ.get("MUD_CONTROLLER_PORT") is None:
    print "Please set MUD_CONTROLLER_HOST and MUD_CONTROLLER_PORT environment variables"
    sys.exit()
    os.exit()

MUD_CONTROLLER_HOST = os.environ.get("MUD_CONTROLLER_HOST") + ":" + os.environ.get("MUD_CONTROLLER_PORT")

#'10.0.0.3:8000'

# The SDN controller controls the flow rules on the switch. We assume 
# The DHCP server is configured with this information. CHANGE THIS IF NEEDED


mudServerUrlPrefix = "http://" + MUD_CONTROLLER_HOST + "/addMudProfile"

#The database-engine to use
#For details, see the configuration guide in the documentation.
DATABASE_ENGINE = 'INI'
INI_FILE='/etc/staticDHCPd/dhcp.ini'

AUTHORITATIVE=True

# List of available addresses. We initialize this once.

# address_list = [ "10.0.0." + str(k) for k in range(100,240)]

def handleUnknowMAC(packet, method,mac,client_ip,relay_ip,port):
    print "Handle Unknown MAC"
    return None

def makeDottedDecimal(address):
    retval = str(address[0]) 
    for i in range(1,len(address)):
        retval = retval + "." + str(address[i])
    return retval

def loadDHCPPacket(pkt, method, mac, definition, relay_ip, port, source_packet):

    print "method = ", method , " mac ", mac, "option ", pkt.getOption(161)

    if method.startswith("REQUEST:") and pkt.isOption(161):
        """
        DHCP Request processing with options 161.
        """
        options = pkt.getOption(161)
        mudUrl = ""
        # Convert the options into a string.
        for ch in options:
            mudUrl = mudUrl + chr(ch)

        # TODO -- verify the mudUrl (must be signed by manufacturer).
        print "mudURl ", mudUrl
        
        mudProfileInfo = {}

        mudProfileInfo["mud_url"] = mudUrl

        mudProfileInfo['dhcp_server_address'] = DHCP_SERVER_IP
        
        mudProfileInfo['router'] = makeDottedDecimal(pkt.getOption('router'))

        mudProfileInfo['domain_name_servers'] = makeDottedDecimal(pkt.getOption('domain_name_servers'))

        mudProfileInfo['subnet_mask'] = makeDottedDecimal(pkt.getOption('subnet_mask'))

        # MUD Server URL - add MAC to it so that the server can know the MAC id.

        mudServerUrl = mudServerUrlPrefix + "/" + str(mac)
            
        response = requests.post(mudServerUrl,data = json.dumps(mudProfileInfo))

        if response.status_code == 200 :
            responseJson = response.json()
            cacheValidity = responseJson['cache-validity']
            leaseTimeByteArray = pkt.getOption('ip_address_lease_time')
            # Options are presented as byte arrays. Consider it to be a base 256 number. 
            weights=[1<<24,1<<16,1<<8,1]
            leaseTime = sum([leaseTimeByteArray[i] * weights[i] for i in range(0,4)])
            print "leaseTime", leaseTime, "cacheValidity ", cacheValidity
            if leaseTime > cacheValidity / 2 :
                pkt.setOption('ip_address_lease_time',cacheValidity/2)
            pkt.setOption(161,"",False)
            return True
        else:
            return False

    else:
        return True
