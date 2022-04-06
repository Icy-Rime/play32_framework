import gc
import uos
from flashbdev import bdev

try:
    if bdev:
        uos.mount(bdev, "/")
except OSError:
    import inisetup

    vfs = inisetup.setup()

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
        try:
            from play32sys import app
            app._on_boot_()
            pass
        except Exception as e:
            import usys, updater
            usys.print_exception(e)
            updater._on_enter_recovery_mode_()
    print("==== End Main ====")

import usys, esp, machine, micropython
# framework_debug
def _exist(pt):
    try:
        return uos.stat(pt)
    except OSError:
        return False
if not _exist("/framework_debug"):
    usys.path[:] = ['.frozen', 'lib', '', '/lib', '/']
    esp.osdebug(None)
    machine.freq(240000000)
    micropython.alloc_emergency_exception_buf(100)
    gc.collect()
    main() # main function
else:
    usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
    # let micropython load boot.py and main.py
