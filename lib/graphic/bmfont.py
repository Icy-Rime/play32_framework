'''
FontDraw class
'''
from micropython import const

TAB_SIZE = const(2)
ASCII_T = const(9)
ASCII_N = const(10)
ASCII_R = const(13)

class FontDraw():
    def get_char_width(self, unicode: int) -> int:
        raise NotImplementedError()

    def get_font_size(self) -> tuple:
        raise NotImplementedError()
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1) -> int:
        raise NotImplementedError()

# ASCII
class FontDrawAscii(FontDraw):
    def get_char_width(self, unicode):
        return 8
    
    def get_font_size(self):
        return (8, 8)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        frame_text = frame.text
        for count, unicode, cx, cy in arrange_text_gen(text, self, x, y, width_limit, height_limit):
            if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
                continue
            if unicode <32 or unicode > 127:
                continue
            frame_text(bytes([unicode]).decode("ascii"), cx, cy, color)
        return count

# UNIVERSAL
def arrange_text_gen(text: str, font: FontDraw, x: int, y: int, width_limit: int = -1, height_limit: int = -1):
    font_width, font_height = font.get_font_size()
    get_char_width = font.get_char_width
    if (width_limit > 0 and width_limit < font_width) or (height_limit > 0 and height_limit < font_height):
        return
    moved_x: int = x
    moved_y: int = y
    count: int = 0
    u8d = text.encode('utf-8')
    length: int = len(u8d)
    tpoint: int = 0
    while tpoint < length:
        # get unicode char
        lead: int = u8d[tpoint]
        tpoint += 1
        u8size: int = 0
        unicode: int = 0
        while tpoint < length and (u8d[tpoint] & 0b11_000000) == 0b10_000000:
            unicode = unicode << 6
            unicode = unicode | (u8d[tpoint] & 0b00_111111)
            tpoint += 1
            u8size += 1
        if u8size == 0:
            unicode = lead
        else:
            lead = (0b00111111 >> u8size) & lead
            unicode = unicode | (lead << (u8size * 6))
        # process special character
        char_width = get_char_width(unicode)
        if unicode == ASCII_N or unicode == ASCII_R:
            char_width = 0
        elif unicode == ASCII_T:
            char_width += font_width * TAB_SIZE
        if unicode == ASCII_N or (width_limit > 0 and moved_x + char_width - x > width_limit):
            moved_y += font_height
            moved_x = x
        if height_limit > 0 and (moved_y + font_height - y > height_limit):
            if unicode == ASCII_N:
                count += 1 # new line
            yield count, -1, 0, 0
            return
        # draw
        yield count, unicode, moved_x, moved_y
        count += 1
        if unicode == ASCII_N or unicode == ASCII_R:
            continue
        moved_x += char_width
    yield count, -1, 0, 0
    return

def get_text_width(text, font:FontDraw):
    font_width, font_height = font.get_font_size()
    get_char_width = font.get_char_width
    u8d = text.encode('utf-8')
    length: int = len(u8d)
    tpoint: int = 0
    line_width = 0
    while tpoint < length:
        # get unicode char
        lead: int = u8d[tpoint]
        tpoint += 1
        u8size: int = 0
        unicode: int = 0
        while tpoint < length and (u8d[tpoint] & 0b11_000000) == 0b10_000000:
            unicode = unicode << 6
            unicode = unicode | (u8d[tpoint] & 0b00_111111)
            tpoint += 1
            u8size += 1
        if u8size == 0:
            unicode = lead
        else:
            lead = (0b00111111 >> u8size) & lead
            unicode = unicode | (lead << (u8size * 6))
        if unicode == ASCII_T:
            line_width += font_width * TAB_SIZE
        elif unicode == ASCII_R or unicode == ASCII_N:
            continue
        else:
            line_width += get_char_width(unicode)
    return line_width

def get_text_count(text, font:FontDraw, width_limit:int, height_limit:int) -> int:
    for count, unicode, cx, cy in arrange_text_gen(text, font, 0, 0, width_limit, height_limit):
        pass
    return count

def get_text_lines(text, font:FontDraw, width_limit:int, height_limit:int) -> list:
    current_line_count = 0
    last_y = 0
    lines = []
    for count, unicode, cx, cy in arrange_text_gen(text, font, 0, 0, width_limit, height_limit):
        if unicode < 0: continue
        if (unicode == ASCII_N or unicode == ASCII_R) and cx <= 0:
            lines.append(count - current_line_count + 1)
            current_line_count = count + 1
            last_y = cy
        elif cy != last_y:
            lines.append(count - current_line_count)
            current_line_count = count
            last_y = cy
    if count - current_line_count > 0:
        lines.append(count - current_line_count)
    return lines
