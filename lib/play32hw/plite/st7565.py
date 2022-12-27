'''
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Example:
cs = Pin(18, Pin.OUT)
rst = Pin(5, Pin.OUT)
rs = Pin(17, Pin.OUT)
sda = Pin(16, Pin.OUT)
sck = Pin(4, Pin.OUT)
spi = SPI(1, baudrate=10000000, polarity=1, phase=1, sck=sck, mosi=sda)
display = ST7565(128, 64, spi, rs, cs, rst)
'''


from micropython import const
from utime import sleep_ms
import framebuf

# LCD Commands definition
CMD_DISPLAY_ON = const(0xAF)
CMD_DISPLAY_OFF = const(0xAF)
CMD_SET_START_LINE = const(0x40)
CMD_SET_PAGE = const(0xB0)
CMD_COLUMN_UPPER = const(0x10)
CMD_COLUMN_LOWER = const(0x00)
CMD_SET_ADC_NORMAL = const(0xA0)
CMD_SET_ADC_REVERSE = const(0xA1)
CMD_SET_COL_NORMAL = const(0xC0)
CMD_SET_COL_REVERSE = const(0xC8)
CMD_SET_DISPLAY_NORMAL = const(0xA6)
CMD_SET_DISPLAY_REVERSE = const(0xA7)
CMD_SET_ALLPX_ON = const(0xA5)
CMD_SET_ALLPX_NORMAL = const(0xA4)
CMD_SET_BIAS_9 = const(0xA2)
CMD_SET_BIAS_7 = const(0xA3)
CMD_DISPLAY_RESET = const(0xE2)
CMD_NOP = const(0xE3)
CMD_TEST = const(0xF0)  # Exit this mode with CMD_NOP
CMD_SET_POWER = const(0x2F)
CMD_SET_RESISTOR_RATIO = const(0x20)
CMD_SET_VOLUME = const(0x81)

# Display init parameters
DISPLAY_CONTRAST = const(0x1B)
DISPLAY_RESISTOR_RATIO = const(5)

DRIVER_COLS = const(132)
DRIVER_PAGES = const(8)
# Rotaion
ROTATION_0 = const(0)
ROTATION_180 = const(2)

class ST7565(framebuf.FrameBuffer):
    """ST7565 Display controller driver"""
    def __init__(self, width, height, spi, a0, cs, rst, rotation=ROTATION_0):
        self.spi = spi
        self.rst = rst
        self.a0 = a0
        self.cs = cs
        self.width = width
        self.height = height
        self.rotation = rotation
        self.pages = height // 8
        self.pages += 0 if height % 8 == 0 else 1
        data_size = self.pages * width
        self.buffer = memoryview(bytearray(data_size))
        super().__init__(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB)
        self.display_init()

    def display_init(self):
        self.reset()
        sleep_ms(1)
        self.write_cmd(CMD_NOP)
        self.write_cmd(CMD_DISPLAY_RESET)
        self.write_cmd(CMD_SET_POWER)
        self.write_cmd(CMD_SET_BIAS_9)
        self.write_cmd(CMD_SET_RESISTOR_RATIO + DISPLAY_RESISTOR_RATIO)
        self.write_cmd(CMD_SET_VOLUME)
        self.write_cmd(DISPLAY_CONTRAST)
        if self.rotation == ROTATION_0:
            self.write_cmd(CMD_SET_ADC_NORMAL)
        else:
            self.write_cmd(CMD_SET_ADC_REVERSE)
        if self.rotation == ROTATION_0:
            self.write_cmd(CMD_SET_COL_REVERSE)
        else:
            self.write_cmd(CMD_SET_COL_NORMAL)
        self.write_cmd(CMD_DISPLAY_ON)

    def write_cmd(self, cmd):
        self.a0(0)
        self.cs(0)
        self.spi.write(bytes([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.a0(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

    def set_contrast(self, value=DISPLAY_CONTRAST):
        if 0x1 <= value <= 0x3f:
            for cmd in (
                CMD_SET_VOLUME,
                    value):
                self.write_cmd(cmd)

    def reset(self):
        self.rst(0)
        sleep_ms(1)
        self.rst(1)

    def show(self):
        _a0 = self.a0
        _cs = self.cs
        _write = self.spi.write
        _buffer = self.buffer
        _cols = self.width
        if self.rotation == ROTATION_0:
            base_page = 0
            column_upper = CMD_COLUMN_UPPER
            column_lower = CMD_COLUMN_LOWER
        else:
            base_page = DRIVER_PAGES - self.pages
            column = DRIVER_COLS - _cols
            column_upper = ((column>>4)&0x0f)+0x10
            column_lower = column&0x0f
        for i in range(self.pages):
            # cmd
            _a0(0)
            _cs(0)
            _write(bytes((
                CMD_SET_START_LINE,
                CMD_SET_PAGE + base_page + i,
                column_upper,
                column_lower
            )))
            _cs(1)
            # data
            _a0(1)
            _cs(0)
            _write(_buffer[i*_cols: (i+1)*_cols])
            _cs(1)
