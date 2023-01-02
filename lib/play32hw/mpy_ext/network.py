MODE_11B = 1
MODE_11G = 2
MODE_11N = 4
STA_IF = 0
AP_IF = 1
AUTH_OPEN = 0
AUTH_WEP = 1
AUTH_WPA_PSK = 2
AUTH_WPA2_PSK = 3
AUTH_WPA_WPA2_PSK = 4
AUTH_WPA2_ENTERPRISE = 5
AUTH_MAX = 8
PHY_LAN8720 = 0
PHY_TLK110 = 1
PHY_IP101 = 2
STAT_BEACON_TIMEOUT = 200
STAT_NO_AP_FOUND = 201
STAT_WRONG_PASSWORD = 202
STAT_ASSOC_FAIL = 203
STAT_HANDSHAKE_TIMEOUT = 204
STAT_IDLE = 1000
STAT_CONNECTING = 1001
STAT_GOT_IP = 1010

class AbstractNIC():
    def __init__(self, id=None, *argv, **kws):
        pass
    def active(self, is_active=None):
        if is_active == None:
            return True
    def connect(self, ssid=None, passwd=None, *,bssid=None):
        pass
    def disconnect(self):
        pass
    def isconnected(self):
        return True
    def scan(self):
        return []
    def status(self, param):
        if param == 'rssi':
            return -62
        elif param == 'stations':
            return [(b'\x00\x00\x00\x00\x00\x00',), (b'"%N\xba\xe4\xd3',), (b'\xe0\x1f\x88\xf6y\xe4',)]
        return STAT_GOT_IP
    def ifconfig(self, config=None):
        if config == None:
            return ('192.168.4.199', '255.255.255.0', '192.168.4.1', '8.8.8.8')
    def config(self, param=None, *argv, **kws):
        if param != None:
            return 0

WLAN = AbstractNIC

def phy_mode(mode=None):
    if mode == None:
        return MODE_11N | MODE_11G | MODE_11B