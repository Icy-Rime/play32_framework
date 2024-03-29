import usys

MODEL_UNKNOWN = 0
MODEL_INITIAL = 1
MODEL_LITE = 2
MODEL_UNIX = 0xFFFE
MODEL_EMULATOR = 0xFFFF

__model = -1

def get_model():
    global __model
    if __model < 0:
        # init model
        try:
            mch = usys.implementation._machine # type: str
        except:
            mch = usys.implementation.machine # type: str
        mch = mch[:mch.find(" with ")]
        __model = MODEL_UNKNOWN
        if mch == "Play32 Initial":
            __model = MODEL_INITIAL
        elif mch == "Play32 Lite":
            __model = MODEL_LITE
        elif mch == "Play32 Emulator":
            __model = MODEL_EMULATOR
        elif mch.startswith("linux"):
            __model = MODEL_UNIX
    return __model
get_model()

class ResetException(Exception):
    pass
