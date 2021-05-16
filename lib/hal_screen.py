from machine import Pin, I2C
from play32hw.ssd1306 import SSD1306_I2C
from play32hw.hw_config import SCREEN_WIDTH, SCREEN_SDA, SCREEN_SCL, SCREEN_HEIGHT

__screen = None

def init(brightness=255):
    global __screen
    if __screen != None:
        return
    i2c = I2C(0, scl=Pin(SCREEN_SCL), sda=Pin(SCREEN_SDA), freq=800000)
    __screen = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)
    __screen.contrast(brightness)

def get_size():
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_framebuffer():
    return __screen

def refresh(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT):
    if isinstance(x, dict) and isinstance(y, list):
        context = x
        effect_area = y
    __screen.show()
