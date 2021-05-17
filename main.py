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
# from machine import Pin, SPI
# from play32hw import ssd1351
# sspi = SPI(1, baudrate=20000000, sck=Pin(32), mosi=Pin(33))
# scs = Pin(14)
# sdc = Pin(12)
# srst = Pin(27)
# display = ssd1351.Display(sspi, scs, sdc, srst, 128, 128)
# display.clear(0xFFFF)
# __screen = hal_screen.__screen
# __buffer = hal_screen.__buffer
# __screen.refresh(0, 0, 128, 128, __buffer)
