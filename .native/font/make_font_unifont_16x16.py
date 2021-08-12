import sys, os
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_path, "..", "lib"))
from make_unicode_bitmap_font import make_unicode_font, _get_char_data
from PIL import ImageFont
import framebuf

def main():
    block_width = 16
    block_height = 16
    font_path = os.path.join(current_path, "unifont-13.0.04.ttf")
    preview_path = os.path.join(current_path, "pix{}x{}.png".format(block_width, block_height))
    output_path = os.path.join(current_path, "pix{}x{}.ufnt".format(block_width, block_height))
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
    # unicodes.extend(c for c in range(0x0000, 0xFFFF+1)) # full
    # make fnt
    try:
        backup_font_path = os.path.join(current_path, "SourceHanSansSC-VF.ttf")
        backup_fnt = ImageFont.truetype(backup_font_path, size=font_size)
        def should_ignore(char, buffer):
            frame = framebuf.FrameBuffer(buffer, block_width, block_height, framebuf.MONO_HLSB)
            filled = 0
            for x in range(block_width):
                for y in range(block_height):
                    filled += frame.pixel(x, y)
            if filled >= block_width*block_height * 0.55:
                print("ignored:", char)
                return True
            return False
        ignore_bytes.append(should_ignore)
        def my_get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
            byts = char_str.encode("utf8")
            if len(byts) == 1 and byts[0] >= 0x20 and byts[0] <= 0x7E:
                # ascii use a different font
                if char_str in "/{[]}:;\\":
                    position_offset = (0, -3)
                elif char_str in "@Q":
                    position_offset = (0, -4)
                elif char_str in "gpqy":
                    position_offset = (0, -6)
                else:
                    position_offset = (0, -2)
                return _get_char_data(char_str, block_w, block_h, backup_fnt, position_offset, invert)
            return _get_char_data(char_str, block_w, block_h, fnt, position_offset, invert)
        make_unicode_font(
            block_width, block_height, font_path, font_size, unicodes=unicodes,
            ignore_bytes=ignore_bytes, output_path=output_path, preview_path=preview_path,
            get_char_data=my_get_char_data
        )
    except:
        make_unicode_font(
            block_width, block_height, font_path, font_size, unicodes=unicodes,
            ignore_bytes=ignore_bytes, output_path=output_path, preview_path=preview_path,
        )

if __name__ == "__main__":
    main()