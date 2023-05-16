from utime import ticks_us, ticks_diff, ticks_add, sleep_us
from usys import print_exception
from ucollections import deque
from _thread import start_new_thread

_ACT_DEINIT = 0
_ACT_INIT = 1

class SoftwareTimer():
    ONE_SHOT = 0
    PERIODIC = 1
    def __init__(self, id, *, mode=PERIODIC, period= -1, callback=None):
        self.__started = False
        self.__running = False
        #
        self.__que = deque(tuple(), 16, 1)
        self.init(mode=mode, period=period, callback=callback)

    def __thread_function(self):
        act = -1
        cb = None
        mode = SoftwareTimer.ONE_SHOT
        target_us = 0
        period_us = 0
        while self.__running:
            # check action queue
            while True:
                try:
                    action = self.__que.popleft()
                    (act, cb, mode, target_us, period_us) = action
                    act = -1
                except IndexError:
                    break
            # wait
            if period_us <= 0 or cb == None or ticks_diff(ticks_us(), target_us) < 0:
                # wait 500 us before continue
                sleep_us(500)
                continue
            try:
                # exec callback
                cb(self)
                # schedule next callback
                if mode == SoftwareTimer.ONE_SHOT:
                    cb = None
                    mode = SoftwareTimer.ONE_SHOT
                    target_us = 0
                    period_us = 0
                else:
                    target_us = ticks_add(target_us, period_us) # continue
            except Exception as e:
                print_exception(e)
                print("================")
                self.__started = False # notify thread end
                return # error, exit
        self.__started = False # notify thread end

    def __del__(self):
        self.deinit()
        self.__running = False
        while self.__started: # wait thread end
            sleep_us(500)

    def init(self, *, mode=ONE_SHOT, period=-1, callback=None):
        if callback == None:
            # deinit
            self.deinit()
            return
        action = (_ACT_INIT, callback, mode, ticks_add(ticks_us(), period * 1_000), period * 1_000)
        self.__que.append(action)
        if not self.__started:
            self.__running = True
            start_new_thread(self.__thread_function, tuple())
            self.__started = True

    def deinit(self):
        action = (_ACT_DEINIT, None, SoftwareTimer.ONE_SHOT, 0, 0)
        self.__que.append(action)
