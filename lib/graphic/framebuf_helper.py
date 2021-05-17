from framebuf import RGB565, MONO_VLSB, MONO_HMSB, MONO_HLSB
import framebuf
import micropython

@micropython.viper
def color565(r:int, g:int, b:int) -> int:
    """Return RGB565 color value.

    Args:
        r (int): Red value.
        g (int): Green value.
        b (int): Blue value.
    """
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

@micropython.viper
def __copy_with_color(get_pixel, set_pixel, size, color:int):
    w = int(size[0])
    h = int(size[1])
    for x in range(w):
        for y in range(h):
            sc:int = int(get_pixel(x, y))
            tc:int = color if sc > 0 else 0
            set_pixel(x, y, tc)

def ensure_same_format(source_frame, source_format, w, h, target_format, target_color=0xFFFF):
    if source_format != target_format:
        # todo: change == to != ^upper^
        if target_format == RGB565:
            target_frame = framebuf.FrameBuffer(bytearray(w*h*2), w, h, target_format)
        elif target_format == MONO_VLSB:
            yp = h // 8
            yp += 1 if h % 8 > 0 else 0
            target_frame = framebuf.FrameBuffer(bytearray(w*yp), w, h, target_format)
        elif target_format == MONO_HLSB or target_format == MONO_HMSB:
            xp = w // 8
            xp += 1 if w % 8 > 0 else 0
            target_frame = framebuf.FrameBuffer(bytearray(xp*h), w, h, target_format)
        else:
            return source_frame
        __copy_with_color(source_frame.pixel, target_frame.pixel, (w, h), target_color)
        return target_frame
    return source_frame

def get_white_color(frame_format):
    if frame_format == RGB565:
        return 0xFFFF
    elif frame_format == MONO_VLSB or frame_format == MONO_HMSB or frame_format == MONO_HLSB:
        return 1
    return 0xFF
