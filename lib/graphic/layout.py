''' layout
Box: Tuple[int, int, int, int] -> x, y, w, h
'''
from graphic.bmfont import get_text_line
from hal_screen import get_format
from graphic.framebuf_helper import get_white_color

ALIGN_START = 0X00
ALIGN_CENTER = 0X01
ALIGN_END = 0X02
DIRECTION_HORIZONTAL = 0X00
DIRECTION_VERTICAL = 0X01

EMPTY_BOX = (0, 0, 0, 0)

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

def box_max_text(box_area, font_size, align_horizontal=ALIGN_CENTER, align_vertical=ALIGN_CENTER):
    font_w, font_h = font_size
    w, h = box_area[2:4]
    aw = w - (w % font_w)
    ah = h - (h % font_h)
    return box_align((0, 0, aw, ah), box_area, align_horizontal, align_vertical)

def box_align_text(text, box_area, font_size, multi_lines=True, align_horizontal=ALIGN_CENTER, align_vertical=ALIGN_CENTER):
    font_w, font_h = font_size
    area_w, area_h = box_area[2:4]
    if multi_lines:
        lines = get_text_line(text, area_w, font_w)
        tw = area_w - (area_w % font_w) if lines > 1 else len(text) * font_w
        th = lines * font_h
    else:
        text_width = len(text) * font_w
        tw = area_w - (area_w % font_w) if text_width > area_w else text_width
        th = font_h
    if th > area_h:
        return box_max_text(box_area, font_size, align_horizontal, align_vertical)
    return box_align((0, 0, tw, th), box_area, align_horizontal, align_vertical)

def box_devide(box, direction, *weight):
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

def config_to_bool(value, str_true_value=["true", "1", "yes"]):
    if type(value) == bool:
        return value
    elif type(value) == str:
        v = value.lower()
        if v in str_true_value:
            return True
        else:
            return False
    return bool(value)

def config_to_int(value, str_int_value=[]):
    if type(value) == int:
        return value
    elif type(value) == str:
        v = value.lower()
        if v in str_int_value:
            return str_int_value.index(v)
        try:
            return int(value)
        except:
            return 0
    else:
        return int(value)

def config_to_box(value):
    if type(value) == tuple:
        return tuple(value[0:4])
    elif type(value) == str:
        try:
            v:str = value.split(",")
            lst = []
            for i in range(4):
                lst.append(int(v[i].strip()))
            return tuple(lst)
        except:
            return EMPTY_BOX
    else:
        return EMPTY_BOX

def config_to_align(value):
    if type(value) == tuple:
        return tuple(value[0:2])
    elif type(value) == str:
        try:
            v:str = value.split(",")
            lst = []
            for i in range(2):
                v = v[i].strip()
                lst.append(config_to_int(v, ["start", "center", "end"]))
            return tuple(lst)
        except:
            return (ALIGN_CENTER, ALIGN_CENTER)
    else:
        return (ALIGN_CENTER, ALIGN_CENTER)

def config_to_list(value: str, sep=",", cast_method=config_to_int):
    if type(value) == list:
        return list(value[0:2])
    elif type(value) == str:
        try:
            lst = []
            for v in value.split(sep):
                lst.append(cast_method(v))
            return lst
        except:
            return []
    else:
        return []

def config_to_direction(value):
    return config_to_int(value, ["horizontal", "vertical"])

def config_to_color(value):
    if type(value) == int:
        return value
    elif type(value) == str:
        v = value.lower()
        if v == "black":
            return 0
        elif v == "none":
            return None
        elif v == "white":
            return get_white_color(get_format())
        try:
            return int(value)
        except:
            return 0
    else:
        return int(value)
