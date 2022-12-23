from play32hw.buzz_note_sound import BuzzPlayer

PIN_BUZZ = 5

__buzz = None

def init():
    global __buzz
    if __buzz != None:
        return
    __buzz = BuzzPlayer(PIN_BUZZ, 0)

def get_buzz_player():
    return __buzz
