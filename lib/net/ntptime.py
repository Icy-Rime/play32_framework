try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
from play32hw.hw_config import get_model, MODEL_UNIX

# mpy: (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
# unix: (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 2208988800 if get_model() == MODEL_UNIX else 3155673600

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
# host = "pool.ntp.org"
host = "ntp.aliyun.com"


def time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA


# There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
def settime():
    t = time()
    import machine
    import utime

    tm = utime.gmtime(t)
    try:
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    except: pass
