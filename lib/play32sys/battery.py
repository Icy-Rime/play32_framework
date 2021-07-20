from play32sys import path
import hal_battery
BATTERY_RECORD_PATH = path.join(path.get_data_path(), "battery.dat")
DEFAULT_BATTERY_CACHE_SIZE = 1024

__battery_level = []
__last_log = []

def load_battery_level():
    global __battery_level
    __battery_level = []
    with open(BATTERY_RECORD_PATH, "rb") as f:
        while True:
            data = f.read(2)
            if len(data) <= 0:
                break
            __battery_level.append(int.from_bytes(data, "big"))
    __battery_level.sort() # from small to big

def init_battery_value_cache(size=DEFAULT_BATTERY_CACHE_SIZE):
    __last_log.clear()
    for _ in range(size):
        __last_log.append(hal_battery.get_raw_battery_value())

def measure():
    __last_log.append(hal_battery.get_raw_battery_value())
    __last_log.pop(0)

def get_battery_level():
    try:
        if len(__battery_level) <= 0:
            load_battery_level()
        if len(__last_log) <= 0:
            init_battery_value_cache()
        measure()
        value = sum(__last_log) // len(__last_log)
        btl = len(__battery_level)
        for i in range(btl):
            if __battery_level[i] > value:
                return i * 100 // btl
        return 100
    except:
        return -1
