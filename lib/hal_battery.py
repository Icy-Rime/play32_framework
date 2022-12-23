from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_battery import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_battery import *
else:
    def init():
        pass

    def get_raw_battery_value():
        return 0
