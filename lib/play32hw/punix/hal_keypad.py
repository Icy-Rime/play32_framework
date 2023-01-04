from play32hw.punix.usdl2 import SDL_Init, SDL_INIT_EVENTS
from play32hw.punix.usdl2 import SDL_PollEvent, SDL_GetEventType, SDL_GetKeyboardState
from play32hw.punix.usdl2 import SDL_EVENT_QUIT
import usys

KEY_A = 0x00
KEY_B = 0x01
KEY_UP = 0x02
KEY_DOWN = 0x03
KEY_LEFT = 0x04
KEY_RIGHT = 0x05

EVENT_KEY_PRESS = 0x00
EVENT_KEY_RELEASE = 0x10

_SCAN_CODE_A = 4
_SCAN_CODE_D = 7
_SCAN_CODE_J = 13
_SCAN_CODE_K = 14
_SCAN_CODE_S = 22
_SCAN_CODE_W = 26

_KEY_MAP = {
    KEY_A: _SCAN_CODE_K,
    KEY_B: _SCAN_CODE_J,
    KEY_UP: _SCAN_CODE_W,
    KEY_DOWN: _SCAN_CODE_S,
    KEY_LEFT: _SCAN_CODE_A,
    KEY_RIGHT: _SCAN_CODE_D,
}

__event_buffer = bytearray(128)
__keypad = [_KEY_MAP[KEY_A], _KEY_MAP[KEY_B], _KEY_MAP[KEY_UP], _KEY_MAP[KEY_DOWN], _KEY_MAP[KEY_LEFT], _KEY_MAP[KEY_RIGHT]]
__key_status = [False, False, False, False, False, False]
__key_name = "ABUDLR"
__inited = False

def init():
    global __inited
    if __inited:
        return
    SDL_Init(SDL_INIT_EVENTS)
    __inited = True

def get_key_value(key):
    # type: (int) -> int
    return SDL_GetKeyboardState()[_KEY_MAP[key]]

def get_key_name(key):
    # type: (int) -> str
    return __key_name[key]

def get_key_event():
    # type: () -> list
    events = []
    while SDL_PollEvent(__event_buffer) == 1:
        sdl_event_type = SDL_GetEventType(__event_buffer)
        if sdl_event_type == SDL_EVENT_QUIT:
            from play32hw.punix.hal_screen import deinit
            deinit()
            usys.exit(0)
    for i in range(len(__keypad)):
        v = get_key_value(i)
        if __key_status[i] and v == 0:
            # release
            __key_status[i] = False
            # text = str(i) + " RELEASED"
            # print(text)
            events.append(EVENT_KEY_RELEASE | i)
        elif __key_status[i] == False and v > 0:
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
    # type: (int) -> bool
    return get_key_value(key) == 1

def clear_key_status(keys):
    for k in keys:
        __key_status[k] = False