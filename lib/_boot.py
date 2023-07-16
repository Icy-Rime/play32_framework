import gc
import uos
from play32hw.hw_config import ResetException

try:
    # esp32 setup
    from flashbdev import bdev
    try:
        if bdev:
            uos.mount(bdev, "/")
    except OSError:
        import inisetup

        vfs = inisetup.setup()
except: pass

# main.py
# >>>> recovery mode <<<<
def check_rec():
    import hal_keypad
    hal_keypad.init()
    hal_keypad.clear_key_status([hal_keypad.KEY_A, hal_keypad.KEY_B])
    __count = 0
    for event in hal_keypad.get_key_event():
        event_type, key = hal_keypad.parse_key_event(event)
        if event_type == hal_keypad.EVENT_KEY_PRESS:
            if key in [hal_keypad.KEY_A, hal_keypad.KEY_B]:
                __count += 1
    if __count >= 2:
        # enter recovery mode
        import updater
        updater._on_enter_recovery_mode_()
    # >>>> main <<<<
    del __count

# >>>> main <<<<
check_rec()

import usys, micropython
# framework_debug
def _exist(pt):
    try:
        return uos.stat(pt)
    except OSError:
        return False
if not _exist("/framework_debug"):
    usys.path[:] = ['.frozen', 'lib', '', '/lib', '/']
    micropython.alloc_emergency_exception_buf(512)
    while True:
        from play32hw.hw_config import ResetException
        import gc
        gc.collect()
        print("Free:", gc.mem_free())
        try:
            import hal_keypad
            hal_keypad.init()
            from play32sys import app
            app._on_boot_()
            print("==== End Main ====")
        except ResetException:
            # deinit
            import hal_keypad
            hal_keypad.clear_key_status([
                hal_keypad.KEY_A,
                hal_keypad.KEY_B,
                hal_keypad.KEY_UP,
                hal_keypad.KEY_DOWN,
                hal_keypad.KEY_LEFT,
                hal_keypad.KEY_RIGHT,
            ])
            from play32hw import ports
            ports.before_reset()
            # clear as much references as possible
            import usys
            keys = list(usys.modules.keys())
            for name in keys:
                if name == "boot_params":
                    print("Reset: Skip clear 'boot_params' module.")
                    continue
                del usys.modules[name]
            globals().clear()
            locals().clear()
            import gc
            gc.collect()
            continue
        except Exception as e:
            import usys
            usys.print_exception(e)
        break
else:
    usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
    # let micropython load boot.py and main.py
