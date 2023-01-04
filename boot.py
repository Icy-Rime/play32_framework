# This file is executed on every boot (including wake-boot from deepsleep)
import usys, machine, micropython
usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
try:
    micropython.alloc_emergency_exception_buf(512)
except: pass
try:
    # init unix port
    try:
        from play32hw import hw_config
    except:
        import uos
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
        root_path = abspath(join(__file__, '..'))
        lib_path = join(root_path, 'lib')
        usys.path.append(lib_path)
        from play32hw import hw_config
    model = hw_config.get_model()
    if model == hw_config.MODEL_UNIX:
        from play32sys import path
        import uos
        root_path = path.abspath(path.join(__file__, '..'))
        uos.chdir(root_path)
        usys.path[:] = ['lib', '', path.join(root_path, 'lib'), root_path, '.frozen', path.join(root_path, 'lib', 'play32hw', 'mpy_ext')]
        import main as __rootmain
except Exception as e:
    import usys
    usys.print_exception(e)
del machine, micropython
#import webrepl
#webrepl.start()
