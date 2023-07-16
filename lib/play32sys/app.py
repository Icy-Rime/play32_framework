import uos, usys
from play32sys.path import join, exist, get_app_path, clear_temporary_dir
from buildin_resource.image import DEFAULT_BOOT_ICON
from play32hw.hw_config import ResetException
from boot_params import get_saved_dict, set_saved_dict

import gc

VERSION = (1, 17, 0)
KEY_BOOT_APP = 'bapp'
KEY_BOOT_APP_PARAMS = 'bappp'
KEY_BOOT_APP_KEYWORDS = 'bappk'
KEY_BOOT_IMAGE_PATH = 'bimg'

__boot_dict = None
def __init_dict():
    global __boot_dict
    if __boot_dict == None:
        __boot_dict = get_saved_dict()

def __save_dict():
    global __boot_dict
    if __boot_dict != None:
        set_saved_dict(__boot_dict)

# system function
def _on_boot_(app_name=None, *app_args, **app_kws):
    __init_dict()
    # >>>> init screen <<<<
    import hal_screen
    hal_screen.init()
    render_boot_image()
    # >>>> init <<<<
    # init what you need.
    
    argv = usys.argv # type: list[str]
    for opt in argv:
        if opt.startswith('-Oapp='):
            app_name = opt[len('-Oapp='):]
    
    if app_name != None:
        boot_app, args, kws = app_name, app_args, app_kws
    else:
        boot_app, args, kws = get_boot_app()
    clear_boot_app()
    clear_boot_image()
    clear_temporary_dir()
    if isinstance(boot_app, str) and boot_app != "":
        # app.clear_boot_app()
        gc.collect()
        run_app(boot_app, *args, **kws)
    else:
        from components.app_selector import appmain as app_selector
        app_selector.main()

# app function
def get_boot_app():
    if KEY_BOOT_APP in __boot_dict:
        return __boot_dict[KEY_BOOT_APP], __boot_dict[KEY_BOOT_APP_PARAMS], __boot_dict[KEY_BOOT_APP_KEYWORDS]
    return None, [], {}

def set_boot_app(app_path, *args, **kws):
    __boot_dict[KEY_BOOT_APP] = app_path
    __boot_dict[KEY_BOOT_APP_PARAMS] = list(args)
    __boot_dict[KEY_BOOT_APP_KEYWORDS] = kws
    __save_dict()

def clear_boot_app():
    if KEY_BOOT_APP in __boot_dict:
        del __boot_dict[KEY_BOOT_APP]
    if KEY_BOOT_APP_PARAMS in __boot_dict:
        del __boot_dict[KEY_BOOT_APP_PARAMS]
    if KEY_BOOT_APP_KEYWORDS in __boot_dict:
        del __boot_dict[KEY_BOOT_APP_KEYWORDS]
    __save_dict()

def render_boot_image():
    boot_image_path = get_boot_image()
    if boot_image_path == None:
        import hal_screen
        hal_screen.refresh()
        boot_image_path = DEFAULT_BOOT_ICON
    if boot_image_path != "":
        from graphic import framebuf_helper
        import framebuf, hal_screen
        if exist(boot_image_path):
            from graphic import pbm
            with open(boot_image_path, 'rb') as ifile:
                iw, ih, _, idata = pbm.read_image(ifile)[:4]
        else:
            from buildin_resource.image.play32_icon import PLAY32_ICON_DATA
            iw, ih, idata = PLAY32_ICON_DATA
        image = framebuf.FrameBuffer(idata, iw, ih, framebuf.MONO_HLSB)
        image = framebuf_helper.ensure_same_format(
            image, 
            framebuf_helper.MONO_HLSB,
            iw, ih,
            hal_screen.get_format(),
            framebuf_helper.get_white_color(hal_screen.get_format())
        )
        sw, sh = hal_screen.get_size()
        frame = hal_screen.get_framebuffer()
        frame.fill(0)
        frame.blit(image, (sw - iw) // 2, (sh - ih) // 2, 0)
        hal_screen.refresh()
        del idata, image, iw, ih, sw, sh
        return True
    return False

def get_boot_image():
    if KEY_BOOT_IMAGE_PATH in __boot_dict:
        return __boot_dict[KEY_BOOT_IMAGE_PATH]
    return None

def set_boot_image(pbm_path):
    __boot_dict[KEY_BOOT_IMAGE_PATH] = pbm_path
    __save_dict()

def disable_boot_image():
    set_boot_image("")

def clear_boot_image():
    if KEY_BOOT_IMAGE_PATH in __boot_dict:
        del __boot_dict[KEY_BOOT_IMAGE_PATH]
    __save_dict()

def reset_and_run_app(app_name, *args, **kws):
    set_boot_app(app_name, *args, **kws)
    if get_boot_image() == None:
        set_boot_image(DEFAULT_BOOT_ICON)
    if render_boot_image():
        disable_boot_image()
    raise ResetException()

def run_app(app_name, *args, **kws):
    curr = uos.getcwd()
    uos.chdir(get_app_path(app_name))
    usys.path.insert(0, get_app_path(app_name))
    usys.path.insert(0, join(get_app_path(app_name), "lib"))
    try:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
        module = __import__("appmain")
        res = module.main(app_name, *args, **kws)
        del module
        return res
    finally:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
        usys.path.remove(get_app_path(app_name))
        usys.path.remove(join(get_app_path(app_name), "lib"))
        uos.chdir(curr)
        gc.collect()

# debug function
def free():
    gc.collect()
    # print('Mem Remain:', gc.mem_free(), 'Bytes')
    return gc.mem_free()

def has_big_memory():
    return gc.threshold() >= 1048576

def timed_function(f, *args, **kwargs):
    try:
        myname = f.__name__
    except:
        myname = str(f)
    def new_func(*args, **kwargs):
        import utime
        print('Function [{}] Start'.format(myname))
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function [{}] Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def timed_function_async(f, *args, **kwargs):
    try:
        myname = f.__name__
    except:
        myname = str(f)
    async def new_func(*args, **kwargs):
        import utime
        print('Function [{}] Start'.format(myname))
        t = utime.ticks_us()
        result = await f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function [{}] Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def print_exception(e):
    import hal_screen, uio, usys
    from graphic import abmfont, framebuf_console, framebuf_helper
    WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
    hal_screen.init()
    frame = hal_screen.get_framebuffer()
    w, h = hal_screen.get_size()
    console = framebuf_console.Console(frame, w, h, abmfont.FontDrawSmallAscii(), WHITE, hal_screen.refresh)
    err = uio.BytesIO()
    usys.print_exception(e, err)
    err.seek(0)
    console.log(err.read().decode("utf8"))
