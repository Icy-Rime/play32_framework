import framebuf
from machine import PWM, Pin, SPI
from play32hw.plite.st7565 import ST7565

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
SCREEN_CS = 7
SCREEN_SCL = 2
SCREEN_SDA_MOSI = 3
SCREEN_DC = 10
SCREEN_RST = 11
SCREEN_LED = 6

__screen = None
__screen_led = None
__frame = None
__buffer = None

def init():
    global __screen, __screen_led, __frame, __buffer
    if __screen != None:
        return
    __screen_led = PWM(Pin(SCREEN_LED))
    __screen_led.duty(256)
    cs = Pin(SCREEN_CS, Pin.OUT)
    rst = Pin(SCREEN_RST, Pin.OUT)
    rs = Pin(SCREEN_DC, Pin.OUT)
    sda = Pin(SCREEN_SDA_MOSI, Pin.OUT)
    sck = Pin(SCREEN_SCL, Pin.OUT)
    spi = SPI(1, baudrate=10000000, polarity=1, phase=1, sck=sck, mosi=sda)
    __screen = ST7565(128, 64, spi, rs, cs, rst)
    __buffer = __screen.buffer
    __frame = __screen
    __screen.show()

def get_size():
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_format():
    return framebuf.MONO_VLSB

def get_framebuffer():
    return __frame

def refresh(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT):
    __screen.show()
