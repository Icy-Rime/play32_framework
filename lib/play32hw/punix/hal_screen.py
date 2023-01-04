import framebuf
from play32hw.punix.usdl2 import SDL_Init, SDL_INIT_VIDEO, SDL_WINDOWPOS_CENTERED, SDL_Quit
from play32hw.punix.usdl2 import SDL_CreateWindow, SDL_CreateRenderer, SDL_RenderSetIntegerScale, SDL_DestroyWindow, SDL_DestroyRenderer
from play32hw.punix.usdl2 import SDL_SetRenderDrawColor, SDL_RenderFillRect, SDL_RenderFillRects, SDL_RenderPresent
from play32hw.punix.usdl2 import SDL_TRUE, SDL_Rect

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
PIXEL_SIZE = 8

_frame = None
_window = 0
_renderer = 0

def init():
    global _frame, _window, _renderer
    if _frame != None:
        return
    _frame = framebuf.FrameBuffer(bytearray(SCREEN_WIDTH*SCREEN_HEIGHT//8), SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.MONO_HLSB)
    SDL_Init(SDL_INIT_VIDEO)
    _window = SDL_CreateWindow("Hello World", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, SCREEN_WIDTH * PIXEL_SIZE, SCREEN_HEIGHT * PIXEL_SIZE, 0)
    _renderer = SDL_CreateRenderer(_window, -1, 0)
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
                rects.extend(SDL_Rect(px * PIXEL_SIZE, py * PIXEL_SIZE, PIXEL_SIZE - 1, PIXEL_SIZE  - 1))
                rects_count += 1
    if rects_count > 0:
        SDL_SetRenderDrawColor(_renderer, 255, 255, 255, 255)
        SDL_RenderFillRects(_renderer, rects, rects_count)
    SDL_RenderPresent(_renderer)