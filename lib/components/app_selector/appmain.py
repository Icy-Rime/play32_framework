from graphic import framebuf_helper, pbm
from graphic.bmfont import get_text_lines, get_text_width
from play32sys import path, app, battery
from play32sys.sys_config import get_sys_config
from play32hw import cpu
import ujson, uos, framebuf
import hal_screen, hal_keypad, hal_battery, hal_sdcard
from utime import ticks_ms, ticks_diff, ticks_add
from buildin_resource.font import get_font_8px
from components.app_selector import settings

MANIFEST_FILE = "manifest.json"
MANIFEST_KEY_NAME = "name"
MANIFEST_KEY_ICON = "icon"
SCREEN_FORMAT = hal_screen.get_format()
COLOR_WHITE = framebuf_helper.get_white_color(SCREEN_FORMAT)
FONT_8 = get_font_8px()
SCR_W, SCR_H = hal_screen.get_size()
FNT_W, FNT_H = FONT_8.get_font_size()
ICON_SIZE_W, ICON_SIZE_H = (48, 48)
DEFAULT_ICON_PATH = "images/fallback_icon.pbm"
DEFAULT_ICON_DATA = b'\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\xf0\xf0\x00\x00\x00\x03\x00\x0c\x00\x00\x00\x0c\x00\x02\x00\x00\x00\x10\x00\x01\x80\x00\x00 \x00\x00@\x00\x00@\x00\x00 \x00\x00@\x00\x00 \x00\x00\x80\x00\x00\x10\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00x\x00\x01\x00\x00\x00\xff\x80\x02\x00\x00\x01\xff\x80\x02\x00\x00\x01\xff\x80\x02\x00\x11\x03\xff\x80\x02\x00+\x87\xff\x80\x02\x00\'\x8f\xff\x00\x02\x00G\x9f\xff\x00\x02\x00\'\xbf\xff\x00\x02\x00\'\xff\xfc\x00\x02\x07\x97\xff\xe0\x00\x02\x07\xef\xff\x80\x00\x01\x03\xff\xff\xf0\x00\x01\x01\xff\xfe\x10\x00\x00\x80\x7f\xe0 \x00\x00\x80\xff\xff\xfc\x00\x00A\x7f\xff\xfe\x00\x00#\xff\xff\xfe\x00\x00\x10\x7f\xff\xff\x00\x00\x0c\xff\xff\xff\x80\x00\x01\xf9\xff\xff\x80\x00\x03\xf9\xfb\xff\xc0\x00\x03\xf9\xf9\xff\xc0\x00\x03\xf9\xf8\x7f\xe0\x00\x03\xf0\xf0\x00\x00\x00\x03\x800\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe4\r\x17\x8e\x00\x01\x94\x14\xa0\x92\x00\x00\xa4\x14\xe1\x02\x00\x00\xc4>#\xc4\x00\x00\x84" L\x00\x00\x87\xa2\xe0\x91\x80\x00\x00"\x03\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
MAX_NAME_LENGTH = (SCR_W - 2*FNT_W) // FNT_W
app_list = []
app_pointer = -1

def main():
    # init
    hal_screen.init()
    hal_keypad.init()
    hal_battery.init()
    init()
    load_app_list()
    render_point_app()
    # loop forever
    main_loop()
    # end

def init():
    pass

def load_app_list():
    global app_list, app_pointer
    app_list = []
    for info in uos.ilistdir(path.get_app_path("/")):
        file_name = info[0]
        file_type = info[1]
        if (not file_name.startswith(".")):
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
            w, h, _, data, _ = pbm.read_image(f)
            assert (w, h) == (ICON_SIZE_W, ICON_SIZE_H)
        return display_name, icon_path, framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    except:
        return display_name, DEFAULT_ICON_PATH, framebuf.FrameBuffer(bytearray(DEFAULT_ICON_DATA), 48, 48, framebuf.MONO_HLSB)

def render_point_app():
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    if app_pointer < 0:
        FONT_8.draw_on_frame("No Apps.", frame, 0, 0, COLOR_WHITE)
        FONT_8.draw_on_frame("Press B to enter FTP mode.", frame, 0, 8, COLOR_WHITE, SCR_W, SCR_H-8)
        hal_screen.refresh()
        return
    app_name = app_list[app_pointer]
    display_name, _, display_icon = get_app_info(app_name)
    # draw arrows
    offset_x_arrows_right = SCR_W - FONT_8.get_char_width(b">"[0])
    FONT_8.draw_on_frame("<", frame, 0, 24, COLOR_WHITE)
    FONT_8.draw_on_frame(">", frame, offset_x_arrows_right, 24, COLOR_WHITE)
    # draw app_name
    display_name_lines = get_text_lines(display_name, FONT_8, SCR_W, FNT_H)
    if len(display_name_lines) > 0:
        display_name = display_name[:display_name_lines[0]]
    width_display_name = get_text_width(display_name, FONT_8)
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
    frame.rect(offset_x_clear, 0, width_clear, FNT_H, 0, True)
    FONT_8.draw_on_frame(battery_level, frame, offset_x_battery_level, 0, COLOR_WHITE)

def render_loading():
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    width_text = get_text_width("loading", FONT_8)
    FONT_8.draw_on_frame("loading", frame, (SCR_W - width_text) // 2, (SCR_H - FNT_H) // 2, COLOR_WHITE)
    hal_screen.refresh()

def run_app():
    if app_pointer < 0:
        return
    app_name = app_list[app_pointer]
    _, display_icon_path, _ = get_app_info(app_name)
    if display_icon_path == DEFAULT_ICON_PATH:
        app.clear_boot_image()
    else:
        app.set_boot_image(display_icon_path)
    app.reset_and_run_app(app_name)

def main_loop():
    import gc
    global app_pointer
    get_key_event = hal_keypad.get_key_event
    parse_key_event = hal_keypad.parse_key_event
    KEY_LEFT = hal_keypad.KEY_LEFT
    KEY_RIGHT = hal_keypad.KEY_RIGHT
    KEY_A = hal_keypad.KEY_A
    KEY_B = hal_keypad.KEY_B
    t_update_battery_ms = ticks_ms()
    if not path.exist("/framework_debug") and not get_sys_config("debug"):
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
                    SIZE = len(app_list)
                    if SIZE > 0:
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
                        hal_sdcard.init()
                        hal_sdcard.mount()
                        gc.collect()
                        settings.main()
                        gc.collect()
                        load_app_list()
                        render_point_app()
                        render_battery_level()
                        t_update_battery_ms = ticks_ms()
                        should_refresh_screen = True
                        gc.collect()
        if ticks_diff(ticks_ms(), t_update_battery_ms) >= 500:
            t_update_battery_ms = ticks_add(t_update_battery_ms, 500)
            with cpu.cpu_speed_context(cpu.FAST):
                render_battery_level()
            should_refresh_screen = True
        else:
            battery.measure()
        if should_refresh_screen:
            hal_screen.refresh()
