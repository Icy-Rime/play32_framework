# >>>> config memory <<<<
import gc
gc.collect()
_threshold = (gc.mem_free() * 80) // 100 # 80% gc auto collect
gc.threshold(_threshold)
print("gc threshold has been set to", _threshold)
del _threshold

# >>>> init <<<<
import hal_screen, hal_keypad, hal_buzz, hal_led
hal_screen.init()
hal_keypad.init()
hal_buzz.init()
hal_led.init()

# >>>> main <<<<
from play32sys import app
app._on_boot_(True)

# test below
# from play32sys import network_helper, network_file_system
# network_helper.connect(True)
# network_helper.sync_time()
# network_file_system.mount(b'12345678', b'12345678', "192.168.31.37")

# f = open("/mnt/README.md", "a")
