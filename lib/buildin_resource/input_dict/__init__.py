__input_dict = None

from buildin_resource import BytesStream

def get_input_dict():
    global __input_dict
    if __input_dict == None:
        try:
            f = open('/resource/input_dict/dict.bin', "rb")
            __input_dict = f
        except:
            from buildin_resource.input_dict.pinyin_dict import data
            __input_dict = BytesStream(data)
    return __input_dict
