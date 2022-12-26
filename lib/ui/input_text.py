# [title]
# text
# <del ok>
# [pinyin|number]
# [abcdefg hijklmn]
# [opq rst uvw xyz]
# [.,!?:;-_~+=()<>]
# <mode switch(a|A|中)>

import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from graphic.bmfont import FontDrawAscii
from buildin_resource.font import get_font_8px
from ui.utils import draw_label_nav, draw_label_header, draw_button, draw_label_invert, sleep_save_power
from play32hw.cpu import cpu_speed_context, VERY_SLOW, FAST
from ui._input_method import InputMethod
from ui.select import select_list_gen
from buildin_resource.input_dict import get_input_dict
from utime import ticks_ms, ticks_diff
_KBD_C_1 = "0123456789[|]'\""
_KBD_C_2 = "abcdefg hijklmn"
_KBD_C_3 = "opq rst uvw xyz"
_KBD_C_4 = ".,!?:;-_~+=()<>"
_MODE_C = ["mode:a", "mode:A", "mode:中"]
_SPECIAL_C = ["delele", "confirm"] # first is delete, last is confirm, others must be added between them

class _KBD_LINE:
    def __init__(self, chars=""):
        self.__chs = chars
        self.__focus = -1
        self.__redraw = True
    
    # common func
    def redraw(self):
        self.__redraw = True

    def set_focus(self, f):
        if f == None:
            self.__focus = -1 # no focus
            self.__redraw = True
            return None
        # f = max(f, 0)
        # f = min(f, len(self.__chs) - 1)
        f = f % len(self.__chs)
        if f != self.__focus:
            self.__redraw = True
            self.__focus = f
        return f
    
    def get_focused_text(self):
        if self.__focus >= 0:
            return self.__chs[self.__focus]
        return "\x00"
    
    def draw(self, frame, x, y, w, h, font, white, force=False):
        if self.__redraw or force:
            with cpu_speed_context(FAST):
                frame.fill_rect(x, y, w, h, 0)
                FW, FH = font.get_font_size()
                tw = len(self.__chs) * FW
                offset = (w - tw) // 2
                font.draw_on_frame(self.__chs, frame, x+offset, y, white, w, h)
                if self.__focus >= 0:
                    ch = self.__chs[self.__focus]
                    off = offset + FW * self.__focus
                    frame.fill_rect(x+off, y, FW, FH, white)
                    font.draw_on_frame(ch, frame, x+off, y, 0, FW, FH)
                self.__redraw = False
                return True # changed
        return False # nothing change

class _KBD_OPTION:
    def __init__(self, options=""):
        self.__ops = options
        self.__focus = False
        self.__op_focus = 0
        self.__redraw = True
    
    def change_op(self, offset):
        self.__op_focus += offset
        self.__op_focus = self.__op_focus % len(self.__ops)
        self.__redraw = True

    # common func
    def redraw(self):
        self.__redraw = True

    def set_focus(self, f):
        if f != None:
            bf = True
        else:
            bf = False
        if bf != self.__focus:
            self.__redraw = True
            self.__focus = bf
        # not change outside
        return f
    
    def get_focused_text(self):
        return self.__ops[self.__op_focus]
    
    def draw(self, frame, x, y, w, h, font, white, force=False):
        if self.__redraw or force:
            with cpu_speed_context(FAST):
                black = white if self.__focus else 0
                white = 0 if self.__focus else white
                frame.fill_rect(x, y, w, h, black)
                draw_label_nav(frame, x, y, w, h, font, white, self.get_focused_text())
                self.__redraw = False
                return True # changed
        return False # nothing change

class _KBD_TEXT:
    def __init__(self, text=""):
        self.__text = text
        self.__focus = False
        self.__cursor = len(text)
        self.__show_cursor = True
        self.__last_ms = ticks_ms()
        self.__redraw = True
    
    def _get_text_with_cursor(self, size):
        cursor_char = "|" if self.__show_cursor else "'"
        if size <= self.__cursor - 1:
            return self.__text[self.__cursor-size+1:self.__cursor] + cursor_char
        else:
            p1 = self.__text[:self.__cursor]
            p2 = self.__text[self.__cursor: size - 1]
            return p1 + cursor_char + p2

    def move_cursor(self, offset):
        self.__cursor += offset
        self.__cursor = max(self.__cursor, 0)
        self.__cursor = min(self.__cursor, len(self.__text))
        self.__redraw = True

    def insert(self, v):
        if len(v) <= 0:
            return
        self.__text = self.__text[:self.__cursor] + v + self.__text[self.__cursor:]
        self.move_cursor(len(v))

    def delete(self):
        delete_index = self.__cursor - 1
        if delete_index >= 0:
            self.__text = self.__text[:delete_index] + self.__text[delete_index+1:]
            self.move_cursor(-1)

    def get_text(self):
        return self.__text

    # common func
    def redraw(self):
        self.__redraw = True
    
    def set_focus(self, f):
        if f != None:
            bf = True
        else:
            bf = False
        if bf != self.__focus:
            self.__redraw = True
            self.__focus = bf
        # not change outside
        return f
    
    def draw(self, frame, x, y, w, h, font, white, force=False):
        now = ticks_ms()
        if ticks_diff(now, self.__last_ms) > 500:
            self.__redraw = True
            self.__show_cursor = (not self.__show_cursor)
            self.__last_ms = now
        if self.__redraw or force:
            with cpu_speed_context(FAST):
                black = white if self.__focus else 0
                white = 0 if self.__focus else white
                FW, FH = font.get_font_size()
                char_count = w // FW
                t = self._get_text_with_cursor(char_count)
                offset_x = (w % FW) // 2
                offset_y = (h % FH) // 2
                frame.fill_rect(x, y, w, h, black)
                font.draw_on_frame(t, frame, x+offset_x, y+offset_y, white, w, h)
                self.__redraw = False
                return True # changed
        return False # nothing change

class _KBD_PINYIN:
    def __init__(self):
        self.__im = InputMethod(get_input_dict())
        self.__focus = False
        self.__redraw = True
    
    def insert(self, v):
        self.__im.input_byte(v.encode("utf8")[0])
        self.__redraw = True

    def delete(self):
        self.__im.input_byte(0x08)
        self.__redraw = True

    def can_delete(self):
        return len(self.__im.get_input_code()) > 0

    def select_word_gen(self):
        if len(self.__im.get_input_code()) <= 0:
            yield ""
        lst = self.__im.all_words()
        for v in select_list_gen(self.__im.get_input_code(), lst):
            yield None
            if v == None:
                continue
            if v < 0:
                yield ""
            else:
                self.__im.clear()
                yield lst[v]

    # common func
    def redraw(self):
        self.__redraw = True
    
    def set_focus(self, f):
        if f != None:
            bf = True
        else:
            bf = False
        if bf != self.__focus:
            self.__redraw = True
            self.__focus = bf
        # not change outside
        return f
    
    def draw(self, frame, x, y, w, h, font, white, force=False):
        if self.__redraw or force:
            with cpu_speed_context(FAST):
                frame.fill_rect(x, y, w, h, 0)
                if self.__focus:
                    draw_label_invert(frame, x, y, w, h, font, white, self.__im.get_input_code())
                else:
                    draw_button(frame, x, y, w, h, font, white, self.__im.get_input_code())
                self.__redraw = False
                return True # changed
        return False # nothing change

def input_text(text="", title="Edit Text"):
    """ show a dialog and display some text.
        return str
    """
    with cpu_speed_context(VERY_SLOW):
        for v in input_text_gen(text, title):
            if v != None:
                return v
            sleep_save_power() # save power

def input_text_gen(text="", title="Edit Text"):
    # test
    # im = InputMethod(get_input_dict())
    # for c in b"long":
    #     im.input_byte(c)
    # print(im.all_words())
    # test end
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    F8_MONO = FontDrawAscii()
    FW, FH = F8.get_font_size()
    EDIT_TEXT_H = SH - (FH * 7)
    frame = hal_screen.get_framebuffer()
    kbdl_piy = _KBD_PINYIN()
    kbdl_txt = _KBD_TEXT(text.replace("\n", ""))
    kbdl_spc = _KBD_OPTION(_SPECIAL_C)
    kbdl_num = _KBD_LINE(_KBD_C_1)
    kbdl_a2n = _KBD_LINE(_KBD_C_2)
    kbdl_o2z = _KBD_LINE(_KBD_C_3)
    kbdl_sym = _KBD_LINE(_KBD_C_4)
    kbdl_mod = _KBD_OPTION(_MODE_C)
    kbd_list = [
        kbdl_txt,
        kbdl_spc,
        kbdl_num,
        kbdl_a2n,
        kbdl_o2z,
        kbdl_sym,
        kbdl_mod,
    ]
    redraw = True
    refresh = False
    focus_line = 0
    focus_col = 0
    # init
    kbdl_spc.change_op(1)
    focus_col = kbd_list[focus_line].set_focus(focus_col)
    kbd_line_size = len(kbd_list)
    mode = 0 # 0: a 1: A 2: 中
    while True:
        action_code = None
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A:
                kbd = kbd_list[focus_line]
                if isinstance(kbd, _KBD_LINE):
                    action_code = kbd.get_focused_text()
                elif isinstance(kbd, _KBD_OPTION) and kbd != kbdl_mod:
                    action_code = kbd.get_focused_text()
                elif isinstance(kbd, _KBD_PINYIN):
                    # select word
                    for v in kbdl_piy.select_word_gen():
                        yield None
                        if v == None:
                            continue
                        if len(v) > 0:
                            kbdl_txt.insert(v)
                        break
                    redraw = True
                    # select word end
            if ekey == KEY_B:
                kbd = kbd_list[focus_line]
                if isinstance(kbd, (_KBD_TEXT, _KBD_PINYIN, _KBD_LINE)):
                    action_code = _SPECIAL_C[0] # delete
            if ekey == KEY_LEFT or ekey == KEY_RIGHT: 
                off = 1 if ekey == KEY_RIGHT else -1
                kbd = kbd_list[focus_line]
                if isinstance(kbd, _KBD_TEXT):
                    kbd.move_cursor(off)
                elif isinstance(kbd, _KBD_LINE):
                    focus_col = kbd.set_focus(focus_col + off)
                elif isinstance(kbd, _KBD_OPTION):
                    kbd.change_op(off)
                    if kbd == kbdl_mod: # special
                        action_code = kbd.get_focused_text()
            if ekey == KEY_UP or ekey == KEY_DOWN:
                off = 1 if ekey == KEY_DOWN else -1
                newf = focus_line + off
                # newf = max(newf, 0)
                # newf = min(newf, kbd_line_size - 1)
                newf = newf % kbd_line_size
                if newf != focus_line:
                    kbd_list[focus_line].set_focus(None)
                    kbd_list[newf].set_focus(focus_col)
                    focus_line = newf
        # process action
        if isinstance(action_code, str):
            # print(action_code)
            if action_code.startswith("mode:"):
                if mode == 2:
                    # from mode 2
                    kbd_list[2] = kbdl_num
                    kbdl_num.redraw()
                if action_code == _MODE_C[2]:
                    mode = 2
                elif action_code == _MODE_C[1]:
                    mode = 1
                else:
                    mode = 0
                if mode == 2:
                    # to mode 2
                    kbd_list[2] = kbdl_piy
                    kbdl_piy.redraw()
            elif action_code == _SPECIAL_C[-1]:
                # confirm
                yield kbdl_txt.get_text()
            elif action_code == _SPECIAL_C[0]:
                # delete
                if mode == 2 and kbdl_piy.can_delete():
                    kbdl_piy.delete()
                else:
                    kbdl_txt.delete()
            else:
                # insert
                if mode == 2:
                    if action_code == " ":
                        # select word
                        for v in kbdl_piy.select_word_gen():
                            yield None
                            if v == None:
                                continue
                            if len(v) > 0:
                                kbdl_txt.insert(v)
                            break
                        redraw = True
                        # select word end
                    else:
                        kbdl_piy.insert(action_code)
                elif mode == 1:
                    try: kbdl_txt.insert(action_code.upper())
                    except: kbdl_txt.insert(action_code)
                else:
                    kbdl_txt.insert(action_code)
        # draw all element
        if redraw:
            with cpu_speed_context(FAST):
                frame.fill(0)
                draw_label_header(frame, 0, 0, SW, FH, F8, WHITE, title)
                refresh = True
        for i in range(len(kbd_list)):
            if isinstance(kbd_list[i], _KBD_LINE):
                FONT = F8_MONO
            else:
                FONT = F8
            if kbd_list[i] == kbdl_txt:
                refresh |= kbdl_txt.draw(frame, 0, FH, SW, EDIT_TEXT_H, FONT, WHITE, redraw)
                continue
            base_y = SH - FH*(kbd_line_size - i)
            refresh |= kbd_list[i].draw(frame, 0, base_y, SW, FH, FONT, WHITE, redraw)
        redraw = False
        if refresh:
            with cpu_speed_context(FAST):
                hal_screen.refresh()
                refresh = False
        yield None
