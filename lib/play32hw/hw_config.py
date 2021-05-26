import ujson
from play32sys import path
__p = path.join(path.get_data_path(), "hw_config.json")
with open(__p, "rb") as f:
    __json = ujson.load(f)

SCREEN_WIDTH = __json["screen_width"]
SCREEN_HEIGHT = __json["screen_height"]
SCREEN_DRIVER = __json["screen_driver"]
SCREEN_SCL = __json["pin_screen_scl"]
SCREEN_SDA_MOSI = __json["pin_screen_sda_mosi"]
SCREEN_CS = __json["pin_screen_cs"]
SCREEN_DC = __json["pin_screen_dc"]
SCREEN_RST = __json["pin_screen_rst"]
PIN_KEY_A = __json["pin_key_a"]
PIN_KEY_B = __json["pin_key_b"]
PIN_KEY_UP = __json["pin_key_up"]
PIN_KEY_DOWN = __json["pin_key_down"]
PIN_KEY_LEFT = __json["pin_key_left"]
PIN_KEY_RIGHT = __json["pin_key_right"]
PIN_BUZZ = __json["pin_buzz"]
PIN_LED = __json["pin_led"]
del __p, __json
