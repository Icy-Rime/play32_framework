import framebuf
from machine import Pin, I2C, SPI
from play32hw.hw_config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_DRIVER, SCREEN_SDA_MOSI, SCREEN_SCL, SCREEN_CS, SCREEN_DC, SCREEN_RST

__screen = None
__frame = None
__buffer = None
__format = -1

def init():
    global __screen, __frame, __buffer, __format
    if __screen != None:
        return
    if SCREEN_DRIVER == "ssd1306":
        from play32hw.ssd1306 import SSD1306_I2C
        i2c = I2C(0, scl=Pin(SCREEN_SCL), sda=Pin(SCREEN_SDA_MOSI), freq=800000)
        __screen = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)
        __buffer = __screen.buffer
        __frame = __screen
        __format = framebuf.MONO_VLSB
    elif SCREEN_DRIVER == "ssd1351":
        from play32hw.ssd1351 import Display as SSD1351
        screen_spi = SPI(1, baudrate=20000000, sck=Pin(SCREEN_SCL), mosi=Pin(SCREEN_SDA_MOSI))
        screen_cs = Pin(SCREEN_CS)
        screen_dc = Pin(SCREEN_DC)
        screen_rs = Pin(SCREEN_RST)
        __screen = SSD1351(screen_spi, screen_cs, screen_dc, screen_rs, 128, 128)
        __buffer = bytearray(SCREEN_WIDTH * SCREEN_HEIGHT * 2)
        __frame = framebuf.FrameBuffer(__buffer, 128, 128, framebuf.RGB565)
        __format = framebuf.RGB565

def get_size():
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_format():
    return __format

def get_framebuffer():
    return __frame

def refresh(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT):
    if SCREEN_DRIVER == "ssd1306":
        if w * 100 >= SCREEN_WIDTH * 75 and h * 100 >= SCREEN_HEIGHT * 75:
            __screen.show()
        else:
            __screen.refresh(x, y, w, h)
    elif SCREEN_DRIVER == "ssd1351":
        __screen.refresh(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, __buffer)
