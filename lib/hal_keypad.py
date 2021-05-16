
from machine import Pin
from play32hw.hw_config import PIN_KEY_A, PIN_KEY_B, PIN_KEY_UP, PIN_KEY_DOWN, PIN_KEY_LEFT, PIN_KEY_RIGHT

KEY_A = 0x00
KEY_B = 0x01
KEY_UP = 0x02
KEY_DOWN = 0x03
KEY_LEFT = 0x04
KEY_RIGHT = 0x05

EVENT_KEY_PRESS = 0x00
EVENT_KEY_RELEASE = 0x10

__keypad = None
__key_status = [False, False, False, False, False, False]
__key_name = "ABUDLR"

def init():
    # type: () -> None
    global __keypad
    if __keypad != None:
        return
    t_a = Pin(PIN_KEY_A, Pin.IN, Pin.PULL_UP)
    t_b = Pin(PIN_KEY_B, Pin.IN, Pin.PULL_UP)
    t_up = Pin(PIN_KEY_UP, Pin.IN, Pin.PULL_UP)
    t_dn = Pin(PIN_KEY_DOWN, Pin.IN, Pin.PULL_UP)
    t_lt = Pin(PIN_KEY_LEFT, Pin.IN, Pin.PULL_UP)
    t_rt = Pin(PIN_KEY_RIGHT, Pin.IN, Pin.PULL_UP)
    __keypad = (t_a, t_b, t_up, t_dn, t_lt, t_rt)

def get_key_value(key):
    # type: (int) -> int
    return __keypad[key].value()

def get_key_name(key):
    return __key_name[key]

def get_key_event():
    # type: () -> list
    events = []
    for i in range(len(__keypad)):
        v = get_key_value(i)
        if __key_status[i] and v > 0:
            # release
            __key_status[i] = False
            # text = str(i) + " RELEASED"
            # print(text)
            events.append(EVENT_KEY_RELEASE | i)
        elif __key_status[i] == False and v == 0:
            # press
            __key_status[i] = True
            # text = str(i) + " PRESSED"
            # print(text)
            events.append(EVENT_KEY_PRESS | i)
        # keep
    return events

def parse_key_event(event):
    # type: (int) -> tuple
    return (event & 0xF0, event & 0x0F)

def is_key_pressed(key):
    return get_key_value(key) == 0