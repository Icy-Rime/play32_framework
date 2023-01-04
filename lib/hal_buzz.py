from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_UNIX, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_buzz import *
elif get_model() == MODEL_UNIX:
    from play32hw.punix.hal_buzz import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_buzz import *
else:
    from play32hw.buzz_note_sound import DummyBuzzPlayer
    def init():
        pass

    def get_buzz_player():
        return DummyBuzzPlayer(0, 0)
