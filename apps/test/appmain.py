import hal_screen, hal_keypad, utime
from graphic import framebuf_console, framebuf_helper
from play32sys import app
from resource.font import get_font_8px
FONT_8 = get_font_8px()
console = framebuf_console.Console(
    hal_screen.get_framebuffer(), *hal_screen.get_size(),
    font_draw=FONT_8,
    color=framebuf_helper.get_white_color(hal_screen.get_format()),
    display_update_fun=lambda: hal_screen.refresh()
)

def main(app_name, *args, **kws):
    hal_screen.init()
    hal_keypad.init()
    print("================")
    console.log("================")
    print('you are running {:}'.format(app_name))
    console.log('you are running {:}'.format(app_name))
    print(args)
    # console.log(args)
    print(kws)
    # console.log(kws)
    utime.sleep(1)
    print('{:} end'.format(app_name))
    console.log('{:} end'.format(app_name))
    print("================")
    console.log("================")
    console.log("Press any key to reboot.")
    main_loop()

def main_loop():
    while True:
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                console.log("Reboot..")
                app.reset_and_run_app("") # press any key to reset