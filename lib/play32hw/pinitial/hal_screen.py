import framebuf
from machine import Pin, I2C
from play32hw.pinitial.ssd1306 import SSD1306_I2C

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
SCREEN_SCL = 18
SCREEN_SDA_MOSI = 19

__screen = None
__frame = None
__buffer = None

def init():
    global __screen, __frame, __buffer
    if __screen != None:
        return
    i2c = I2C(0, scl=Pin(SCREEN_SCL), sda=Pin(SCREEN_SDA_MOSI), freq=800000)
    __screen = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)
    __buffer = __screen.buffer
    __frame = __screen

def get_size():
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_format():
    return framebuf.MONO_VLSB

def get_framebuffer():
    return __frame

def refresh(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT):
    if w * 100 >= SCREEN_WIDTH * 75 and h * 100 >= SCREEN_HEIGHT * 75:
        __screen.show()
    else:
        __screen.refresh(x, y, w, h)
