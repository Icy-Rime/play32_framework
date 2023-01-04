from utime import ticks_us, ticks_diff, ticks_add
from usys import print_exception
from _thread import start_new_thread, allocate_lock, get_ident

class SoftwareTimer():
    ONE_SHOT = 0
    PERIODIC = 1
    def __init__(self, id, *, mode=PERIODIC, period= -1, callback=None):
        self.__cb = None
        self.__thd = None
        self.__current_thd = 0
        self.__target_us = 0
        self.__period = 0
        self.__mode = SoftwareTimer.ONE_SHOT
        self.__lock = allocate_lock()
        self.init(mode=mode, period=period, callback=callback)

    def __protect(fn):
        def func(self, *args, **kwargs):
            if not isinstance(self, SoftwareTimer) or get_ident() == self.__thd:
                return fn(self, *args, **kwargs)
            else:
                self.__lock.acquire()
                self.__thd = get_ident()
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    self.__thd = None
                    self.__lock.release()
        return func

    def __callback(self):
        self.__current_thd = get_ident()
        while True:
            # waiting
            while ticks_diff(ticks_us(), self.__target_us) < 0:
                if get_ident() != self.__current_thd:
                    return
            # exec callback
            try:
                self.__lock.acquire()
                self.__thd = get_ident()
                if get_ident() == self.__current_thd and self.__cb != None:
                    self.__cb(self)
                    if self.__mode == SoftwareTimer.ONE_SHOT:
                        return # end timer
                    else:
                        self.__target_us = ticks_add(self.__target_us, self.__period) # continue
                else:
                    return # end timer
            except Exception as e:
                print_exception(e)
            finally:
                self.__thd = None
                self.__lock.release()

    @__protect
    def init(self, *, mode=ONE_SHOT, period=-1, callback=None):
        if callback == None:
            # deinit
            self.__cb = None
            self.__target_us = 0
            self.__period = 0
            self.__mode = SoftwareTimer.ONE_SHOT
            return
        self.__target_us = ticks_add(ticks_us(), period * 1_000)
        self.__period = period * 1_000
        self.__mode = mode
        self.__cb = callback
        start_new_thread(self.__callback, tuple())

    @__protect
    def deinit(self):
        self.__cb = None
        self.__target_us = 0
        self.__period = 0
        self.__mode = SoftwareTimer.ONE_SHOT

    def value(self):
        return 0 # ?