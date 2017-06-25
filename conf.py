#Copy this file to one of the following locations, then rename it to conf.py:
#/etc/staticDHCPd/, ./conf/

#import databases.generic.Definition
from staticdhcpdlib.databases.generic import Definition
import requests
import json

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
DHCP_SERVER_IP = '10.0.0.1'

MUD_CONTROLLER_HOST = '10.0.0.3'

MUD_PROFILE_SERVER_HOST = '10.0.0.4'

#The database-engine to use
#For details, see the configuration guide in the documentation.
DATABASE_ENGINE = 'INI'
INI_FILE='/home/mininet/dhcp.ini'

AUTHORITATIVE=True

# List of available addresses. We initialize this once.

# address_list = [ "10.0.0." + str(k) for k in range(100,240)]

def handleUnknowMAC(packet, method,mac,client_ip,relay_ip,port):
    print "Handle Unknown MAC"
    return None

def loadDHCPPacket(pkt, method, mac, definition, relay_ip, port, source_packet):
    """
    if not definition.ip[3] % 3: #The client's IP's fourth octet is a multiple of 3
        packet.setOption('renewal_time_value', 60)
    elif method.startswith('REQUEST:') and random.random() < 0.5:
        packet.transformToDHCPNakPacket()
    elif random.random() < 0.1:
        return False
    """

    print "method = ", method , " mac ", mac, "option ", pkt.getOption(161)

    if method.startswith("REQUEST:") and pkt.isOption(161):
        """
        DHCP Request processing with options 161.
        """
        options = pkt.getOptions(161)
        mudUri = ""
        # Convert the options into a string.
        for ch in options:
            mudUri = mudInfo + chr(ch)
        print "mudURI ", mudUri
        # TODO...
        # A DHCP server that does process the MUD URL MUST
        # adhere to the process specified in [RFC2818] and [RFC5280] to
        # validate the TLS certificate of the web server hosting the MUD file.
        requestInfo = {}
        requestInfo['mac'] = mac
        r  = requests.get(mudUri,data=requestInfo)
        
        if r.status_code == 200:
            mudProfile = r.json()
            print "mudProfile = ", json.dumps(mudProfile)
            print "TODO -- send the json to our MUD controller here "
            
            pkt.setOption(161,"",False)
            return True
        else:
            return False
        
        

    return True
