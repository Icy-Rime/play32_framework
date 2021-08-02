import hal_screen, hal_keypad, utime, framebuf
from graphic import framebuf_console, framebuf_helper, pbm
from play32sys import app, path
from resource.font import get_font_8px
FONT_8 = get_font_8px()
WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
SCR_W, SCR_H = hal_screen.get_size()
console = framebuf_console.Console(
    hal_screen.get_framebuffer(), SCR_W // 2, SCR_H,
    font_draw=FONT_8,
    color=WHITE,
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
    # draw image
    image_path = path.join(path.get_app_path(app_name), "images", "dragon_bing_ling.pbm")
    with open(image_path, "rb") as f:
        res = pbm.read_image(f)
        iw = res[0]
        ih = res[1]
        idata = res[3]
        del res
    img = framebuf.FrameBuffer(idata, iw, ih, framebuf.MONO_HLSB)
    img = framebuf_helper.ensure_same_format(img, framebuf.MONO_HLSB, iw, ih, WHITE)
    ipos = ((((SCR_W // 2) - iw) // 2) + (SCR_W // 2), SCR_H - ih)
    frame = hal_screen.get_framebuffer()
    frame.fill_rect(ipos[0], ipos[1], iw, ih, 0)
    frame.blit(img, ipos[0], ipos[1], 0)
    hal_screen.refresh()
    main_loop()

def main_loop():
    while True:
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                console.log("Reboot..")
                app.reset_and_run_app("") # press any key to reset