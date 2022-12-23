'''
FontDraw class
'''
import micropython
from micropython import const

TAB_SIZE = const(4)
ASCII_T = const(9)
ASCII_N = const(10)
ASCII_R = const(13)

# UNIVERSAL
def _draw_char_one_by_one(frame, text, x:int, y:int, color, width_limit:int, height_limit:int, font_width:int, font_height:int, draw_char_on) -> int:
    if (width_limit > 0 and width_limit < font_width) or (height_limit > 0 and height_limit < font_height):
        return 0
    moved_x:int = x
    moved_y:int = y
    count:int = 0
    u8d = text.encode('utf-8')
    length:int = int(len(u8d))
    string = u8d
    tpoint: int = 0
    frame_pixel = frame.pixel
    while tpoint < length:
        # get unicode char
        lead:int = string[tpoint]
        tpoint += 1
        u8size:int = 0
        unicode:int = 0
        while tpoint < length and (string[tpoint] & 0b11_000000) == 0b10_000000:
            unicode = unicode << 6
            unicode = unicode | (string[tpoint] & 0b00_111111)
            tpoint += 1
            u8size += 1
        if u8size == 0:
            unicode = lead
        else:
            lead = (0b00111111 >> u8size) & lead
            unicode = unicode | (lead << (u8size * 6))
        # process special character
        if unicode == ASCII_T:
            char_count = (moved_x - x) // font_width
            lack_of_char = (TAB_SIZE - (char_count % TAB_SIZE)) % TAB_SIZE
            moved_x += font_width * lack_of_char
        elif unicode == ASCII_R:
            moved_x = x
        elif unicode == ASCII_N or (width_limit > 0 and moved_x + font_width - x > width_limit):
            moved_y += font_height
            moved_x = x
        if height_limit > 0 and (moved_y + font_height - y > height_limit):
            if unicode == ASCII_N:
                count += 1 # new line
            return count
        count += 1
        if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
            continue
        # draw
        draw_char_on(frame, frame_pixel, unicode, moved_x, moved_y, color)
        moved_x += font_width
    return count

def get_text_line(text, width_limit:int, size:int) -> int:
    if width_limit < size:
        return 0
    # unicode also ok!
    moved_x:int = 0
    lines:int = 1
    u8d = text.encode('utf-8')
    length:int = int(len(u8d))
    string = u8d
    tpoint: int = 0
    while tpoint < length:
        # get unicode char
        lead:int = string[tpoint]
        tpoint += 1
        u8size:int = 0
        unicode:int = 0
        while tpoint < length and (string[tpoint] & 0b11_000000) == 0b10_000000:
            unicode = unicode << 6
            unicode = unicode | (string[tpoint] & 0b00_111111)
            tpoint += 1
            u8size += 1
        if u8size == 0:
            unicode = lead
        else:
            lead = (0b00111111 >> u8size) & lead
            unicode = unicode | (lead << (u8size * 6))
        # process special character
        if unicode == ASCII_T:
            char_count = moved_x // size
            lack_of_char = TAB_SIZE - char_count % TAB_SIZE
            lack_of_char = 0 if lack_of_char >= TAB_SIZE else lack_of_char
            moved_x += size * lack_of_char
        elif unicode == ASCII_R:
            moved_x = 0
        elif unicode == ASCII_N or (width_limit > 0 and moved_x + size > width_limit):
            lines += 1
            moved_x = 0
        if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
            continue
        moved_x += size
    return lines

def get_text_count(text, width_limit:int, height_limit:int, font_width:int, font_height:int) -> int:
    if (width_limit > 0 and width_limit < font_width) or (height_limit > 0 and height_limit < font_height):
        return 0
    moved_x:int = 0
    moved_y:int = 0
    count:int = 0
    u8d = text.encode('utf-8')
    length:int = int(len(u8d))
    string = u8d
    tpoint: int = 0
    while tpoint < length:
        # get unicode char
        lead:int = string[tpoint]
        tpoint += 1
        u8size:int = 0
        unicode:int = 0
        while tpoint < length and (string[tpoint] & 0b11_000000) == 0b10_000000:
            unicode = unicode << 6
            unicode = unicode | (string[tpoint] & 0b00_111111)
            tpoint += 1
            u8size += 1
        if u8size == 0:
            unicode = lead
        else:
            lead = (0b00111111 >> u8size) & lead
            unicode = unicode | (lead << (u8size * 6))
        # process special character
        if unicode == ASCII_T:
            char_count = moved_x // font_width
            lack_of_char = (TAB_SIZE - (char_count % TAB_SIZE)) % TAB_SIZE
            moved_x += font_width * lack_of_char
        elif unicode == ASCII_R:
            moved_x = 0
        elif unicode == ASCII_N or (width_limit > 0 and moved_x + font_width > width_limit):
            moved_y += font_height
            moved_x = 0
        if height_limit > 0 and (moved_y + font_height > height_limit):
            if unicode == ASCII_N:
                count += 1 # new line
            return count
        count += 1
        if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
            continue
        # draw
        moved_x += font_width
    return count

class FontDraw():
    def get_font_size(self) -> tuple:
        raise NotImplementedError()
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1) -> int:
        raise NotImplementedError()

# ASCII
def _ascii_draw_char_on(frame, _, unicode:int, x:int, y:int, color):
    if unicode <32 or unicode > 127:
        return
    frame.text(bytes([unicode]).decode("ascii"), x, y, color)

class FontDrawAscii(FontDraw):
    def get_font_size(self):
        return (8, 8)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        return _draw_char_one_by_one(frame, text, x, y, color, width_limit, height_limit, 8, 8, _ascii_draw_char_on)
