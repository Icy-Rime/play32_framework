from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_sdcard import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_sdcard import *
else:
    def init():
        pass

    def mount():
        pass

    def umount():
        pass

    def format_fat():
        pass

    def format_lfs2():
        pass
