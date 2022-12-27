import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from graphic.bmfont import get_text_width
from buildin_resource.font import get_font_8px
from ui.utils import draw_buttons_at_last_line, draw_label_header, sleep_save_power

def input_slide(title="", text_yes="OK", text_no="CANCEL", slide_start = 0, slide_size = 100):
    """ show a dialog and display some text.
        return True/False
    """
    for v in input_slide_gen(title, text_yes, text_no, slide_start, slide_size):
        if v != None:
            return v
        sleep_save_power() # save power

def input_slide_gen(title="", text_yes="OK", text_no="CANCEL", slide_start = 0, slide_size = 100):
    assert slide_start >= 0
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    TITLE_H = FH if title else 0
    H_SLIDE_H = (SH - FH - TITLE_H) // 2
    SLIDE_W = SW - FW - FW
    value = slide_start
    redraw = True
    while True:
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A or ekey == KEY_B:
                yield value if ekey == KEY_A else -1 - value
            if ekey == KEY_UP or ekey == KEY_DOWN:
                value += int(slide_size * 0.1) if ekey == KEY_UP else -int(slide_size * 0.1)
                value = max(slide_start, value)
                value = min(slide_start + slide_size, value)
                redraw = True
            if ekey == KEY_LEFT or ekey == KEY_RIGHT:
                value += 1 if ekey == KEY_RIGHT else -1
                value = max(slide_start, value)
                value = min(slide_start + slide_size, value)
                redraw = True
        if redraw:
            frame = hal_screen.get_framebuffer()
            frame.fill(0)
            # draw title
            if TITLE_H > 0:
                draw_label_header(frame, 0, 0, SW, TITLE_H, F8, WHITE, title)
            # draw slide text
            t = str(value)
            tw = get_text_width(t, F8)
            offset_x = (SW - tw) // 2
            offset_y = ((H_SLIDE_H - FH) // 2) + TITLE_H
            F8.draw_on_frame(t, frame, offset_x, offset_y, WHITE, SW, FH)
            # draw slide
            offset_y = ((H_SLIDE_H - FH) // 2) + H_SLIDE_H + TITLE_H
            ava_w = SLIDE_W - 4
            bar_w = int(ava_w * (value / slide_size))
            bar_w = min(ava_w, bar_w)
            bar_w = max(1, bar_w)
            frame.rect(FW, offset_y, SLIDE_W, FH, WHITE)
            frame.fill_rect(FW + 2, offset_y + 2, bar_w, FH - 4, WHITE)
            # draw button
            draw_buttons_at_last_line(frame, SW, SH, F8, WHITE, text_yes, text_no)
            redraw = False
            hal_screen.refresh()
        yield None
