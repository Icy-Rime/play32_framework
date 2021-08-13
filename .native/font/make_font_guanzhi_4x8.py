import sys, os
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_path, "..", "lib"))
from make_unicode_bitmap_font import make_unicode_font
from PIL import Image, ImageFont, ImageDraw
import math
import coding, framebuf

def _get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
    block_size = math.ceil(block_h / 8) * block_w
    char_left, char_top, char_right, char_bottom = fnt.getbbox(char_str)
    char_width = char_right - char_left
    char_height = char_bottom - char_top
    char_x_offset = (block_w - char_width) // 2
    char_y_offset = char_top
    char_offset = (position_offset[0] + char_x_offset, position_offset[1] + char_y_offset)
    # draw char
    fnt_img = Image.new("1", (block_w, block_h), color=255)
    fnt_draw = ImageDraw.Draw(fnt_img)
    try:
        fnt_draw.text(char_offset, char_str, fill=0, font=fnt, anchor="lt", spacing=0)
    except: pass
    # draw framebuffer
    buffer = bytearray(block_size)
    frame = framebuf.FrameBuffer(buffer, block_w, block_h, framebuf.MONO_VLSB)
    for y in range(block_h):
        for x in range(block_w):
            pixel = fnt_img.getpixel((x, y))
            pixel = 1 if ((pixel == 0) ^ invert) else 0
            frame.pixel(x, y, pixel)
    # print(frame)
    # fnt_img.save('l.png')
    return buffer, fnt_img

def main():
    block_width = 4
    block_height = 8
    if len(sys.argv) > 1:
        font_path = sys.argv[1]
    else:
        font_path = os.path.join(current_path, "guanzhi.ttf")
    offset= (0, -1)
    font_size = 8
    font = ImageFont.truetype(font_path, size=font_size)
    ignore_bytes = []
    ignore_bytes.append(bytearray(8))
    unicodes = []
    # unicodes.append(0x20) # space ignore
    unicodes.extend(c for c in range(0x21, 0x7E+1))
    buffer = bytearray()
    for unic in unicodes:
        char = coding.UTF8.to_bytes(unic).decode("utf8")
        data, img = _get_char_data(char, block_width, block_height, font, offset)
        buffer.extend(data)
    print(str(buffer))

if __name__ == "__main__":
    main()