from graphic.bmfont import FontDrawAscii
from graphic.layout import box_align, box_max_text, box_padding, box_align_text, box_devide, config_to_bool, config_to_int, config_to_box, config_to_color, config_to_align, config_to_direction, DIRECTION_HORIZONTAL, ALIGN_CENTER, EMPTY_BOX
from utime import ticks_us, ticks_diff
from usys import print_exception
from hal_screen import get_format
from graphic.framebuf_helper import ensure_same_format, get_white_color
from graphic import pbm
import framebuf

class Widget():
    def __init__(self) -> None:
        self._id = None
        self._frame = None
        self._box = (0, 0, 0, 0)
    
    def set_id(self, uid):
        self._id = uid
    
    def set_frame(self, frame):
        self._frame = frame
    
    def set_box(self, box):
        self._box = config_to_box(box)
    
    def move_by(self, x_offset, y_offset):
        x, y, w, h = self._box
        self.set_box((x+x_offset, y+y_offset, w, h))
    
    def move_to(self, x, y):
        w, h = self._box[2:4]
        self.set_box((x, y, w, h))

    def animation(self):
        # no animation
        pass

    def render(self):
        pass

class WidgetLayout(Widget):
    def __init__(self):
        super().__init__()
        self._children = []
    
    def check_layout(self):
        # need implement
        pass

    def set_box(self, box):
        if box != self._box:
            super().set_box(box)
            self.check_layout()

    def append_child(self, child):
        if isinstance(child, Widget):
            self._children.append(child)
        self.check_layout()
    
    def remove_child(self, child):
        if child in self._children:
            self._children.remove(child)
        self.check_layout()
    
    def find_child_by_id(self, id):
        if id == None:
            return None
        for ch in self._children:
            if isinstance(ch, WidgetLayout):
                wdg = ch.find_child_by_id(id)
            elif isinstance(ch, Widget):
                wdg = ch if ch._id == id else None
            else:
                continue
            if wdg != None:
                return wdg
        return None

    def clear_child(self):
        self._children.clear()
        self.check_layout()
    
    def animation(self):
        for ch in self._children:
            w, h = ch._box[2:4]
            if w > 0 and h > 0:
                try:
                    ch.animation()
                except Exception as e:
                    print_exception(e)
    
    def render(self):
        for ch in self._children:
            w, h = ch._box[2:4]
            if w > 0 and h > 0:
                try:
                    ch.render()
                except Exception as e:
                    print_exception(e)

class Button(Widget):
    def __init__(self):
        super().__init__()
        self.__label = "B"
        self.__color = 1
        self.__font = FontDrawAscii()
        self.__callback = None
        self.__pressed = False
        self.__focused = False
    
    def set_label(self, value):
        self.__label = value

    def set_color(self, value):
        self.__color = config_to_color(value)

    def set_font(self, value):
        self.__font = value
    
    def set_callback(self, value):
        self.__callback = value

    def set_pressed(self, value):
        self.__pressed = config_to_bool(value)
    
    def set_focused(self, value):
        self.__focused = config_to_bool(value)

    def trigger(self):
        cb = self.__callback
        if cb != None:
            cb()

    def render(self):
        # render button
        frame = self._frame
        box = self._box
        color = self.__color
        label = self.__label
        font = self.__font
        font_size = font.get_font_size()
        # draw label
        if self.__focused:
            bg = color
            fg = 0
        else:
            bg = 0
            fg = color
        tax, tay, taw, tah = box_padding(box, 2, 2, 2, 2)
        frame.fill_rect(tax, tay, taw, tah, bg)
        tax, tay, taw, tah = box_align_text(label, box, font_size, False, ALIGN_CENTER, ALIGN_CENTER)
        font.draw_on_frame(label, frame, tax, tay, fg, taw, tah)
        # draw border
        if self.__pressed:
            bg = color
            fg = 0
        else:
            bg = 0
            fg = color
        x, y, w, h = box
        frame.fill_rect(x+1, y, w-2, 2, fg)
        frame.fill_rect(x, y+1, 2, h-2, fg)
        frame.fill_rect(x+1, y+h-2, w-2, 2, fg)
        frame.fill_rect(x+w-2, y+1, 2, h-2, fg)
        frame.line(x, y, x+1, y+1, bg)
        frame.line(x+w-2, y+h-2, x+w-1, y+h-1, bg)
        frame.line(x, y+h-1, x+1, y+h-2, bg)
        frame.line(x+w-1, y, x+w-2, y+1, bg)

class Text(Widget):
    def __init__(self):
        super().__init__()
        self.__text = ""
        self.__color = 1
        self.__font = FontDrawAscii()
        self.__inverted = False
        self.__align = (ALIGN_CENTER, ALIGN_CENTER)
    
    def set_text(self, value):
        self.__text = value

    def set_color(self, value):
        self.__color = config_to_color(value)

    def set_font(self, value):
        self.__font = value
    
    def set_inverted(self, value):
        self.__inverted = config_to_bool(value)

    def set_align(self, value=(ALIGN_CENTER, ALIGN_CENTER)):
        self.__align = config_to_align(value)

    def render(self):
        frame = self._frame
        box = self._box
        text = self.__text
        font = self.__font
        font_size = font.get_font_size()
        if self.__inverted:
            bg = self.__color
            fg = 0
        else:
            bg = 0
            fg = self.__color
        tax, tay, taw, tah = box
        frame.fill_rect(tax, tay, taw, tah, bg)
        tax, tay, taw, tah = box_align_text(text, box, font_size, False, *self.__align)
        font.draw_on_frame(text, frame, tax, tay, fg, taw, tah)

class ScrollText(Widget):
    def __init__(self):
        super().__init__()
        self.__text = ""
        self.__color = 1
        self.__font = FontDrawAscii()
        self.__speed = 32
        self.__inverted = False
        self.__align = (ALIGN_CENTER, ALIGN_CENTER)
        self.__text_offset = 0
        self.__need_scroll = False
        self.__last_update_us = ticks_us()
    
    def __reset_text_offset(self):
        self.__text_offset = -self.__font.get_font_size()[0] + 1

    def __check_need_scroll(self):
        font_width = self.__font.get_font_size()[0]
        area_width = self._box[2]
        self.__need_scroll = (len(self.__text) * font_width) > area_width
        if self.__need_scroll:
            self.__text = self.__text + " "
        self.__last_update_us = ticks_us()
        self.__reset_text_offset()

    def set_text(self, value):
        index = value.find("\n")
        if index >= 0:
            value = value[:index].replace("\r", "").strip()
        self.__text = value
        self.__check_need_scroll()

    def set_color(self, value):
        self.__color = config_to_color(value)

    def set_font(self, value):
        self.__font = value
        self.__check_need_scroll()
    
    def set_speed(self, value):
        self.__speed = config_to_int(value)

    def set_inverted(self, value):
        self.__inverted = config_to_bool(value)

    def set_align(self, value=(ALIGN_CENTER, ALIGN_CENTER)):
        self.__align = config_to_align(value)

    def set_box(self, box):
        if box != self._box:
            super().set_box(box)
            self.__check_need_scroll()

    def animation(self):
        if self.__need_scroll:
            if self.__inverted:
                bg = self.__color
                fg = 0
            else:
                bg = 0
                fg = self.__color
            frame = self._frame
            box = self._box
            text = self.__text
            font = self.__font
            font_size = font.get_font_size()
            tax, tay, taw, tah = box
            frame.fill_rect(tax, tay, taw, tah, bg)
            # tax, tay, taw, tah = box_align( (0, 0, taw, font_size[1]), box, ALIGN_START, ALIGN_CENTER)
            font_width = font_size[0]
            text_area_width = box_max_text(box, font_size)[2]
            tax, tay, taw, tah = box_align( (0, 0, text_area_width, font_size[1]), box, *self.__align)
            expect_char_count = (text_area_width // font_width) - 1
            text_char_count = len(text)
            text_width = text_char_count * font_width
            last_us = self.__last_update_us
            now_us = ticks_us()
            self.__last_update_us = now_us # <-- update
            text_offset = self.__text_offset
            text_offset += self.__speed * ticks_diff(now_us, last_us) / 1_000_000
            self.__text_offset = text_offset if text_offset < 0 else text_offset % text_width # <-- update
            text_offset = text_offset % text_width
            slice_start = int(text_offset // font_width)
            if slice_start + expect_char_count <= text_char_count:
                slice_text = text[slice_start: slice_start+expect_char_count]
            else:
                slice_text = text[slice_start: text_char_count] + text[: slice_start+expect_char_count-text_char_count]
            xoffset = -int(text_offset % font_width) + font_width
            taw -= font_width
            font.draw_on_frame(slice_text, frame, tax+xoffset, tay, fg, taw, tah)
    
    def render(self):
        if self.__inverted:
            bg = self.__color
            fg = 0
        else:
            bg = 0
            fg = self.__color
        frame = self._frame
        box = self._box
        text = self.__text
        font = self.__font
        font_size = font.get_font_size()
        tax, tay, taw, tah = box
        frame.fill_rect(tax, tay, taw, tah, bg)
        if self.__need_scroll:
            text_area_width = box_max_text(box, font_size)[2]
            tax, tay, taw, tah = box_align( (0, 0, text_area_width, font_size[1]), box, *self.__align)
            self.__reset_text_offset() # reset animation
        else:
            tax, tay, taw, tah = box_align_text(text, box, font_size, False, *self.__align)
        font.draw_on_frame(text, frame, tax, tay, fg, taw, tah)

class PBMImage(Widget):
    def __init__(self):
        super().__init__()
        self.__src = None
        self.__key_color = None
        self.__background = None
        self.__align = (ALIGN_CENTER, ALIGN_CENTER)
    
    def set_src(self, value):
        self.__src = value
    
    def set_key_color(self, value):
        self.__key_color = config_to_color(value)
    
    def set_background(self, value):
        self.__background = config_to_color(value)
    
    def set_align(self, value=(ALIGN_CENTER, ALIGN_CENTER)):
        self.__align = config_to_align(value)

    def render(self):
        SCREEN_FORMAT = get_format()
        box = self._box
        bg = self.__background
        frame = self._frame
        key = self.__key_color
        ix, iy, iw, ih = box
        if bg != None:
            frame.fill_rect(ix, iy, iw, ih, bg)
        with open(self.__src, "rb") as f:
            iw, ih, _, data, = pbm.read_image(f)[:4]
            imgf = framebuf.FrameBuffer(data, iw, ih, framebuf.MONO_HLSB)
            imgf = ensure_same_format(imgf, framebuf.MONO_HLSB, iw, ih, SCREEN_FORMAT, get_white_color(SCREEN_FORMAT))
            ix, iy = box_align((0, 0, iw, ih), box, *self.__align)[:2]
            if key == None:
                frame.blit(imgf, ix, iy)
            else:
                frame.blit(imgf, ix, iy, key)

class FixedLayout(WidgetLayout):
    def __init__(self):
        super().__init__()
        self.__direction = DIRECTION_HORIZONTAL
        self.__start = 0
        self.__end = 0
    
    def set_direction(self, value):
        self.__direction = config_to_direction(value)
        self.check_layout()
    
    def set_start(self, value):
        self.__start = config_to_int(value)
        self.check_layout()
    
    def set_end(self, value):
        self.__end = config_to_int(value)
        self.check_layout()

    def check_layout(self):
        x, y, w, h = self._box
        frame = self._frame
        dire = self.__direction
        start = self.__start
        end = self.__end
        widget_count = 0
        for ch in self._children:
            if start > 0 and widget_count == 0:
                ch.set_frame(frame)
                if dire == DIRECTION_HORIZONTAL:
                    ch.set_box((x, y, start, h))
                else:
                    ch.set_box((x, y, w, start))
            elif (start > 0 and widget_count == 1) or (start <= 0 and widget_count == 0):
                ch.set_frame(frame)
                if dire == DIRECTION_HORIZONTAL:
                    ch.set_box((x+start, y, w-start-end, h))
                else:
                    ch.set_box((x, y+start, w, h-start-end))
            elif (start > 0 and end > 0 and widget_count == 2) or (start <= 0 and end > 0 and widget_count == 1):
                ch.set_frame(frame)
                if dire == DIRECTION_HORIZONTAL:
                    ch.set_box((x+w-end, y, end, h))
                else:
                    ch.set_box((x, y+h-end, w, end))
            else:
                ch.set_frame(None)
                ch.set_box(EMPTY_BOX)
            widget_count += 1

class DevidedLayout(WidgetLayout):
    def __init__(self):
        super().__init__()
        self.__direction = DIRECTION_HORIZONTAL
    
    def set_direction(self, value):
        self.__direction = config_to_direction(value)
        self.check_layout()

    def check_layout(self):
        box = self._box
        frame = self._frame
        dire = self.__direction
        size = len(self._children)
        boxes = box_devide(box, dire, *[1 for _ in range(size)])
        for i in range(size):
            ch = self._children[i]
            ch.set_frame(frame)
            ch.set_box(boxes[i])
