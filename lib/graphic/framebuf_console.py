'''
framebuf tool kit Module
'''
from graphic.bmfont import FontDrawAscii, get_text_lines
# Console
class Console():
    def __init__(self, frame, width, height, font_draw=None, color=1, display_update_fun=None):
        self.__fd = FontDrawAscii() if font_draw == None else font_draw
        self.__color = color
        self.__font_size = self.__fd.get_font_size()
        self.__print_y = 0
        self.__print_frame = frame
        self.__print_frame_width = width
        self.__print_frame_height = height
        self.__show_f = display_update_fun
    def log(self, *args, show=True):
        txts = []
        for t in args:
            txts.append(str(t))
        text = ' '.join(txts)
        lines = len(get_text_lines(text, self.__fd, self.__print_frame_width, -1))
        new_y = self.__print_y + lines * self.__font_size[1]
        if new_y > self.__print_frame_height:
            offset = new_y - self.__print_frame_height
            self.__print_y -= offset
            self.__print_frame.scroll(0, 0-offset)
            new_y = self.__print_frame_height
        self.__print_frame.fill_rect(0, self.__print_y, self.__print_frame_width, lines * self.__font_size[1], 0)
        self.__fd.draw_on_frame(text, self.__print_frame, 0, self.__print_y, self.__color, self.__print_frame_width, self.__print_frame_height)
        self.__print_y = new_y
        if self.__show_f != None and show:
            self.__show_f()
    def clear(self, *_, show=True):
        self.__print_frame.fill_rect(0, 0, self.__print_frame_width, self.__print_frame_height, 0)
        self.__print_y = 0
        if self.__show_f != None and show:
            self.__show_f()
