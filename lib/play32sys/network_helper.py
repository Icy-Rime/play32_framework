import ntptime, network
from play32sys.sys_config import get_sys_config
ALIYUN_NTP_HOST = "ntp.aliyun.com"
ntptime.host = ALIYUN_NTP_HOST

def sync_time():
    try:
        ntptime.settime()
    except: pass

def connect(waiting=False):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ssid = get_sys_config('wifi_ssid')
    passwd = get_sys_config('wifi_pass')
    wlan.config(dhcp_hostname=get_sys_config("hostname", "play32"))
    print("hostname:", get_sys_config("hostname", "play32"))
    if ssid != None and passwd != None:
        if not wlan.isconnected():
            wlan.connect(ssid, passwd)
    while waiting and not wlan.isconnected():
        pass
    return wlan

def ap(ssid="Play32AP", passwd="12345678"):
    ap = network.WLAN(network.AP_IF)
    ap.config(dhcp_hostname="play32")
    ap.config(essid=ssid)
    ap.config(max_clients=16)
    ap.config(hidden=False)
    if passwd == None or passwd == "":
        ap.config(authmode=network.AUTH_OPEN)
    else:
        ap.config(password=passwd)
        ap.config(authmode=network.AUTH_WPA_WPA2_PSK)
    ap.active(True)
    return ap

def deactive_all():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
