from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_screen import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_screen import *
else:
    def init():
        pass

    def get_size():
        return 0, 0

    def get_format():
        return 0

    def get_framebuffer():
        return None

    def refresh(x=0, y=0, w=0, h=0):
        pass
