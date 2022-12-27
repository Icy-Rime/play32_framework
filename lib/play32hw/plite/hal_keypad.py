
from machine import Pin
from play32hw.plite.button import Button, EVENT_CLICK, EVENT_LONG_PRESS

PIN_KEY = 9

KEY_A = 0x00
KEY_B = 0x01
KEY_UP = 0x02
KEY_DOWN = 0x03
KEY_LEFT = 0x04
KEY_RIGHT = 0x05

EVENT_KEY_PRESS = 0x00
EVENT_KEY_RELEASE = 0x10

__key_button = Button(PIN_KEY, True, True)
__key_name = "ABUDLR"

def init():
    # type: () -> None
    global __key_button
    __key_button = Button(PIN_KEY, True, True)

def get_key_value(key):
    # type: (int) -> int
    return 1

def get_key_name(key):
    return __key_name[key]

def get_key_event():
    # type: () -> list
    events = []
    evt, count = __key_button.scan()
    if evt == EVENT_LONG_PRESS:
        if count == 1:
            events.append(EVENT_KEY_PRESS | KEY_A)
            events.append(EVENT_KEY_RELEASE | KEY_A)
        elif count == 2:
            events.append(EVENT_KEY_PRESS | KEY_B)
            events.append(EVENT_KEY_RELEASE | KEY_B)
    elif evt == EVENT_CLICK:
        key = -1
        if count == 1:
            key = KEY_RIGHT
        elif count == 2:
            key = KEY_LEFT
        elif count == 3:
            key = KEY_DOWN
        elif count == 4:
            key = KEY_UP
        if key >= 0:
            events.append(EVENT_KEY_PRESS | key)
            events.append(EVENT_KEY_RELEASE | key)
    return events

def parse_key_event(event):
    # type: (int) -> tuple
    return (event & 0xF0, event & 0x0F)

def is_key_pressed(key):
    return get_key_value(key) == 0

def clear_key_status(keys):
    pass
