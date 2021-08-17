from graphic import pbm, framebuf_helper
from play32sys import path, app, battery
from play32hw import cpu
import framebuf, ujson, uos
import hal_screen, hal_keypad, hal_battery
from resource.font import get_font_8px
from utime import ticks_ms, ticks_diff, ticks_add
FONT_8 = get_font_8px()
MANIFEST_FILE = "manifest.json"
MANIFEST_KEY_NAME = "name"
MANIFEST_KEY_ICON = "icon"
SCREEN_FORMAT = hal_screen.get_format()
COLOR_WHITE = framebuf_helper.get_white_color(SCREEN_FORMAT)
ICON_SIZE_W, ICON_SIZE_H = (48, 48)
SCR_W, SCR_H = hal_screen.get_size()
FNT_W, FNT_H = FONT_8.get_font_size()

THIS_APP_NAME = "app_selector"
DEFAULT_ICON = None
app_list = []
app_pointer = -1

def main(app_name, *args, **kws):
    # init
    global THIS_APP_NAME
    THIS_APP_NAME = app_name
    hal_screen.init()
    hal_keypad.init()
    hal_battery.init()
    init()
    render_point_app()
    # loop forever
    main_loop()
    # end

def init():
    global DEFAULT_ICON, app_list, app_pointer
    with open(path.join(path.get_component_path(THIS_APP_NAME), "images", "fallback_icon.pbm"), "rb") as f:
        w, h, _, data, = pbm.read_image(f)[:4]
    assert (w, h) == (ICON_SIZE_W, ICON_SIZE_H)
    DEFAULT_ICON = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    DEFAULT_ICON = framebuf_helper.ensure_same_format(DEFAULT_ICON, framebuf.MONO_HLSB, w, h, SCREEN_FORMAT, COLOR_WHITE)
    app_list = []
    for info in uos.ilistdir(path.get_app_path("/")):
        file_name = info[0]
        file_type = info[1]
        if (file_type == path.FILE_TYPE_DIR) and (file_name != THIS_APP_NAME):
            app_list.append(file_name)
    app_list.sort()
    if len(app_list) <= 0:
        app_pointer = -1
    else:
        app_pointer = 0

def get_app_info(app_name):
    app_path = path.get_app_path(app_name)
    manifest_path = path.join(app_path, MANIFEST_FILE)
    display_name = app_name
    try:
        with open(manifest_path, "rb") as f:
            manifest = ujson.load(f)
        display_name = manifest[MANIFEST_KEY_NAME]
        icon_path = path.join(app_path, manifest[MANIFEST_KEY_ICON])
        with open(icon_path, "rb") as f:
            w, h, _, data, = pbm.read_image(f)[:4]
        assert (w, h) == (ICON_SIZE_W, ICON_SIZE_H)
        icon = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
        icon = framebuf_helper.ensure_same_format(icon, framebuf.MONO_HLSB, w, h, SCREEN_FORMAT, COLOR_WHITE)
        return display_name, icon
    except:
        return display_name, DEFAULT_ICON

def render_point_app():
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    if app_pointer < 0:
        FONT_8.draw_on_frame("No Apps.", frame, 0, 0, COLOR_WHITE)
        FONT_8.draw_on_frame("Press B to enter FTP mode.", frame, 0, 8, COLOR_WHITE, SCR_W, SCR_H-8)
        hal_screen.refresh()
        return
    app_name = app_list[app_pointer]
    display_name, display_icon = get_app_info(app_name)
    # draw arrows
    offset_x_arrows_right = SCR_W - FNT_W
    FONT_8.draw_on_frame("<", frame, 0, 24, COLOR_WHITE)
    FONT_8.draw_on_frame(">", frame, offset_x_arrows_right, 24, COLOR_WHITE)
    # draw app_name
    width_display_name = FNT_W * len(display_name)
    offset_x_display_name = (SCR_W - width_display_name) // 2
    FONT_8.draw_on_frame(display_name, frame, offset_x_display_name, 56, COLOR_WHITE)
    # draw icon
    offset_x_icon = (SCR_W - ICON_SIZE_W) // 2
    frame.blit(display_icon, offset_x_icon, 0)

def render_battery_level():
    frame = hal_screen.get_framebuffer()
    battery_level = str(battery.get_battery_level())
    width_battery_level = FNT_W * len(battery_level)
    offset_x_battery_level = SCR_W - width_battery_level
    width_clear = FNT_W * 3 # 100 battery
    offset_x_clear = SCR_W - width_clear
    frame.fill_rect(offset_x_clear, 0, width_clear, FNT_H, 0)
    FONT_8.draw_on_frame(battery_level, frame, offset_x_battery_level, 0, COLOR_WHITE)

def render_loading():
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    width_text = FNT_W * len("loading")
    FONT_8.draw_on_frame("loading", frame, (SCR_W - width_text) // 2, (SCR_H - FNT_H) // 2, COLOR_WHITE)
    hal_screen.refresh()

def run_app():
    if app_pointer < 0:
        return
    app_name = app_list[app_pointer]
    display_name, display_icon = get_app_info(app_name)
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    # draw icon
    offset_x_icon = (SCR_W - ICON_SIZE_W) // 2
    offset_y_icon = (SCR_H - ICON_SIZE_H) // 2
    frame.blit(display_icon, offset_x_icon, offset_y_icon)
    hal_screen.refresh()
    # reset and run
    app.disable_boot_image()
    app.reset_and_run_app(app_name)

def main_loop():
    global app_pointer
    get_key_event = hal_keypad.get_key_event
    parse_key_event = hal_keypad.parse_key_event
    KEY_LEFT = hal_keypad.KEY_LEFT
    KEY_RIGHT = hal_keypad.KEY_RIGHT
    KEY_A = hal_keypad.KEY_A
    KEY_B = hal_keypad.KEY_B
    SIZE = len(app_list)
    t_update_battery_ms = ticks_ms()
    cpu.set_cpu_speed(cpu.VERY_SLOW)
    while True:
        should_refresh_screen = False
        for event in get_key_event():
            event_type, key = parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                if key == KEY_LEFT:
                    app_pointer -= 1
                if key == KEY_RIGHT:
                    app_pointer += 1
                # ensure pointer
                if key == KEY_LEFT or key == KEY_RIGHT:
                    if 0 > app_pointer or SIZE <= app_pointer:
                        app_pointer = (app_pointer + SIZE) % SIZE
                    with cpu.cpu_speed_context(cpu.FAST):
                        render_point_app()
                        render_battery_level()
                    should_refresh_screen = True
                if key == KEY_A:
                    with cpu.cpu_speed_context(cpu.FAST):
                        run_app()
                if key == KEY_B:
                    # entering setup mode
                    with cpu.cpu_speed_context(cpu.FAST):
                        render_loading()
                        app.call_component("ftp_mode")
                        render_point_app()
                        render_battery_level()
                        t_update_battery_ms = ticks_ms()
                        should_refresh_screen = True
                        import gc
                        gc.collect()
                        # app.reset_and_run_app("") # reset
        if ticks_diff(ticks_ms(), t_update_battery_ms) >= 5000:
            t_update_battery_ms = ticks_add(t_update_battery_ms, 5000)
            with cpu.cpu_speed_context(cpu.FAST):
                render_battery_level()
            should_refresh_screen = True
        else:
            battery.measure()
        if should_refresh_screen:
            hal_screen.refresh()
