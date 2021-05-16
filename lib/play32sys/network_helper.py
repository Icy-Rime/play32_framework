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
    if not wlan.isconnected():
        wlan.connect(get_sys_config('wifi_ssid'), get_sys_config('wifi_pass'))
        while waiting and not wlan.isconnected():
            pass
    return wlan
