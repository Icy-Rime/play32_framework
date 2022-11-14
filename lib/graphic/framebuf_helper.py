from framebuf import RGB565, MONO_VLSB, MONO_HMSB, MONO_HLSB
from uctypes import NATIVE, UINT8, UINT16, UINT32, struct
import framebuf
import micropython

RAW_PTR = UINT32 # bytes

FRAMEBUFFER_OBJECT = {
    "base": (0 | RAW_PTR),
    "buf_obj": (4 | RAW_PTR),
    "buf": (8 | RAW_PTR),
    "width": (12 | UINT16),
    "height": (14 | UINT16),
    "stride": (16 | UINT16),
    "format": (18 | UINT8),
}

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

@micropython.viper
def __copy(get_pixel, set_pixel, w:int, h:int):
    for x in range(w):
        for y in range(h):
            sc:int = int(get_pixel(x, y))
            set_pixel(x, y, sc)

def ensure_same_format(source_frame, source_format, w, h, target_format, target_color=0xFFFF):
    if source_format != target_format:
        target_frame = new_framebuffer(w, h, target_format)
        __copy_with_color(source_frame.pixel, target_frame.pixel, (w, h), target_color)
        return target_frame
    return source_frame

def get_white_color(frame_format):
    if frame_format == RGB565:
        return 0xFFFF
    elif frame_format == MONO_VLSB or frame_format == MONO_HMSB or frame_format == MONO_HLSB:
        return 1
    return 0xFF

def new_framebuffer(w, h, frame_format):
    if frame_format == RGB565:
        return framebuf.FrameBuffer(bytearray(w*h*2), w, h, frame_format)
    elif frame_format == MONO_VLSB:
        yp = h // 8
        yp += 1 if h % 8 > 0 else 0
        return framebuf.FrameBuffer(bytearray(w*yp), w, h, frame_format)
    elif frame_format == MONO_HLSB or frame_format == MONO_HMSB:
        xp = w // 8
        xp += 1 if w % 8 > 0 else 0
        return framebuf.FrameBuffer(bytearray(xp*h), w, h, frame_format)

def clone_framebuffer(frame, w, h, format):
    target_frame = new_framebuffer(w, h, format)
    __copy(frame.pixel, target_frame.pixel, w, h)
    return target_frame

def crop_framebuffer(frame, x, y, w, h, format):
    new_frame = new_framebuffer(w, h, format)
    new_frame.blit(frame, -x, -y)
    return new_frame

def get_framebuffer_info(frame):
    assert type(frame) == framebuf.FrameBuffer
    frame_address = id(frame)
    stru_frame = struct(frame_address, FRAMEBUFFER_OBJECT, NATIVE)
    return stru_frame.width, stru_frame.height, stru_frame.format, stru_frame.stride
