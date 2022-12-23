from machine import freq, lightsleep

VERY_SLOW = 40_000_000
SLOW = 80_000_000
MIDDLE = 160_000_000
FAST = 240_000_000

class CPUContextManager():
    def __init__(self, target_speed):
        self.__s = target_speed
        self.__o = freq()
    
    def __enter__(self):
        self.__o = freq()
        freq(self.__s)
    
    def __exit__(self, type, value, trace):
        freq(self.__o)

def set_cpu_speed(speed):
    freq(speed)

def cpu_speed_context(speed):
    return CPUContextManager(speed)

def sleep(ms):
    lightsleep(ms)
