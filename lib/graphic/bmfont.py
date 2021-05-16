'''
FontDraw class
'''

TAB_SIZE = 4
ASCII_T = 9
ASCII_N = 10
ASCII_R = 13

# UNIVERSAL
def _draw_char_one_by_one(frame, x, y, color, width_limit, height_limit, font_size, chars_it, is_special_char, draw_char_on):
    moved_x = x
    moved_y = y
    count = 0
    for char in chars_it:
        count += 1
        if is_special_char(char, ASCII_T):
            char_count = (moved_x - x) // font_size[0]
            lack_of_char = (TAB_SIZE - (char_count % TAB_SIZE)) % TAB_SIZE
            moved_x += font_size[0] * lack_of_char
        elif is_special_char(char, ASCII_R):
            moved_x = x
        elif is_special_char(char, ASCII_N) or (width_limit > 0 and moved_x + font_size[0] - x > width_limit):
            moved_y += font_size[1]
            moved_x = x
        if height_limit > 0 and (moved_y + font_size[1] - y > height_limit):
            return count
        if is_special_char(char, ASCII_T) or is_special_char(char, ASCII_N) or is_special_char(char, ASCII_R):
            continue
        draw_char_on(char, frame, moved_x, moved_y, color)
        moved_x += font_size[0]
    return count

def get_text_line(text, width_limit, size=8):
    # unicode also ok!
    moved_x = 0
    lines = 1
    for char in text:
        if char == '\t':
            char_count = moved_x // size
            lack_of_char = TAB_SIZE - char_count % TAB_SIZE
            lack_of_char = 0 if lack_of_char >= TAB_SIZE else lack_of_char
            moved_x += size * lack_of_char
        elif char == '\r':
            moved_x = 0
        elif char == '\n' or (width_limit > 0 and moved_x + size > width_limit):
            lines += 1
            moved_x = 0
        if char == '\t' or char == '\n' or char == '\r':
            continue
        moved_x += size
    return lines

class FontDraw():
    def get_font_size(self):
        raise NotImplementedError()
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        raise NotImplementedError()

# UNICODE
# import framebuf
# import coding, ubmfont
# from io import BytesIO

# def _unicode_is_special_char(char, ascii):
#     return char == ascii

# def _draw_unicode_text(text, frame, x, y, color, width_limit, height_limit, font_size, font_query):
#     stream = BytesIO(text.encode("utf8"))
#     reader = coding.UTF8Reader(stream)
#     def _unicode_draw_char_on(char, frame, x, y, color):
#         data_buf = font_query.query(char)
#         if data_buf == None:
#             return
#         img = framebuf.FrameBuffer(data_buf, font_size[0], font_size[1], framebuf.MONO_HLSB)
#         for fx in range(font_size[0]):
#             for fy in range(font_size[1]):
#                 if (img.pixel(fx, fy) > 0):
#                     frame.pixel(x+fx, y+fy, color)
#     return _draw_char_one_by_one(frame, x, y, color, width_limit, height_limit, font_size, reader.chars(), _unicode_is_special_char, _unicode_draw_char_on)

# class FontDrawUnicode(FontDraw):
#     def __init__(self, font):
#         if isinstance(font, str):
#             font = open(font, 'rb')
#         self.__fq = ubmfont.FontQuery(font)
#         self.__font_size = self.__fq.get_font_size()
    
#     def get_font_size(self):
#         return self.__font_size
    
#     def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
#         return _draw_unicode_text(text, frame, x, y, color, width_limit, height_limit, self.__font_size, self.__fq)

# ASCII
def _ascii_is_special_char(char, ascii):
    return char.encode("utf8")[0] == ascii

def _ascii_draw_char_on(char, frame, x, y, color):
    frame.text(char, x, y, color)

class FontDrawAscii(FontDraw):
    def get_font_size(self):
        return (8, 8)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        return _draw_char_one_by_one(frame, x, y, color, width_limit, height_limit, (8, 8), text, _ascii_is_special_char, _ascii_draw_char_on)
