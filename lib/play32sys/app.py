import uos, usys, ujson
from play32sys.path import join, get_tmp_path, get_app_path, get_component_path, clear_temporary_dir
from resource.image import PLAY32_ICON
from machine import reset as __soft_reset
import gc

VERSION = (1, 16, 0)
KEY_BOOT_APP = 'bapp'
KEY_BOOT_APP_PARAMS = 'bappp'
KEY_BOOT_APP_KEYWORDS = 'bappk'
KEY_BOOT_IMAGE_PATH = 'bimg'
DICT_FILE_PATH = join(get_tmp_path(), 'boot.json')

__boot_dict = None
def __init_dict():
    global __boot_dict
    if __boot_dict == None:
        pass
    try:
        with open(DICT_FILE_PATH, 'rb') as f:
            __boot_dict = ujson.load(f)
    except:
        __boot_dict = {}

def __save_dict():
    if __boot_dict == None:
        return
    try:
        with open(DICT_FILE_PATH, 'wb') as f:
            ujson.dump(__boot_dict, f)
    except Exception as e:
        usys.print_exception(e)

# system function
def _on_boot_(debug=False, app_name=None, *app_args, **app_kws):
    __init_dict()
    # >>>> init screen <<<<
    import hal_screen
    hal_screen.init()
    render_boot_image()
    # >>>> init <<<<
    # init what you need.
    # import hal_keypad, hal_buzz, hal_led, hal_battery
    # hal_keypad.init()
    # hal_buzz.init()
    # hal_led.init()
    # hal_battery.init()
    # >>>> start <<<<
    usys.path[:] = ['', 'lib', '/', '/lib']
    if app_name != None:
        boot_app, args, kws = app_name, app_args, app_kws
    else:
        boot_app, args, kws = get_boot_app()
    clear_boot_app()
    clear_boot_image()
    clear_temporary_dir()
    if isinstance(boot_app, str) and boot_app != "":
        # app.clear_boot_app()
        try:
            gc.collect()
            run_app(boot_app, *args, **kws)
        except Exception as e:
            usys.print_exception(e)
            if not debug:
                reset_and_run_app("")
    else:
        call_component('app_selector')

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
        boot_image_path = PLAY32_ICON
    if boot_image_path != "":
        from graphic import framebuf_helper, pbm
        import framebuf, hal_screen
        with open(boot_image_path, 'rb') as ifile:
            iw, ih, ifm, idata, _ = pbm.read_image(ifile)
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
        del idata, image, iw, ih, sw, sh, ifm
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
        set_boot_image(PLAY32_ICON)
    if render_boot_image():
        disable_boot_image()
    __soft_reset()

def run_app(app_name, *args, **kws):
    curr = uos.getcwd()
    uos.chdir(get_app_path(app_name))
    try:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
        module = __import__("appmain")
        res = module.main(app_name, *args, **kws)
        return res
    finally:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
        uos.chdir(curr)
        gc.collect()

def call_component(component_name, *args, **kws):
    curr = uos.getcwd()
    uos.chdir(get_component_path(component_name))
    try:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
        module = __import__("appmain")
        res = module.main(component_name, *args, **kws)
        return res
    finally:
        if "appmain" in usys.modules:
            del usys.modules["appmain"]
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
