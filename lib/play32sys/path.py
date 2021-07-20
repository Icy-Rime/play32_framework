# path operation
import uos, uio
FILE_TYPE_DIR = 0x4000
FILE_TYPE_FILE = 0X8000

__ROOT_BASE = '/'
__APP_BASE = '/apps'
__DATA_BASE = '/data'
__TMP_BASE = '/tmp'
__COMPONENT_BASE = '/components'
__cur_app = ''

def _get_curr_app():
    return __cur_app

def _set_curr_app(app):
    global __cur_app
    __cur_app = app

class TemporaryFileContext(uio.IOBase):
    def __init__(self, path):
        self.__p = path
        self.__f = None
    
    def __enter__(self):
        self.__f = open(self.__p, "wb+")
        return self.__f
    
    def __exit__(self, type, value, trace):
        try:
            self.__f.close()
            self.__f = None
        except: pass
        try:
            uos.remove(self.__p)
        except: pass

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

def rmtree(pt):
    try:
        uos.remove(pt)
    except:
        for f in uos.ilistdir(pt):
            fname = f[0]
            rmtree(join(pt, fname))
        uos.rmdir(pt)

def mkdirs(pt):
    parts = abspath(pt).split("/")
    c_dir = parts[0]
    for p in parts:
        c_dir = join(c_dir, p)
        if exist(c_dir):
            continue
        uos.mkdir(c_dir)

def get_app_path(name='/'):
    # type: (str) -> str
    if name == '/':
        return __APP_BASE
    else:
        return join(__APP_BASE, name)

def get_data_path(name='/'):
    # type: (str) -> str
    if name == '/':
        return __DATA_BASE
    else:
        return join(__DATA_BASE, name)

def get_tmp_path(name='/'):
    # type: (str) -> str
    if name == '/':
        return __TMP_BASE
    else:
        return join(__TMP_BASE, name)

def get_component_path(name='/'):
    if name == '/':
        return __COMPONENT_BASE
    else:
        return join(__COMPONENT_BASE, name)

def open_temporary_file(path):
    return TemporaryFileContext(path)

def __ensure_dir__():
    if not exist(__APP_BASE):
        uos.mkdir(__APP_BASE)
    if not exist(__DATA_BASE):
        uos.mkdir(__DATA_BASE)
    if not exist(__TMP_BASE):
        uos.mkdir(__TMP_BASE)
    else:
        # re-build tmp dir
        rmtree(__TMP_BASE)
        mkdirs(__TMP_BASE)
__ensure_dir__()
