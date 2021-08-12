from graphic.bmfont import FontDraw, _draw_char_one_by_one
import micropython
from micropython import const

BASE_OFFSET = const(770)# 2 + (256 * 3)
class FontDrawUnicode(FontDraw):
    def __init__(self, font_stream):
        self.__font_file = font_stream
        self.__seek = self.__font_file.seek
        self.__read = self.__font_file.read
        self.__area_offset = []
        self.__area_size = bytearray()
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
    @micropython.viper
    def _unicode_draw_char_on(self, frame, unicode:int, x:int, y:int, color):
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
        pos_lst = ptr8(read(area_size))
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
        font_data = ptr8(data)
        pixel = frame.pixel
        xp:int = x
        yp:int = y
        end_x:int = x + int(self.__font_width)
        for i in range(font_data_size):
            hdata = int(font_data[i])
            for bit in range(8):
                pat:int = 0b10000000 >> bit
                if (hdata & pat) != 0:
                    if 0 <= xp and 0 <= yp:
                        pixel(xp, yp, color)
                xp += 1
            if xp >= end_x:
                xp = x
                yp += 1

    def get_font_size(self):
        return (self.__font_width, self.__font_height)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        return _draw_char_one_by_one(frame, text, x, y, color, width_limit, height_limit, self.__font_width, self.__font_height, self._unicode_draw_char_on)
