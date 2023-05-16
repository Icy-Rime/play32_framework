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
def main():
    # >>>> config memory <<<<
    import gc
    _threshold = (gc.mem_free() * 60) // 100 # 60% gc auto collect
    gc.threshold(_threshold)
    print("gc threshold has been set to", _threshold)
    del _threshold
    # >>>> recovery mode <<<<
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
    else:
        del __count
        from play32sys import app
        app._on_boot_()
    print("==== End Main ====")

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
        gc.collect()
        try:
            main() # main function
        except ResetException:
            continue
        except Exception as e:
            import usys
            usys.print_exception(e)
            text = str(e)
            del e
            gc.collect()
            import hal_screen
            hal_screen.init()
            from ui.dialog import dialog
            dialog(text, "Error")
            from play32sys import app
            app.reset_and_run_app("")
        break
else:
    usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
    # let micropython load boot.py and main.py
