import sys, os
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_path, "..", "lib"))
from make_unicode_bitmap_font import make_unicode_font, _get_char_data
from PIL import Image
import framebuf, coding

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
    # unicodes.extend(c for c in range(0x0000, 0xFFFF+1)) # full
    # for char_area_pose in coding.GB2312.all_available_pos():
    #     char = coding.GB2312.to_bytes(char_area_pose).decode('gb2312')
    #     unic = coding.UTF8.from_bytes(char.encode("utf8"))
    #     unicodes.append(unic)
    font_petme128_8x8 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00OO\x00\x00\x00\x00\x07\x07\x00\x00\x07\x07\x00\x14\x7f\x7f\x14\x14\x7f\x7f\x14\x00$.kk:\x12\x00\x00c3\x18\x0cfc\x00\x002\x7fMMwrP\x00\x00\x00\x04\x06\x03\x01\x00\x00\x00\x1c>cA\x00\x00\x00\x00Ac>\x1c\x00\x00\x08*>\x1c\x1c>*\x08\x00\x08\x08>>\x08\x08\x00\x00\x00\x80\xe0`\x00\x00\x00\x00\x08\x08\x08\x08\x08\x08\x00\x00\x00\x00``\x00\x00\x00\x00@`0\x18\x0c\x06\x02\x00>\x7fIE\x7f>\x00\x00@D\x7f\x7f@@\x00\x00bsQIOF\x00\x00"cII\x7f6\x00\x00\x18\x18\x14\x16\x7f\x7f\x10\x00\'gEE}9\x00\x00>\x7fII{2\x00\x00\x03\x03y}\x07\x03\x00\x006\x7fII\x7f6\x00\x00&oII\x7f>\x00\x00\x00\x00$$\x00\x00\x00\x00\x00\x80\xe4d\x00\x00\x00\x00\x08\x1c6cAA\x00\x00\x14\x14\x14\x14\x14\x14\x00\x00AAc6\x1c\x08\x00\x00\x02\x03QY\x0f\x06\x00\x00>\x7fAMO.\x00\x00|~\x0b\x0b~|\x00\x00\x7f\x7fII\x7f6\x00\x00>\x7fAAc"\x00\x00\x7f\x7fAc>\x1c\x00\x00\x7f\x7fIIAA\x00\x00\x7f\x7f\t\t\x01\x01\x00\x00>\x7fAI{:\x00\x00\x7f\x7f\x08\x08\x7f\x7f\x00\x00\x00A\x7f\x7fA\x00\x00\x00 `A\x7f?\x01\x00\x00\x7f\x7f\x1c6cA\x00\x00\x7f\x7f@@@@\x00\x00\x7f\x7f\x06\x0c\x06\x7f\x7f\x00\x7f\x7f\x0e\x1c\x7f\x7f\x00\x00>\x7fAA\x7f>\x00\x00\x7f\x7f\t\t\x0f\x06\x00\x00\x1e?!a\x7f^\x00\x00\x7f\x7f\x199oF\x00\x00&oII{2\x00\x00\x01\x01\x7f\x7f\x01\x01\x00\x00?\x7f@@\x7f?\x00\x00\x1f?``?\x1f\x00\x00\x7f\x7f0\x180\x7f\x7f\x00cw\x1c\x1cwc\x00\x00\x07\x0fxx\x0f\x07\x00\x00aqYMGC\x00\x00\x00\x7f\x7fAA\x00\x00\x00\x02\x06\x0c\x180`@\x00\x00AA\x7f\x7f\x00\x00\x00\x08\x0c\x06\x06\x0c\x08\x00\xc0\xc0\xc0\xc0\xc0\xc0\xc0\xc0\x00\x00\x01\x03\x06\x04\x00\x00\x00 tTT|x\x00\x00\x7f\x7fDD|8\x00\x008|DDl(\x00\x008|DD\x7f\x7f\x00\x008|TT\\X\x00\x00\x08~\x7f\t\x03\x02\x00\x00\x98\xbc\xa4\xa4\xfc|\x00\x00\x7f\x7f\x04\x04|x\x00\x00\x00\x00}}\x00\x00\x00\x00@\xc0\x80\x80\xfd}\x00\x00\x7f\x7f08lD\x00\x00\x00A\x7f\x7f@\x00\x00\x00||\x180\x18||\x00||\x04\x04|x\x00\x008|DD|8\x00\x00\xfc\xfc$$<\x18\x00\x00\x18<$$\xfc\xfc\x00\x00||\x04\x04\x0c\x08\x00\x00H\\TTt \x00\x04\x04?\x7fDd \x00\x00<|@@|<\x00\x00\x1c<``<\x1c\x00\x00\x1c|0\x180|\x1c\x00Dl88lD\x00\x00\x9c\xbc\xa0\xa0\xfc|\x00\x00Ddt\\LD\x00\x00\x08\x08>wAA\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00AAw>\x08\x08\x00\x00\x02\x03\x01\x03\x02\x03\x01\xaaU\xaaU\xaaU\xaaU'
    def my_get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
        byts = char_str.encode("utf8")
        if len(byts) == 1 and byts[0] >= 0x20 and byts[0] <= 0x7E:
            # ascii use a different font
            chr_data_offset = (byts[0] - 32) * 8
            char_frame = framebuf.FrameBuffer(font_petme128_8x8[chr_data_offset: chr_data_offset+8], 8, 8, framebuf.MONO_VLSB)
            buffer = bytearray(8)
            target_frame = framebuf.FrameBuffer(buffer, 8, 8, framebuf.MONO_HLSB)
            fnt_img = Image.new("1", (8, 8), color=255)
            for y in range(8):
                for x in range(8):
                    pixel = char_frame.pixel(x, y)
                    target_frame.pixel(x, y, pixel)
                    fnt_img.putpixel((x, y), 255 if pixel == 0 else 0)
            return buffer, fnt_img
        return _get_char_data(char_str, block_w, block_h, fnt, position_offset, invert)
    _, _, used_unicode = make_unicode_font(
        block_width, block_height, font_path, font_size, unicodes=unicodes,
        position_offset=offset, ignore_bytes=ignore_bytes,
        output_path=output_path, preview_path=preview_path,
        get_char_data=my_get_char_data
    )
    print("real font count:", len(used_unicode))
    # print(used_unicode)

if __name__ == "__main__":
    main()