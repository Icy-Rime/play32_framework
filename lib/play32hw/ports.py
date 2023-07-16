from play32hw.hw_config import get_model, MODEL_UNIX

if get_model() == MODEL_UNIX:
    from play32hw.punix.ports import *
else:
    def before_reset():
        pass
