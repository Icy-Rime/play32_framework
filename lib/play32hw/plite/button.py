from machine import Pin, Signal
from utime import ticks_ms, ticks_diff
from micropython import const

SHAKE_IGNORE_MS = const(20)
CLICK_DELAY_MS = const(200)
LONG_PRESS_MS = const(500)

EVENT_NONE = const(0x00)
EVENT_CLICK = const(0x01)
EVENT_LONG_PRESS = const(0x02)
EVENT_MAYBE_CLICK = const(0x03)
EVENT_PRESS_DOWN = const(0x04)

class Button():
    def __init__(self, io: int, invert=False, many_click=True):
        self.__btn = Signal(Pin(io, Pin.IN), invert=invert)
        self.__many_click = many_click
        self.__wait_release = False # flag wait for release
        self.__ptime = 0 # last time press down
        self.__rtime = 0 # last time release up
        self.__ccount = 0 # click count
    
    @property
    def pressed(self):
        return self.__btn.value() >= 1 # type: ignore

    def scan(self) -> tuple[int, int]:
        """ Scan the button and return the event.
            Return (EVENT, CLICK_COUNT)
            if nothing happened, it will return (EVENT_NONE, 0)
        """
        pressed = self.pressed
        if self.__ptime == 0:
            if ticks_diff(ticks_ms(), self.__rtime) > SHAKE_IGNORE_MS:
                # press
                if pressed:
                    self.__ptime = ticks_ms()
                    self.__rtime = 0
                    self.__ccount += 1
                    return EVENT_PRESS_DOWN, self.__ccount
                # delay click
                elif self.__many_click and self.__rtime > 0:
                    if ticks_diff(ticks_ms(), self.__rtime) > CLICK_DELAY_MS:
                        self.__rtime = 0
                        num_click = self.__ccount
                        self.__ccount = 0
                        return EVENT_CLICK, num_click
        else:
            if ticks_diff(ticks_ms(), self.__ptime) > SHAKE_IGNORE_MS:
                # release
                if not pressed:
                    self.__ptime = 0
                    if self.__wait_release: # long press release
                        self.__rtime = 0
                        self.__ccount = 0
                        self.__wait_release = False
                    else:
                        self.__rtime = ticks_ms()
                        if not self.__many_click:
                            self.__ccount = 0
                            return EVENT_CLICK, 1
                        else:
                            return EVENT_MAYBE_CLICK, self.__ccount
                # long press
                elif ticks_diff(ticks_ms(), self.__ptime) > LONG_PRESS_MS and not self.__wait_release:
                    self.__wait_release = True
                    return EVENT_LONG_PRESS, self.__ccount
        return EVENT_NONE, 0
