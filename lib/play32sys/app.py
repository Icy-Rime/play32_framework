import uos as os
import usys as sys
from play32hw.rtc_memory import rtc_dict
from play32sys.path import get_app_path, _get_curr_app, _set_curr_app, get_component_path
from machine import reset
import gc

KEY_BOOT_APP = 'bapp'
KEY_BOOT_APP_PARAMS = 'bappp'
KEY_BOOT_APP_KEYWORDS = 'bappk'

# system function
def _on_boot_(debug=False):
    sys.path[:] = ['', 'lib', '/', '/lib']
    boot_app, args, kws = get_boot_app()
    if isinstance(boot_app, str) and boot_app != "":
        # app.clear_boot_app()
        try:
            run_app(boot_app, *args, **kws)
        except Exception as e:
            import usys
            usys.print_exception(e)
            if not debug:
                reset_and_run_app("")
    else:
        call_component('app_selector')

# app function
def get_env(env_name, default=None):
    if env_name in rtc_dict:
        return rtc_dict[env_name]
    return default

def set_env(env_name, env_value, commit=True):
    rtc_dict[env_name] = env_value
    if commit:
        rtc_dict.commit_change()

def get_boot_app():
    if KEY_BOOT_APP in rtc_dict:
        return rtc_dict[KEY_BOOT_APP], rtc_dict[KEY_BOOT_APP_PARAMS], rtc_dict[KEY_BOOT_APP_KEYWORDS]
    return None, [], {}

def set_boot_app(app_path, *args, **kws):
    rtc_dict[KEY_BOOT_APP] = app_path
    rtc_dict[KEY_BOOT_APP_PARAMS] = list(args)
    rtc_dict[KEY_BOOT_APP_KEYWORDS] = kws
    rtc_dict.commit_change()

def clear_boot_app():
    if KEY_BOOT_APP in rtc_dict:
        del rtc_dict[KEY_BOOT_APP]
    rtc_dict.commit_change()

def reset_and_run_app(app_name, *args, **kws):
    set_boot_app(app_name, *args, **kws)
    reset()

def run_app(app_name, *args, **kws):
    curr = os.getcwd()
    c_a = _get_curr_app()
    _set_curr_app(app_name)
    os.chdir(get_app_path(app_name))
    try:
        module = __import__("appmain")
        if "appmain" in sys.modules:
            del sys.modules["appmain"]
        return module.main(app_name, *args, **kws)
    finally:
        os.chdir(curr)
        _set_curr_app(c_a)
        gc.collect()

def call_component(component_name, *args, **kws):
    curr = os.getcwd()
    os.chdir(get_component_path(component_name))
    try:
        module = __import__("appmain")
        if "appmain" in sys.modules:
            del sys.modules["appmain"]
        return module.main(component_name, *args, **kws)
    finally:
        os.chdir(curr)
        gc.collect()

# debug function
def free():
    gc.collect()
    # print('Mem Remain:', gc.mem_free(), 'Bytes')
    return gc.mem_free()

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
