import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from buildin_resource.font import get_font_8px
from ui.utils import PagedText, draw_buttons_at_last_line, draw_label_header, sleep_save_power
from play32hw.cpu import cpu_speed_context, VERY_SLOW, FAST

def dialog(text="", title="", text_yes="OK", text_no="OK"):
    """ show a dialog and display some text.
        return True/False
    """
    with cpu_speed_context(VERY_SLOW):
        for v in dialog_gen(text, title, text_yes, text_no):
            if v != None:
                return v
            sleep_save_power() # save power

def dialog_gen(text="", title="", text_yes="OK", text_no="OK"):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    TITLE_H = FH if title else 0
    TEXT_H = SH - FH - TITLE_H
    if isinstance(text, str):
        paged_text = PagedText(text, F8, SW, TEXT_H,)
    else:
        paged_text = None
    redraw = True
    while True:
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A or ekey == KEY_B:
                yield ekey == KEY_A
            if ekey == KEY_LEFT or ekey == KEY_UP:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_RIGHT or ekey == KEY_DOWN:
                paged_text.page_down()
                redraw = True
        if redraw:
            with cpu_speed_context(FAST):
                frame = hal_screen.get_framebuffer()
                frame.fill(0)
                # draw title
                if TITLE_H > 0:
                    draw_label_header(frame, 0, 0, SW, TITLE_H, F8, WHITE, title)
                # draw text
                if callable(text):
                    text(frame, 0, TITLE_H, SW, TEXT_H, F8, WHITE)
                else:
                    paged_text.draw(frame, 0, TITLE_H, SW, TEXT_H, F8, WHITE)
                # draw button
                draw_buttons_at_last_line(frame, SW, SH, F8, WHITE, text_yes, text_no)
                redraw = False
                hal_screen.refresh()
        yield None
