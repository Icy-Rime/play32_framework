__saved_dict = {}

def get_saved_dict():
    global __saved_dict
    return __saved_dict

def set_saved_dict(dic):
    global __saved_dict
    __saved_dict = dic
