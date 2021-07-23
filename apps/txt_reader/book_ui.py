from graphic import framebuf_helper, ubmfont, bmfont
from resource import font
import hal_screen

WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
SCR_W, SCR_H = hal_screen.get_size()
FNT: ubmfont.FontDrawUnicode = font.get_font_16px()
FNT_W, FNT_H = FNT.get_font_size()

def render_loading(msg="加载中", process=0.0):
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    # prograss bar 7px
    frame.fill_rect(0, 0, int((process * SCR_W) // 1), 7, WHITE)
    # text margin top 8px
    if bmfont.get_text_line(msg, SCR_W, FNT_W) == 1:
        t_width = FNT_W * len(msg)
        t_offset = (SCR_W - t_width) // 2
    else:
        t_offset = 0
    FNT.draw_on_frame(msg, frame, t_offset, 8, WHITE, SCR_W, SCR_H-8)
    hal_screen.refresh()

def render_status(battery, load_progress):
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    FNT.draw_on_frame("电量:{}%".format(battery), frame, 0, 0, WHITE, SCR_W, FNT_H)
    if load_progress < 1.0:
        FNT.draw_on_frame("加载进度:", frame, 0, FNT_H, WHITE, SCR_W, FNT_H)
        FNT.draw_on_frame("{:.3f}%".format(load_progress * 100), frame, 0, FNT_H * 2, WHITE, SCR_W, FNT_H)
    else:
        FNT.draw_on_frame("已加载完成", frame, 0, FNT_H, WHITE, SCR_W, FNT_H)
    hal_screen.refresh()
