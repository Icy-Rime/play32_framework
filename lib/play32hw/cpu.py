from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_LITE, MODEL_UNIX, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.hesp32.cpu import *
elif get_model() == MODEL_LITE:
    from play32hw.hesp32c3.cpu import *
elif get_model() == MODEL_UNIX:
    from play32hw.hunix.cpu import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.hemu.cpu import *
else:
    from utime import sleep_ms
    from play32hw.hw_config import ResetException

    VERY_SLOW = 40_000_000
    SLOW = 80_000_000
    MIDDLE = 160_000_000
    FAST = 240_000_000

    class CPUContextManager():
        def __init__(self, target_speed):
            pass
        
        def __enter__(self):
            pass
        
        def __exit__(self, type, value, trace):
            pass

    def set_cpu_speed(speed):
        pass

    def cpu_speed_context(speed):
        return CPUContextManager(speed)

    def sleep(ms):
        sleep_ms(ms)
    
    def reset():
        print("reset!")
        raise ResetException()
