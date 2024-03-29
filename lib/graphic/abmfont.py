from graphic.bmfont import FontDraw, arrange_text_gen
from micropython import const

ASCII_4X8_VLSB = b'\x00/\x00\x00\x03\x00\x03\x00?\x12?\x00\x16?\x1a\x00\x12\x08$\x006)\x16(\x02\x01\x00\x00\x00>A\x00A>\x00\x00\n\x07\n\x00\x08>\x08\x00\x00@ \x00\x08\x08\x08\x00\x00 \x00\x00\x10\x08\x04\x00\x1c"\x1c\x00$> \x002*$\x00"*\x14\x00\x18\x14>\x00.*\x12\x00>*:\x00\x02:\x06\x00>*>\x00.*>\x00\x00\x14\x00\x00 \x14\x00\x00\x08\x14"\x00\x14\x14\x14\x00"\x14\x08\x00\x02)\x06\x00\x12)\x1e\x00>\t>\x00?%\x1a\x00\x1e!!\x00?!\x1e\x00?%!\x00?\x05\x01\x00\x1e!9\x00?\x08?\x00!?!\x00\x10 \x1f\x00?\x04;\x00?  \x00?\x06?\x00?\x01>\x00\x1e!\x1e\x00?\t\x06\x00\x1e!^\x00?\t6\x00"%\x19\x00\x01?\x01\x00? ?\x00?\x10\x0f\x00?\x18?\x003\x0c3\x00\x03<\x03\x001-#\x00\x00\x7fA\x00\x04\x08\x10\x00A\x7f\x00\x00\x02\x01\x02\x00@@@\x00\x00\x01\x02\x00\x18$<\x00?$\x18\x00\x18$$\x00\x18$?\x00\x184(\x00\x04?\x05\x00\\T|\x00?\x048\x00$= \x00@=\x00\x00?\x084\x00!? \x00<\x08<\x00<\x048\x00\x18$\x18\x00|$\x18\x00\x18$|\x00<\x08\x04\x00(<\x14\x00\x04>$\x00\x1c <\x00\x0c0\x0c\x00<\x10<\x00$\x18$\x00LP<\x00$4,\x00\x086A\x00\x00\x7f\x00\x00A6\x08\x00\x01\x03\x02\x00'
ASCII_DATA_START = const(0X21)
ASCII_DATA_END = const(0x7E)
ASCII_T = const(9)
ASCII_N = const(10)
ASCII_R = const(13)

def _small_ascii_draw_char_on(frame_pixel, unicode:int, x:int, y:int, color):
    if unicode < ASCII_DATA_START or unicode > ASCII_DATA_END:
        return
    data_offset:int = (unicode - ASCII_DATA_START) * 4
    xp:int = x
    yp:int = y
    for i in range(data_offset, data_offset+4):
        vdata:int = int(ASCII_4X8_VLSB[i])
        yp = y
        for bit in range(8):
            pat:int = 0b1 << bit
            if (vdata & pat) != 0:
                frame_pixel(xp, yp, color)
            yp += 1
        xp += 1

class FontDrawSmallAscii(FontDraw):
    def get_char_width(self, unicode):
        return 4

    def get_font_size(self):
        return (4, 8)
    
    def draw_on_frame(self, text, frame, x, y, color=1, width_limit=-1, height_limit=-1):
        frame_pixel = frame.pixel
        for count, unicode, cx, cy in arrange_text_gen(text, self, x, y, width_limit, height_limit):
            if unicode == ASCII_T or unicode == ASCII_N or unicode == ASCII_R:
                continue
            if unicode >= 0:
                _small_ascii_draw_char_on(frame_pixel, unicode, cx, cy, color)
        return count
