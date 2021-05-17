# >>>> init <<<<
import hal_screen, hal_keypad, hal_buzz
hal_screen.init()
hal_keypad.init()
hal_buzz.init()

# >>>> main <<<<
from play32sys import app
boot_app, args, kws = app.get_boot_app()
if isinstance(boot_app, str) and boot_app != "":
    # app.clear_boot_app()
    try:
        res = app.run_app(boot_app, *args, **kws)
    except Exception as e:
        import usys
        usys.print_exception(e)
        # app.reset()
else:
    app.run_app('app_selector')
    pass

# test below
