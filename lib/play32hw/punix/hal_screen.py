import framebuf, usys
from play32hw.punix.usdl2 import SDL_Init, SDL_INIT_VIDEO, SDL_WINDOWPOS_CENTERED, SDL_RENDERER_SOFTWARE, SDL_WINDOW_FULLSCREEN_DESKTOP, SDL_Quit
from play32hw.punix.usdl2 import SDL_CreateWindow, SDL_CreateRenderer, SDL_RenderSetLogicalSize, SDL_RenderSetIntegerScale, SDL_DestroyWindow, SDL_DestroyRenderer
from play32hw.punix.usdl2 import SDL_SetRenderDrawColor, SDL_RenderFillRect, SDL_RenderFillRects, SDL_RenderPresent
from play32hw.punix.usdl2 import SDL_TRUE, SDL_Rect

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
PIXEL_SIZE = 8
PIXEL_GAP = 1

_frame = None
_window = 0
_renderer = 0

def init():
    global _frame, _window, _renderer, PIXEL_SIZE, PIXEL_GAP
    if _frame != None:
        return
    screen_flag = 0
    argv = usys.argv # type: list[str]
    for opt in argv:
        if opt == "-Ofullscreen":
            screen_flag = screen_flag | SDL_WINDOW_FULLSCREEN_DESKTOP
        elif opt.startswith("-Opixelsize"):
            size = int(opt[len("-Opixelsize"):])
            if size >= 1 and size <= 16:
                PIXEL_SIZE = size
        elif opt.startswith("-Opixelgap"):
            size = int(opt[len("-Opixelgap"):])
            if size >= 0 and size <= 4:
                PIXEL_GAP = size
    _frame = framebuf.FrameBuffer(bytearray(SCREEN_WIDTH*SCREEN_HEIGHT//8), SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.MONO_HLSB)
    SDL_Init(SDL_INIT_VIDEO)
    _window = SDL_CreateWindow("Play32 UNIX",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        SCREEN_WIDTH * PIXEL_SIZE, SCREEN_HEIGHT * PIXEL_SIZE,
        screen_flag)
    _renderer = SDL_CreateRenderer(_window, -1, SDL_RENDERER_SOFTWARE)
    SDL_RenderSetLogicalSize(_renderer, SCREEN_WIDTH * PIXEL_SIZE, SCREEN_HEIGHT * PIXEL_SIZE)
    SDL_RenderSetIntegerScale(_renderer, SDL_TRUE)

def deinit():
    global _frame, _window, _renderer
    if _frame == None:
        return
    SDL_DestroyRenderer(_renderer)
    _renderer = 0
    SDL_DestroyWindow(_window)
    _window = 0
    SDL_Quit()
    _frame = None

def get_size():
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_format():
    return framebuf.MONO_HLSB

def get_framebuffer() -> framebuf.FrameBuffer:
    return _frame

def refresh(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT):
    if _frame == None:
        return
    rects = bytearray()
    rects_count = 0
    SDL_SetRenderDrawColor(_renderer, 0, 0, 0, 255)
    SDL_RenderFillRect(_renderer, SDL_Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, w * PIXEL_SIZE, h * PIXEL_SIZE))
    for iy in range(h):
        for ix in range(w):
            px = x + ix
            py = y + iy
            if _frame.pixel(px, py) > 0:
                rects.extend(SDL_Rect(px * PIXEL_SIZE, py * PIXEL_SIZE, PIXEL_SIZE - PIXEL_GAP, PIXEL_SIZE  - PIXEL_GAP))
                rects_count += 1
    if rects_count > 0:
        SDL_SetRenderDrawColor(_renderer, 255, 255, 255, 255)
        SDL_RenderFillRects(_renderer, rects, rects_count)
    SDL_RenderPresent(_renderer)