import uos

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