''' layout
Box: Tuple[int, int, int, int] -> x, y, w, h
'''
from graphic.bmfont import get_text_line

ALIGN_START = 0X00
ALIGN_CENTER = 0X01
ALIGN_END = 0X02
DIRECTION_HORIZONTAL = 0X00
DIRECTION_VERTICAL = 0X01

def box_align(box_inner, box_outer, align_horizontal=ALIGN_CENTER, align_vertical=ALIGN_CENTER):
    ix, iy, iw, ih = box_inner
    ox, oy, ow, oh = box_outer
    rx = ox
    if align_horizontal == ALIGN_START:
        pass
    elif align_horizontal == ALIGN_END:
        rx += ow - iw
    else:
        rx += (ow - iw) // 2
    ry = oy
    if align_vertical == ALIGN_START:
        pass
    elif align_vertical == ALIGN_END:
        ry += oh - ih
    else:
        ry += (oh - ih) // 2
    return (rx, ry, iw, ih)

def box_padding(box, top=0, right=0, bottom=0, left=0):
    x, y, w, h = box
    x += left
    y += top
    w -= right
    h -= bottom
    w = 0 if w < 0 else w
    h = 0 if h < 0 else h
    return (x, y, w, h)

def box_max_text(box_area, font_size):
    font_w, font_h = font_size
    w, h = box_area[2:4]
    aw = w - (w % font_w)
    ah = h - (h % font_h)
    return box_align((0, 0, aw, ah), box_area, ALIGN_CENTER, ALIGN_CENTER)

def box_center_text(text, box_area, font_size):
    font_w, font_h = font_size
    area_w, area_h = box_area[2:4]
    lines = get_text_line(text, area_w, font_w)
    tw = area_w - (area_w % font_w) if lines > 1 else len(text) * font_w
    th = lines * font_h
    if th > area_h:
        return box_max_text(box_area, font_size)
    return box_align((0, 0, tw, th), box_area, ALIGN_CENTER, ALIGN_CENTER)

def box_devide(box, direction=DIRECTION_HORIZONTAL, *weight):
    x, y, w, h = box
    lst = []
    summary = sum(weight)
    priv = 0
    for wei in weight:
        if direction == DIRECTION_HORIZONTAL:
            offset = x + (w * priv // summary)
            width = (w * wei // summary)
            lst.append((offset, y, width, h))
        else:
            offset = y + (h * priv // summary)
            height = (h * wei // summary)
            lst.append((x, offset, w, height))
        priv += wei
    return lst
