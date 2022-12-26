import sys, os, math
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_path, "..", "lib"))
from make_unicode_bitmap_font import make_unicode_font, _get_char_data
from PIL import Image, ImageDraw
import framebuf

def main():
    block_width = 16
    block_height = 16
    font_path = os.path.join(current_path, "unifont-15.0.01.ttf")
    preview_path = os.path.join(current_path, "pix{}x{}.png".format(block_width, block_height))
    output_path = os.path.join(current_path, "pix{}x{}.ufnt".format(block_width, block_height))
    python_output_path = os.path.join(current_path, "pix{}x{}.py".format(block_width, block_height))
    external_char_dir = os.path.join(current_path, "char{}x{}".format(block_width, block_height))
    os.makedirs(external_char_dir, exist_ok=True)
    font_size = 16
    ignore_bytes = []
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
    # make fnt
    def should_ignore(char, buffer):
        frame = framebuf.FrameBuffer(buffer, block_width, block_height, framebuf.MONO_HLSB)
        filled = 0
        for x in range(block_width):
            for y in range(block_height):
                filled += frame.pixel(x, y)
        if filled >= block_width*block_height * 0.55 or filled == 0:
            print("ignored:", char)
            return True
        return False
    ignore_bytes.append(should_ignore)
    def my_get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
        byts = char_str.encode("utf8")
        if len(byts) == 1 and byts[0] >= 0x21 and byts[0] <= 0x7E:
            # ascii use external image
            fnt_img_path = os.path.join(external_char_dir, "{}.pbm".format(byts[0]))
            ascii_offset = byts[0] - 0x21
            block_size = math.ceil(block_w / 8) * block_h
            ascii_width[ascii_offset] = 8 # record ascii width, == 8
            fnt_img = Image.open(fnt_img_path)
            # draw framebuffer
            buffer = bytearray(block_size)
            frame = framebuf.FrameBuffer(buffer, block_w, block_h, framebuf.MONO_HLSB)
            for y in range(block_h):
                for x in range(8):
                    pixel = fnt_img.getpixel((x, y))
                    pixel = 1 if ((pixel == 0) ^ invert) else 0
                    frame.pixel(x, y, pixel)
            return buffer, fnt_img
        return _get_char_data(char_str, block_w, block_h, fnt, position_offset, invert)
    font_data, _, used_unicode = make_unicode_font(
        block_width, block_height, font_path, font_size, unicodes=unicodes,
        ignore_bytes=ignore_bytes, output_path=output_path, preview_path=preview_path,
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