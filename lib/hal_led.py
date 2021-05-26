from play32hw.hw_config import PIN_LED
from machine import Pin
from neopixel import NeoPixel

__led = None

def init():
    global __led
    if __led != None or PIN_LED <= 0:
        return
    __led = NeoPixel(Pin(PIN_LED, Pin.OUT), 1)
    __led.fill((0, 0, 0))
    __led.write()


def set_color(r, g, b):
    if __led != None:
        __led.fill((g, r, b))
        __led.write()