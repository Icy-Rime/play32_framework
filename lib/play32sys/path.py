# path operation
import uos
FILE_TYPE_DIR = 0x4000
FILE_TYPE_FILE = 0X8000

__ROOT_BASE = '/'
__APP_BASE = '/apps'
__DATA_BASE = '/data'
__cur_app = ''

def _get_curr_app():
    return __cur_app

def _set_curr_app(app):
    global __cur_app
    __cur_app = app

def join(pt1, *pts):
    # type: (str, str) -> str
    for pt in pts:
        if pt.endswith('/'):
            pt = pt[:-1]
        if pt.startswith('/'):
            pt1 = pt
        else:
            pt1 += '' if pt1.endswith('/') else '/'
            pt1 += pt
    return pt1

def abspath(pt):
    # type: (str) -> str
    if pt.startswith('/'):
        return pt
    else:
        c = uos.getcwd()
        return join(c, pt)

def exist(pt):
    try:
        return uos.stat(pt)
    except OSError:
        return False

def get_app_path(name='/'):
    # type: (str) -> str
    if __cur_app == '/':
        return __ROOT_BASE
    else:
        return join(__APP_BASE, name)

def get_data_path(name='/'):
    # type: (str) -> str
    if __cur_app == '/':
        return __DATA_BASE
    else:
        return join(__DATA_BASE, name)
