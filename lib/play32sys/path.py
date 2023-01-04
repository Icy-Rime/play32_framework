# path operation
from play32hw.hw_config import get_model, MODEL_UNIX
import uos
FILE_TYPE_DIR = 0x4000
FILE_TYPE_FILE = 0X8000

def abspath(pt):
    # type: (str) -> str
    if pt.startswith('/'):
        return pt
    else:
        c = uos.getcwd()
        return join(c, pt)

def join(pt1, *pts):
    # type: (str, str) -> str
    for pt in pts:
        if pt.endswith('/'):
            pt = pt[:-1]
        if pt.startswith('/'):
            pt1 = pt
        elif pt == '..':
            rid = pt1.rfind('/')
            if rid > 0:
                pt1 = pt1[:rid]
            elif rid == 0:
                pt1 = '/'
            else:
                pt1 = ''
        else:
            pt1 += '' if pt1.endswith('/') else '/'
            pt1 += pt
    if pt1.endswith('/') and len(pt1) > 1:
        pt1 = pt1[:-1]
    return pt1

__ROOT_BASE = join(abspath(join(__file__, '..')), '..', '..', '.play32root') if get_model() == MODEL_UNIX else '/'
__APP_BASE = join(__ROOT_BASE, 'apps') if get_model() == MODEL_UNIX else '/apps'
__DATA_BASE = join(__ROOT_BASE, 'data') if get_model() == MODEL_UNIX else '/data'
__TMP_BASE = join(__ROOT_BASE, 'tmp') if get_model() == MODEL_UNIX else '/tmp'

class TemporaryFileContext():
    def __init__(self, path):
        self.__p = path
        self.__f = None
    
    def __enter__(self):
        self.__f = open(self.__p, 'wb+')
        return self.__f
    
    def __exit__(self, type, value, trace):
        try:
            self.__f.close()
            self.__f = None
        except: pass
        try:
            uos.remove(self.__p)
        except: pass

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
    parts = abspath(pt).split('/')
    c_dir = "/"
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

def open_temporary_file(path):
    return TemporaryFileContext(path)

def clear_temporary_dir():
    rmtree(__TMP_BASE)
    mkdirs(__TMP_BASE)


def __ensure_dir__():
    if not exist(__ROOT_BASE):
        mkdirs(__ROOT_BASE)
    if not exist(__APP_BASE):
        uos.mkdir(__APP_BASE)
    if not exist(__DATA_BASE):
        uos.mkdir(__DATA_BASE)
    if not exist(__TMP_BASE):
        uos.mkdir(__TMP_BASE)
__ensure_dir__()
