from utime import sleep_ms
from play32hw.hw_config import ResetException
from play32hw.punix.hal_screen import deinit as scr_deinit
from play32hw.punix.hal_buzz import deinit as buzz_deinit
from play32hw.shared_timer import stop_all_timer

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
    # clean up
    scr_deinit()
    buzz_deinit()
    stop_all_timer()
    sleep_ms(500)
    # reset
    raise ResetException()
