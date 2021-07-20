from play32sys import path
import hal_battery
BATTERY_RECORD_PATH = path.join(path.get_data_path(), "battery.dat")

__battery_level = []

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

def get_battery_level():
    try:
        if len(__battery_level) <= 0:
            load_battery_level()
        value = hal_battery.get_raw_battery_value()
        btl = len(__battery_level)
        for i in range(btl):
            if __battery_level[i] > value:
                return i * 100 // btl
        return 100
    except:
        return -1
