"""SSD1351 OLED module."""
import framebuf
from utime import sleep_ms
from micropython import const

# Command constants from SSD1351 datasheet
SET_COLUMN = const(0x15)
SET_ROW = const(0x75)
WRITE_RAM = const(0x5C)
READ_RAM = const(0x5D)
SET_REMAP = const(0xA0)
START_LINE = const(0xA1)
DISPLAY_OFFSET = const(0xA2)
DISPLAY_ALL_OFF = const(0xA4)
DISPLAY_ALL_ON = const(0xA5)
NORMAL_DISPLAY = const(0xA6)
INVERT_DISPLAY = const(0xA7)
FUNCTION_SELECT = const(0xAB)
DISPLAY_OFF = const(0xAE)
DISPLAY_ON = const(0xAF)
PRECHARGE = const(0xB1)
DISPLAY_ENHANCEMENT = const(0xB2)
CLOCK_DIV = const(0xB3)
SET_VSL = const(0xB4)
SET_GPIO = const(0xB5)
PRECHARGE2 = const(0xB6)
SET_GRAY = const(0xB8)
USE_LUT = const(0xB9)
PRECHARGE_LEVEL = const(0xBB)
VCOMH = const(0xBE)
CONTRAST_ABC = const(0xC1)
CONTRAST_MASTER = const(0xC7)
MUX_RATIO = const(0xCA)
COMMAND_LOCK = const(0xFD)
HORIZ_SCROLL = const(0x96)
STOP_SCROLL = const(0x9E)
START_SCROLL = const(0x9F)

class Display():
    """Serial interface for 16-bit color (5-6-5 RGB) SSD1351 OLED display.

    Note:  All coordinates are zero based.
    """


    def __init__(self, spi, cs, dc, rst, width=128, height=128):
        """Initialize OLED.

        Args:
            spi (Class Spi):  SPI interface for OLED
            cs (Class Pin):  Chip select pin
            dc (Class Pin):  Data/Command pin
            rst (Class Pin):  Reset pin
            width (Optional int): Screen width (default 128)
            height (Optional int): Screen height (default 128)
        """
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height
        # Initialize GPIO pins and set implementation specific methods
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        self.reset()
        # Send initialization commands
        self.write_cmd(COMMAND_LOCK, 0x12)  # Unlock IC MCU interface
        self.write_cmd(COMMAND_LOCK, 0xB1)  # A2,B1,B3,BB,BE,C1
        self.write_cmd(DISPLAY_OFF)  # Display off
        self.write_cmd(DISPLAY_ENHANCEMENT, 0xA4, 0x00, 0x00)
        self.write_cmd(CLOCK_DIV, 0xF0)  # Clock divider F1 or F0
        self.write_cmd(MUX_RATIO, 0x7F)  # Mux ratio
        self.write_cmd(SET_REMAP, 0x74)  # Segment remapping
        self.write_cmd(START_LINE, 0x00)  # Set Display start line
        self.write_cmd(DISPLAY_OFFSET, 0x00)  # Set display offset
        self.write_cmd(SET_GPIO, 0x00)  # Set GPIO
        self.write_cmd(FUNCTION_SELECT, 0x01)  # Function select
        self.write_cmd(PRECHARGE, 0x32),  # Precharge
        self.write_cmd(PRECHARGE_LEVEL, 0x1F)  # Precharge level
        self.write_cmd(VCOMH, 0x05)  # Set VcomH voltage
        self.write_cmd(NORMAL_DISPLAY)  # Normal Display
        self.write_cmd(CONTRAST_MASTER, 0x0A)  # Contrast master
        self.write_cmd(CONTRAST_ABC, 0xFF, 0xFF, 0xFF)  # Contrast RGB
        self.write_cmd(SET_VSL, 0xA0, 0xB5, 0x55)  # Set segment low volt.
        self.write_cmd(PRECHARGE2, 0x01)  # Precharge2
        self.write_cmd(DISPLAY_ON)  # Display on
        self.clear()

    def refresh(self, x0, y0, x1, y1, data):
        """Write a block of data to display.

        Args:
            x0 (int):  Starting X position.
            y0 (int):  Starting Y position.
            x1 (int):  Ending X position.
            y1 (int):  Ending Y position.
            data (bytes): Data buffer to write.
        """
        assert x1 > x0 and y1 > y0
        self.write_cmd(SET_COLUMN, x0, x1-1)
        self.write_cmd(SET_ROW, y0, y1-1)
        self.write_cmd(WRITE_RAM)
        self.write_data(data)

    def cleanup(self):
        """Clean up resources."""
        self.clear()
        self.display_off()
        self.spi.deinit()
        print('display off')

    def clear(self, color=0):
        """Clear display.

        Args:
            color (Optional int): RGB565 color value (Default: 0 = Black).
        """
        w = self.width
        h = self.height
        # Clear display in 1024 byte blocks
        if color:
            line = color.to_bytes(2, 'big') * 1024
        else:
            line = bytearray(2048)
        for x in range(0, w, 8):
            self.refresh(x, 0, x + 8, h, line)

    def contrast(self, level):
        """Set display contrast to specified level.

        Args:
            level (int): Contrast level (0 - 15).
        Note:
            Can pass list to specifiy
        """
        assert(0 <= level < 16)
        self.write_cmd(CONTRAST_MASTER, level)

    def display_off(self):
        """Turn display off."""
        self.write_cmd(DISPLAY_OFF)

    def display_on(self):
        """Turn display on."""
        self.write_cmd(DISPLAY_ON)

    def reset(self):
        """Perform reset: Low=initialization, High=normal operation.
        Notes: MicroPython implemntation
        """
        self.rst(0)
        sleep_ms(50)
        self.rst(1)
        sleep_ms(50)

    def write_cmd(self, command, *args):
        """Write command to OLED (MicroPython).

        Args:
            command (byte): SSD1351 command code.
            *args (optional bytes): Data to transmit.
        """
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        # Handle any passed data
        if len(args) > 0:
            self.write_data(bytearray(args))

    def write_data(self, data):
        """Write data to OLED (MicroPython).

        Args:
            data (bytes): Data to transmit.
        """
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
