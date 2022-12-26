import sys, os, math
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_path, "..", "lib"))
from make_unicode_bitmap_font import make_unicode_font, _get_char_data
from PIL import Image, ImageDraw
import framebuf

def main():
    block_width = 8
    block_height = 8
    if len(sys.argv) > 1:
        font_path = sys.argv[1]
    else:
        font_path = os.path.join(current_path, "quan.ttf")
    offset= (0, -0)
    preview_path = os.path.join(current_path, "pix{}x{}.png".format(block_width, block_height))
    output_path = os.path.join(current_path, "pix{}x{}.ufnt".format(block_width, block_height))
    python_output_path = os.path.join(current_path, "pix{}x{}.py".format(block_width, block_height))
    font_size = 8
    ignore_bytes = []
    ignore_bytes.append(bytearray(8))
    unicodes = []
    unicodes.extend(c for c in range(0x20, 0x7E+1)) # ascii some
    unicodes.extend(c for c in range(0x0080, 0x024F+1)) # latin
    unicodes.extend(c for c in range(0x2000, 0x206F+1)) # general punctuation
    unicodes.extend(c for c in range(0x20A0, 0x20CF+1)) # currency symbols
    unicodes.extend(c for c in range(0x2100, 0x21FF+1)) # symbols
    unicodes.extend(c for c in range(0x2200, 0x22FF+1)) # math symbols
    unicodes.extend(c for c in range(0x3000, 0x303F+1)) # cjk symbols and punctuation
    unicodes.extend(c for c in range(0x3040, 0x30FF+1)) # jp
    unicodes.extend(c for c in range(0x4E00, 0x9FFF+1)) # cjk general
    unicodes.extend(c for c in range(0xFF00, 0xFFEF+1)) # full ascii
    ascii_width = bytearray(0x7E+1 - 0x21) # 0x20 ascii space
    def my_get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
        byts = char_str.encode("utf8")
        if len(byts) == 1 and byts[0] >= 0x21 and byts[0] <= 0x7E:
            ascii_offset = byts[0] - 0x21
            block_size = math.ceil(block_w / 8) * block_h
            char_left, char_top, char_right, char_bottom = fnt.getbbox(char_str)
            char_width = char_right - char_left
            ascii_width[ascii_offset] = char_width # record ascii width
            # print("ch", char_str, "width", char_width, "offset", ascii_offset)
            char_x_offset = char_left
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
            frame = framebuf.FrameBuffer(buffer, block_w, block_h, framebuf.MONO_HLSB)
            for y in range(block_h):
                for x in range(block_w):
                    pixel = fnt_img.getpixel((x, y))
                    pixel = 1 if ((pixel == 0) ^ invert) else 0
                    frame.pixel(x, y, pixel)
            return buffer, fnt_img
        return _get_char_data(char_str, block_w, block_h, fnt, position_offset, invert)
    font_data, _, used_unicode = make_unicode_font(
        block_width, block_height, font_path, font_size, unicodes=unicodes,
        position_offset=offset, ignore_bytes=ignore_bytes,
        output_path=output_path, preview_path=preview_path,
        get_char_data=my_get_char_data
    )
    with open(python_output_path, "wt") as f:
        f.write("data=")
        f.write(repr(bytes(font_data)))
        f.write("\n")
        f.write("width_data=")
        f.write(repr(bytes(ascii_width)))
        f.write("\n")
    print("real font count:", len(used_unicode))

if __name__ == "__main__":
    main()