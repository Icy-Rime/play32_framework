import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from buildin_resource.font import get_font_8px
from ui.utils import PagedText, draw_buttons_at_last_line, draw_label_nav, draw_label_header, sleep_save_power

def select_menu(text="", title="", options=[], text_yes="OK", text_no="CANCEL"):
    """ show a menu and display some text.
        select_menu has a big area to display text, it is suitable for explaining your options.
    """
    for v in select_menu_gen(text, title, options, text_yes, text_no):
        if v != None:
            return v
        sleep_save_power() # save power

def select_menu_gen(text="", title="", options=[], text_yes="OK", text_no="CANCEL"):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    TITLE_H = FH if title else 0
    TEXT_H = SH - FH - FH - TITLE_H
    OP_SIZE = len(options)
    if isinstance(text, str):
        paged_text = PagedText(text, F8, SW, TEXT_H)
    else:
        paged_text = None
    pointer = 0
    redraw = True
    while True:
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A or ekey == KEY_B:
                yield pointer if ekey == KEY_A and OP_SIZE > 0 else -1 - pointer
            if ekey == KEY_UP:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_DOWN:
                paged_text.page_down()
                redraw = True
            if OP_SIZE > 0 and ekey == KEY_LEFT:
                pointer -= 1
                pointer %= OP_SIZE
                redraw = True
            if OP_SIZE > 0 and ekey == KEY_RIGHT:
                pointer += 1
                pointer %= OP_SIZE
                redraw = True
        if redraw:
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
            # draw options
            if OP_SIZE > 0:
                draw_label_nav(frame, 0, TEXT_H + TITLE_H, SW, FH, F8, WHITE, options[pointer])
            # draw button
            draw_buttons_at_last_line(frame, SW, SH, F8, WHITE, text_yes, text_no)
            redraw = False
            hal_screen.refresh()
        yield None

def select_list(title="", options=[], text_yes="OK", text_no="CANCEL"):
    """ show a menu and display some text.
        select_menu has a big area to display text, it is suitable for explaining your options.
    """
    for v in select_list_gen(title, options, text_yes, text_no):
        if v != None:
            return v
        sleep_save_power() # save power

def select_list_gen(title="", options=[], text_yes="OK", text_no="CANCEL"):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    OP_SIZE = len(options)
    SCROLL_BAR_W = 4 if OP_SIZE > 1 else 0
    LIST_AREA_W = SW - SCROLL_BAR_W
    LIST_AREA_H = SH - FH - FH
    LIST_PAGE_SIZE = LIST_AREA_H // FH
    LIST_OFFSET_X = (LIST_AREA_W % FW) // 2
    if OP_SIZE > 0:
        paged_text = PagedText(options[0], F8, LIST_AREA_W, FH, style_inline=True)
    else:
        paged_text = PagedText("", F8, LIST_AREA_W, FH, style_inline=True)
    pointer = 0
    redraw = True
    while True:
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A or ekey == KEY_B:
                yield pointer if ekey == KEY_A and OP_SIZE > 0 else -1 - pointer
            if ekey == KEY_LEFT:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_RIGHT:
                paged_text.page_down()
                redraw = True
            if OP_SIZE > 0 and (ekey == KEY_UP or ekey == KEY_DOWN):
                pointer += 1 if ekey == KEY_DOWN else -1
                pointer %= OP_SIZE
                paged_text = PagedText(options[pointer], F8, LIST_AREA_W, FH, style_inline=True)
                redraw = True
        if redraw:
            frame = hal_screen.get_framebuffer()
            frame.fill(0)
            # draw title
            draw_label_header(frame, 0, 0, SW, FH, F8, WHITE, title)
            # draw options
            page = pointer // LIST_PAGE_SIZE
            for i in range(OP_SIZE):
                if i // LIST_PAGE_SIZE != page:
                    continue
                offset_y = FH + FH * (i % LIST_PAGE_SIZE)
                if i == pointer:
                    frame.rect(0, offset_y, LIST_AREA_W, FH, WHITE, True)
                    paged_text.draw(frame, 0, offset_y, LIST_AREA_W, FH, F8, 0)
                else:
                    F8.draw_on_frame(options[i], frame, LIST_OFFSET_X, offset_y, WHITE, LIST_AREA_W, FH)
            # draw scroll bar
            if SCROLL_BAR_W > 0:
                area_h = LIST_AREA_H - 4
                scroll_h = max(int(area_h / OP_SIZE), 1)
                scroll_start = int(pointer * area_h / OP_SIZE)
                frame.rect(SW - 3, FH + scroll_start + 2, 2, scroll_h, WHITE, True)
                frame.hline(SW - 4, FH, 4, WHITE)
                frame.hline(SW - 4, FH + LIST_AREA_H - 1, 4, WHITE)
            # draw button
            draw_buttons_at_last_line(frame, SW, SH, F8, WHITE, text_yes, text_no)
            redraw = False
            hal_screen.refresh()
        yield None
