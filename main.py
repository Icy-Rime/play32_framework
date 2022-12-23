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
        import usys
        usys.print_exception(e)
print("==== End Main ====")

# test below
