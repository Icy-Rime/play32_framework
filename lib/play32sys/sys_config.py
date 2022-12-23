import ujson
from play32sys import path

__json = None

def init():
    global __json
    __p = path.join(path.get_data_path(), "sys_config.json")
    try:
        with open(__p, "rb") as f:
            __json = ujson.load(f)
    except:
        __json = {}
    del __p

def get_sys_config(key, default_value=None):
    if __json == None:
        init()
    if key in __json:
        return __json[key]
    return default_value

def set_sys_config(key, value):
    if __json == None:
        init()
    __json[key] = value

def save_sys_config():
    if __json == None:
        init()
    __p = path.join(path.get_data_path(), "sys_config.json")
    try:
        with open(__p, "wb") as f:
            ujson.dump(__json, f)
        return True
    except:
        return False
