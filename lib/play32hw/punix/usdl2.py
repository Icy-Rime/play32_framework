# (c) 2018 Paul Sokolovsky. Either zlib or MIT license at your choice.
import ffi
import ustruct
import uctypes
import usys

SIZE_SIZE_T = uctypes.sizeof({ "_": (0 | uctypes.PTR, uctypes.VOID) })
SIZE_INT = uctypes.sizeof({ "_": (0 | uctypes.INT) })
SIZE_T = uctypes.UINT32 if SIZE_SIZE_T == 4 else uctypes.UINT64
RAW_PTR = SIZE_T

PTR_NULL = 0
SDL_TRUE = 1
SDL_FALSE = 0

SDL_INIT_AUDIO = 0x00000010
SDL_INIT_VIDEO = 0x00000020
SDL_INIT_EVENTS = 0x00004000

SDL_WINDOW_FULLSCREEN = 0x00000001
SDL_WINDOW_OPENGL = 0x00000002
SDL_WINDOW_FULLSCREEN_DESKTOP = SDL_WINDOW_FULLSCREEN | 0x00001000
SDL_WINDOWPOS_UNDEFINED = 0x1FFF0000
SDL_WINDOWPOS_CENTERED = 0x2FFF0000
SDL_RENDERER_SOFTWARE = 0x00000001
SDL_RENDERER_ACCELERATED = 0x00000002
SDL_RENDERER_PRESENTVSYNC = 0x00000004
SDL_RENDERER_TARGETTEXTURE = 0x00000008
SDL_TEXTUREACCESS_STREAMING = 1

def SDL_DEFINE_PIXELFORMAT(type, order, layout, bits, bytes):
    return ((1 << 28) | ((type) << 24) | ((order) << 20) | ((layout) << 16) | \
        ((bits) << 8) | ((bytes) << 0))

SDL_PIXELTYPE_UNKNOWN = 0,
SDL_PIXELTYPE_INDEX1 = 1
SDL_PIXELTYPE_INDEX4 = 2
SDL_PIXELTYPE_INDEX8 = 3
SDL_PIXELTYPE_PACKED8 = 4
SDL_PIXELTYPE_PACKED16 = 5
SDL_PIXELTYPE_PACKED32 = 6
SDL_PIXELTYPE_ARRAYU8 = 7
SDL_PIXELTYPE_ARRAYU16 = 8
SDL_PIXELTYPE_ARRAYU32 = 9
SDL_PIXELTYPE_ARRAYF16 = 10
SDL_PIXELTYPE_ARRAYF32 = 11

SDL_PACKEDORDER_NONE = 0
SDL_PACKEDORDER_XRGB = 1
SDL_PACKEDORDER_RGBX = 2
SDL_PACKEDORDER_ARGB = 3
SDL_PACKEDORDER_RGBA = 4
SDL_PACKEDORDER_XBGR = 5
SDL_PACKEDORDER_BGRX = 6
SDL_PACKEDORDER_ABGR = 7
SDL_PACKEDORDER_BGRA = 8

SDL_ARRAYORDER_NONE = 0
SDL_ARRAYORDER_RGB = 1
SDL_ARRAYORDER_RGBA = 2
SDL_ARRAYORDER_ARGB = 3
SDL_ARRAYORDER_BGR = 4
SDL_ARRAYORDER_BGRA = 5
SDL_ARRAYORDER_ABGR = 6

SDL_PACKEDLAYOUT_NONE = 0
SDL_PACKEDLAYOUT_332 = 1
SDL_PACKEDLAYOUT_4444 = 2
SDL_PACKEDLAYOUT_1555 = 3
SDL_PACKEDLAYOUT_5551 = 4
SDL_PACKEDLAYOUT_565 = 5
SDL_PACKEDLAYOUT_8888 = 6
SDL_PACKEDLAYOUT_2101010 = 7
SDL_PACKEDLAYOUT_1010102 = 8

SDL_PIXELFORMAT_ARGB8888 = \
        SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_ARGB,
                               SDL_PACKEDLAYOUT_8888, 32, 4)

SDL_PIXELFORMAT_RGB24 = \
        SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_ARRAYU8, SDL_ARRAYORDER_RGB, 0,
                               24, 3)

SDL_EVENT_QUIT = 0x100
SDL_EVENT_KEYDOWN = 0x300
SDL_EVENT_KEYUP = 0x301

SDL_AUDIO_U8 = 0x0008
SDL_AUDIO_S8 = 0x8008
SDL_AUDIO_U16LSB = 0x0010
SDL_AUDIO_S16LSB = 0x8010
SDL_AUDIO_U16MSB = 0x1010
SDL_AUDIO_S16MSB = 0x9010
SDL_AUDIO_U16 = SDL_AUDIO_U16LSB
SDL_AUDIO_S16 = SDL_AUDIO_S16LSB
SDL_AUDIO_CHANNEL_MONO = 1
SDL_AUDIO_CHANNEL_STEREO = 2

# https://wiki.libsdl.org/SDL2/SDL_AudioSpec
STRUCT_SDL_AUDIO_SPEC = {
    "freq": (0 | uctypes.INT),
    "format": (SIZE_INT | uctypes.UINT16),
    "channels": (SIZE_INT + 2 | uctypes.UINT8),
    "silence": (SIZE_INT + 3 | uctypes.UINT8),
    "samples": (SIZE_INT + 4 | uctypes.UINT16),
    "size": (SIZE_INT + 6 | uctypes.UINT32),
    "callback": (SIZE_INT + 10 | RAW_PTR),
    "userdata": (SIZE_INT + SIZE_SIZE_T + 10 | RAW_PTR),
}
STRUCT_RAW_PTR = {
    "ptr": (0 | RAW_PTR)
}
STRUCT_PTR_CHAR = {
    "ch": (0 | uctypes.UINT8)
}

try:
    _sdl = ffi.open("libSDL2-2.0.so")
except:
    print("\n======= Error =======")
    print("SDL2.0 is required!")
    print("=====================\n")
    raise

SDL_malloc = _sdl.func("P", "SDL_malloc", "P") # argument 'P' as 'size_t'
SDL_free = _sdl.func("v", "SDL_free", "P")

SDL_Init = _sdl.func("i", "SDL_Init", "I")
SDL_Quit = _sdl.func("v", "SDL_Quit", "")

SDL_CreateWindow = _sdl.func("P", "SDL_CreateWindow", "siiiii")
SDL_DestroyWindow = _sdl.func("v", "SDL_DestroyWindow", "P")

SDL_CreateRenderer = _sdl.func("P", "SDL_CreateRenderer", "PiI")
SDL_CreateSoftwareRenderer = _sdl.func("P", "SDL_CreateSoftwareRenderer", "P")
SDL_DestroyRenderer = _sdl.func("v", "SDL_DestroyRenderer", "P")
SDL_RenderSetLogicalSize = _sdl.func("i", "SDL_RenderSetLogicalSize", "Pii")
SDL_SetRenderDrawColor = _sdl.func("i", "SDL_SetRenderDrawColor", "PBBBB")
SDL_RenderClear = _sdl.func("v", "SDL_RenderClear", "P")
SDL_RenderCopy = _sdl.func("v", "SDL_RenderCopy", "PPPP")
SDL_RenderPresent = _sdl.func("v", "SDL_RenderPresent", "P")

SDL_RenderDrawPoint = _sdl.func("i", "SDL_RenderDrawPoint", "Pii")
SDL_RenderDrawLine = _sdl.func("i", "SDL_RenderDrawLine", "Piiii")
SDL_RenderDrawRect = _sdl.func("i", "SDL_RenderDrawRect", "PP")
SDL_RenderFillRect = _sdl.func("i", "SDL_RenderFillRect", "PP")
SDL_RenderFillRects = _sdl.func("i", "SDL_RenderFillRects", "PPi")
SDL_RenderSetIntegerScale = _sdl.func("i", "SDL_RenderSetIntegerScale", "Pi")

SDL_FreeSurface = _sdl.func("v", "SDL_FreeSurface", "P")

SDL_CreateTexture = _sdl.func("P", "SDL_CreateTexture", "PIiii")
SDL_CreateTextureFromSurface = _sdl.func("P", "SDL_CreateTextureFromSurface", "PP")
SDL_UpdateTexture = _sdl.func("i", "SDL_UpdateTexture", "PPPi")
SDL_LockTexture = _sdl.func("i", "SDL_LockTexture", "pPpp")
SDL_UnlockTexture = _sdl.func("i", "SDL_UnlockTexture", "p")

SDL_LoadBMP_RW = _sdl.func("P", "SDL_LoadBMP_RW", "Pi")
SDL_RWFromFile = _sdl.func("P", "SDL_RWFromFile", "ss")
SDL_RWFromMem = _sdl.func("P", "SDL_RWFromMem", "Pi")

_SDL_GetKeyboardState = _sdl.func("P", "SDL_GetKeyboardState", "p")
SDL_PollEvent = _sdl.func("i", "SDL_PollEvent", "p")
SDL_ResetKeyboard = _sdl.func("v", "SDL_ResetKeyboard", "")

_SDL_GetDefaultAudioInfo = _sdl.func("i", "SDL_GetDefaultAudioInfo", "ppi")
_SDL_OpenAudioDevice = _sdl.func("I", "SDL_OpenAudioDevice", "PiPpi")
_SDL_PauseAudioDevice = _sdl.func("v", "SDL_PauseAudioDevice", "Ii")
_SDL_QueueAudio = _sdl.func("i", "SDL_QueueAudio", "IPI")
SDL_ClearQueuedAudio = _sdl.func("v", "SDL_ClearQueuedAudio", "I")
SDL_GetQueuedAudioSize = _sdl.func("I", "SDL_GetQueuedAudioSize", "I")

def read_cstring(string_ptr):
    if string_ptr == PTR_NULL:
        return ""
    size = 0
    addr = string_ptr
    ch = uctypes.struct(addr, STRUCT_PTR_CHAR).ch
    while ch > 0:
        size += 1
        addr += 1
        ch = uctypes.struct(addr, STRUCT_PTR_CHAR).ch
    return uctypes.bytes_at(string_ptr, size).decode("utf-8")

def SDL_LoadBMP(file):
    return SDL_LoadBMP_RW(SDL_RWFromFile(file, "rb"), 1)

def SDL_Rect(x=0, y=0, w=0, h=0):
    return ustruct.pack("iiii", x, y, w, h)

def SDL_GetEventType(event_buffer):
    return ustruct.unpack_from("I", event_buffer)[0]

def SDL_GetKeyboardEventStruct(event_buffer):
    # struct https://wiki.libsdl.org/SDL2/SDL_KeyboardEvent
    # scan code https://github.com/libsdl-org/SDL/blob/SDL2/include/SDL_scancode.h
    # key code https://github.com/libsdl-org/SDL/blob/SDL2/include/SDL_keycode.h
    return ustruct.unpack_from("IIIBBiiHI", event_buffer)

def SDL_GetKeyboardEventKeyCode(event_buffer):
    event = ustruct.unpack_from("IIIBBiiHI", event_buffer)
    return event[6]

def SDL_GetKeyboardEventRepeat(event_buffer):
    event = ustruct.unpack_from("IIIBBiiHI", event_buffer)
    return event[4]

def SDL_GetKeyboardState():
    # https://wiki.libsdl.org/SDL2/SDL_GetKeyboardState
    num_buffer = bytearray(ustruct.pack("i", 0))
    mem_start = _SDL_GetKeyboardState(num_buffer)
    size = ustruct.unpack("i", num_buffer)[0]
    return uctypes.bytearray_at(mem_start, size)

def SDL_AudioSpec(freq = 44100, format = SDL_AUDIO_S16LSB, channels = SDL_AUDIO_CHANNEL_STEREO, samples = 4096):
    spec_buffer = bytearray(uctypes.sizeof(STRUCT_SDL_AUDIO_SPEC))
    spec = uctypes.struct(uctypes.addressof(spec_buffer), STRUCT_SDL_AUDIO_SPEC)
    spec.freq = freq
    spec.format = format
    spec.channels = channels
    spec.samples = samples
    spec.callback = PTR_NULL
    spec.userdata = PTR_NULL
    return spec_buffer

def SDL_AudioSpecDict(spec_buffer):
    spec = uctypes.struct(uctypes.addressof(spec_buffer), STRUCT_SDL_AUDIO_SPEC)
    return {
        "freq": spec.freq,
        "format": spec.format,
        "channels": spec.channels,
        "silence": spec.silence,
        "samples": spec.samples,
        "size": spec.size,
    }

def SDL_GetDefaultAudioInfo():
    # type: () -> tuple[str, bytearray]
    name_ptr_buffer = bytearray(SIZE_SIZE_T)
    spec_buffer = SDL_AudioSpec()
    suc = _SDL_GetDefaultAudioInfo(name_ptr_buffer, spec_buffer)
    print(suc == 0)
    name_text_ptr = uctypes.struct(uctypes.addressof(name_ptr_buffer), STRUCT_RAW_PTR).ptr
    if name_text_ptr != PTR_NULL:
        name = read_cstring(name_text_ptr)
        SDL_free(name_text_ptr)
    else:
        name = ""
    return name, spec_buffer

def SDL_OpenAudioDevice(name, is_capture, desired, obtained, allowed_changes = 0):
    # type: (str, bool, bytearray, bytearray, int) -> int
    if len(name) == 0:
        name_ptr = PTR_NULL
    else:
        name_bytes = name.encode("utf-8") + b"\0"
        name_ptr = uctypes.addressof(name_bytes)
    iscapture = SDL_TRUE if is_capture else SDL_FALSE
    return _SDL_OpenAudioDevice(name_ptr, iscapture, desired, obtained, allowed_changes)

def SDL_PauseAudioDevice(device_id, pause):
    _SDL_PauseAudioDevice(device_id, SDL_TRUE if pause else SDL_FALSE)

def SDL_QueueAudio(device_id, data):
    data = bytes(data)
    size = len(data)
    return _SDL_QueueAudio(device_id, data, size)
