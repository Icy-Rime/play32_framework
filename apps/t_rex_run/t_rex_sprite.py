import framebuf, hal_screen
from graphic import pbm, framebuf_helper
import gc
SCREEN_FORMAT = hal_screen.get_format()
SPRIT_FORMAT = framebuf.MONO_HLSB
COLOR_WHITE = framebuf_helper.get_white_color(SCREEN_FORMAT)

def get_color_or_white(r, g, b):
    if SCREEN_FORMAT == framebuf.RGB565:
        return framebuf_helper.color565(r, g, b)
    return COLOR_WHITE

class Sprite():
    def __init__(self, box=(0, 0, 0, 0), img=None, key=None):
        self.box = box
        self.img = img
        self.key = key
    def move(self, offset_x, offset_y):
        x, y, w, h = self.box
        self.box = x+offset_x, y+offset_y, w, h
    def move_to(self, x, y):
        _x, _y, w, h = self.box
        self.box = x, y, w, h
    def draw(self, frame):
        x, y, w, h = self.box
        img = self.img
        key = self.key
        if img != None:
            if key != None:
                frame.blit(img, int(x), int(y), key)
            else:
                frame.blit(img, int(x), int(y))
    def clone(self):
        x, y, w, h = self.box
        return Sprite((x, y, w, h), self.img, self.key)

def is_sprite_collide(s1, s2):
    # type: (Sprite, Sprite) -> bool
    x1, y1, w1, h1 = s1.box
    x2, y2, w2, h2 = s2.box
    x1 = int(x1)
    y1 = int(y1)
    w1 = int(w1)
    h1 = int(h1)
    x2 = int(x2)
    y2 = int(y2)
    w2 = int(w2)
    h2 = int(h2)
    startx = max(x1, x2)
    endx = min(x1 + w1, x2 + w2)
    starty = max(y1, y2)
    endy = min(y1 + h1, y2 + h2)
    if startx >= endx or starty >= endy:
        return False
    w = endx - startx
    h = endy - starty
    pixel1 = s1.img.pixel
    key1 = s1.key
    pixel2 = s2.img.pixel
    key2 = s2.key
    for xi in range(w):
        for yi in range(h):
            x = startx + xi
            y = starty + yi
            c1 = pixel1(x - x1, y - y1)
            c2 = pixel2(x - x2, y - y2)
            if c1 == key1 or c2 == key2:
                continue
            return True
    return False

def load_sprite(img_path, color=COLOR_WHITE):
    with open(img_path, "rb") as in_stream:
        w, h, format, data, comment = pbm.read_image(in_stream)
    img = framebuf.FrameBuffer(data, w, h, SPRIT_FORMAT)
    img = framebuf_helper.ensure_same_format(img, SPRIT_FORMAT, w, h, SCREEN_FORMAT, color)
    gc.collect()
    return Sprite((0, 0, w, h), img)

def new_sprite(w, h):
    wp = w // 8
    wp += 0 if w % 8 == 0 else 1
    img = framebuf.FrameBuffer(bytearray(wp * h), w, h, SPRIT_FORMAT)
    img = framebuf_helper.ensure_same_format(img, SPRIT_FORMAT, w, h, SCREEN_FORMAT, COLOR_WHITE)
    gc.collect()
    return Sprite((0, 0, w, h), img)
