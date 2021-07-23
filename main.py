# >>>> config memory <<<<
import gc
_threshold = (gc.mem_free() * 60) // 100 # 80% gc auto collect
gc.threshold(_threshold)
print("gc threshold has been set to", _threshold)
del _threshold
# >>>> main <<<<
from play32sys import app
app._on_boot_(True)
# app._on_boot_(True, "txt_reader")

# test below
# from play32sys import network_helper
# from play32sys import network_file_system
# wlan = network_helper.connect(True)
# print(wlan.ifconfig())
# network_helper.sync_time()
# network_file_system.mount(b'12345678', b'12345678', "192.168.31.37")

# f = open("/mnt/README.md", "a")
