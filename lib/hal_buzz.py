from play32hw.buzz_note_sound import BuzzPlayer
from play32hw.hw_config import PIN_BUZZ
__buzz = None

def init():
    global __buzz
    if __buzz != None:
        return
    __buzz = BuzzPlayer(PIN_BUZZ, 0)

def get_buzz_player():
    return __buzz
