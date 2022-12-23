from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_keypad import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_keypad import *
else:
    KEY_A = 0x00
    KEY_B = 0x01
    KEY_UP = 0x02
    KEY_DOWN = 0x03
    KEY_LEFT = 0x04
    KEY_RIGHT = 0x05

    EVENT_KEY_PRESS = 0x00
    EVENT_KEY_RELEASE = 0x10

    def init():
        pass

    def get_key_value(key):
        # type: (int) -> int
        return 0

    def get_key_name(key):
        return "K"

    def get_key_event():
        # type: () -> list
        return []

    def parse_key_event(event):
        # type: (int) -> tuple
        return (event & 0xF0, event & 0x0F)

    def is_key_pressed(key):
        return get_key_value(key) == 1

    def clear_key_status(keys):
        pass
