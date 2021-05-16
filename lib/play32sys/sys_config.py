import ujson
from play32sys import path
__p = path.join(path.get_data_path(), "sys_config.json")
with open(__p, "rb") as f:
    __json = ujson.load(f)

def get_sys_config(key, default_value=None):
    if key in __json:
        return __json[key]
    return default_value

del __p
