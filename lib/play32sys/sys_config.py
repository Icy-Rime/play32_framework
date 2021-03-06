__json = None

def init():
    global __json
    import ujson
    from play32sys import path
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
