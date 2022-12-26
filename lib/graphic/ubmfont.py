from graphic.bmfont import FontDraw, arrange_text_gen
from micropython import const

ASCII_DATA_START = const(0X21)
ASCII_DATA_END = const(0x7E)
ASCII_T = const(9)
ASCII_N = const(10)
ASCII_R = const(13)
ASCII_SPACE = const(32)
BASE_OFFSET = const(770)# 2 + (256 * 3)

class FontDrawUnicode(FontDraw):
    def __init__(self, font_stream, ascii_width=b''):
        self.__font_file = font_stream
        self.__seek = self.__font_file.seek
        self.__read = self.__font_file.read
        self.__area_offset = []
        self.__area_size = bytearray()
        self.__ascii_width = ascii_width # type: bytes
        self.__ascii_width_limit = len(ascii_width)
        self.__font_width = self.__font_file.read(1)[0]
        self.__font_height = self.__font_file.read(1)[0]
        w_block = self.__font_width // 8
        w_block += 0 if self.__font_width % 8 == 0 else 1
        self.__font_data_size = w_block * self.__font_height
        for i in range(256):
            offset = int.from_bytes(self.__font_file.read(2), 'big')
            # offset = self.__font_file.read(2)
            size = int.from_bytes(self.__font_file.read(1), 'big')
            if i == 0:
                # self.__area_offset.extend(b'\x00\x00')
                self.__area_offset.append(0)
            else:
                self.__area_offset.append(offset)
            self.__area_size.append(size)

    # @timed_function
    def _unicode_draw_char_on(self, frame_pixel, unicode:int, x:int, y:int, color):
        if unicode > 0xFFFF:
            return
        area:int = unicode & 0xFF
        pos:int = (unicode & 0xFF00) >> 8
        # query char data
        seek = self.__seek
        read = self.__read
        font_data_size:int = int(self.__font_data_size)
        area_offset:int = int(self.__area_offset[area])
        area_size:int = int(self.__area_size[area])
        offset:int = int(area_offset * (font_data_size + 1)) + BASE_OFFSET
        seek(offset)
        pos_lst = read(area_size)
        data_not_found = True
        data = b''
        for i in range(area_size):
            if pos_lst[i] == pos:
                data_index = i
                offset += area_size + font_data_size * data_index
                seek(offset)
                data_not_found = False
                data = read(font_data_size)
                break
        if data_not_found:
            # not found
            return
        # draw on frame
        font_data = data
        xp:int = x
        yp:int = y
        end_x:int = x + int(self.__font_width)
        for i in range(font_data_size):
            hdata = int(font_data[i])
            for bit in range(8):
                pat:int = 0b10000000 >> bit
                if (hdata & pat) != 0:
                    if 0 <= xp and 0 <= yp:
                        frame_pixel(xp, yp, color)
                xp += 1
            if xp >= end_x:
                xp = x
                yp += 1

    def get_char_width(self, unicode: int) -> int:
        if unicode == ASCII_SPACE:
            return self.__font_width // 2 # half width space
        elif unicode == ASCII_N or unicode == ASCII_R:
            return 0
        ascii_offset = unicode - ASCII_DATA_START
        if ascii_offset >= 0 and ascii_offset < self.__ascii_width_limit:
            return self.__ascii_width[ascii_offset]
        else:
            return self.__font_width

    def get_font_size(self):
        return (self.__font_width, self.__font_height)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        draw_char_on = self._unicode_draw_char_on
        frame_pixel = frame.pixel
        for count, unicode, cx, cy in arrange_text_gen(text, self, x, y, width_limit, height_limit):
            if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
                continue
            if unicode >= 0:
                draw_char_on(frame_pixel, unicode, cx, cy, color)
        return count
