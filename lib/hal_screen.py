from play32hw.hw_config import get_model, MODEL_INITIAL, MODEL_LITE, MODEL_EMULATOR

if get_model() == MODEL_INITIAL:
    from play32hw.pinitial.hal_screen import *
elif get_model() == MODEL_LITE:
    from play32hw.plite.hal_screen import *
elif get_model() == MODEL_EMULATOR:
    from play32hw.pemulator.hal_screen import *
else:
    import framebuf
    _buffer = framebuf.FrameBuffer(bytearray(128*64//8), 128, 64, framebuf.MONO_HLSB)
    def init():
        pass

    def get_size():
        return 128, 64

    def get_format():
        return framebuf.MONO_HLSB

    def get_framebuffer() -> framebuf.FrameBuffer:
        return _buffer

    def refresh(x=0, y=0, w=0, h=0):
        pass
