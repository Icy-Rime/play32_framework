from graphic import framebuf_helper
from play32sys import path, app, battery
from play32hw import cpu
import ujson, uos
import hal_screen, hal_keypad, hal_battery, hal_sdcard
from utime import ticks_ms, ticks_diff, ticks_add
from graphic.widget import FixedLayout, PBMImage, ScrollText, Text
from graphic.layout import ALIGN_CENTER, DIRECTION_HORIZONTAL, DIRECTION_VERTICAL, box_align
from buildin_resource.font import get_font_8px

MANIFEST_FILE = "manifest.json"
MANIFEST_KEY_NAME = "name"
MANIFEST_KEY_ICON = "icon"
SCREEN_FORMAT = hal_screen.get_format()
COLOR_WHITE = framebuf_helper.get_white_color(SCREEN_FORMAT)
SCR_W, SCR_H = hal_screen.get_size()

THIS_APP_NAME = "app_selector"
DEFAULT_ICON_PATH = "images/fallback_icon.pbm"
main_layout:FixedLayout = None
loading_text:Text = None
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
    load_app_list()
    render_point_app(True)
    # loop forever
    main_loop()
    # end

def init():
    global DEFAULT_ICON_PATH, main_layout, loading_text
    DEFAULT_ICON_PATH = path.join(path.get_component_path(THIS_APP_NAME), "images", "fallback_icon.pbm")
    frame = hal_screen.get_framebuffer()
    full_box = (0, 0, SCR_W, SCR_H)
    main_layout = FixedLayout()
    main_layout.set_frame(frame)
    main_layout.set_box(full_box)
    main_layout.set_direction(DIRECTION_VERTICAL)
    main_layout.set_start(2)
    main_layout.set_end(8)
    view = Text()
    view.set_id("battery")
    main_layout.append_child(view)
    inner_layout = FixedLayout()
    inner_layout.set_direction(DIRECTION_HORIZONTAL)
    inner_layout.set_start(8)
    inner_layout.set_end(8)
    view = Text()
    view.set_color(COLOR_WHITE)
    view.set_text("<")
    inner_layout.append_child(view)
    view = PBMImage()
    view.set_id("app_icon")
    view.set_key_color(0)
    view.set_background(0)
    inner_layout.append_child(view)
    view = Text()
    view.set_color(COLOR_WHITE)
    view.set_text(">")
    inner_layout.append_child(view)
    main_layout.append_child(inner_layout)
    font = get_font_8px()
    view = ScrollText()
    view.set_id("app_name")
    view.set_font(font)
    view.set_color(COLOR_WHITE)
    main_layout.append_child(view)
    loading_text = Text()
    loading_text.set_frame(frame)
    loading_text.set_box(full_box)
    loading_text.set_text("Loading...")

def load_app_list():
    global app_list, app_pointer
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
        return display_name, icon_path
    except:
        return display_name, DEFAULT_ICON_PATH

def render_point_app(full=False):
    if app_pointer < 0:
        frame = hal_screen.get_framebuffer()
        FONT_8 = get_font_8px()
        FONT_8.draw_on_frame("No Apps.", frame, 0, 0, COLOR_WHITE)
        FONT_8.draw_on_frame("Press B to enter FTP mode.", frame, 0, 8, COLOR_WHITE, SCR_W, SCR_H-8)
        hal_screen.refresh()
        return
    if main_layout == None:
        return
    app_name = app_list[app_pointer]
    display_name, display_icon = get_app_info(app_name)
    img_view:PBMImage = main_layout.find_child_by_id("app_icon")
    img_view.set_src(display_icon)
    name_view:ScrollText = main_layout.find_child_by_id("app_name")
    name_view.set_text(display_name)
    if full:
        main_layout.render()
    else:
        img_view.render()
        name_view.render()

def render_battery_level():
    battery_level = battery.get_battery_level()
    if main_layout == None or battery_level < 0:
        return
    frame = hal_screen.get_framebuffer()
    battery_view:Text = main_layout.find_child_by_id("battery")
    box = battery_view._box
    x, y, w, h = box
    frame.fill_rect(x, y, w, h, 0)
    batt_bar_box = (0, 0, box[2]*battery_level//100, box[3])
    x, y, w, h = box_align(batt_bar_box, box, ALIGN_CENTER, ALIGN_CENTER)
    frame.fill_rect(x, y, w, h, COLOR_WHITE)

def render_loading():
    if loading_text != None:
        loading_text.render()
    hal_screen.refresh()

def run_app():
    if app_pointer < 0:
        return
    app_name = app_list[app_pointer]
    _, display_icon = get_app_info(app_name)
    app.set_boot_image(display_icon)
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
                        app.call_component("ftp_mode")
                        gc.collect()
                        load_app_list()
                        render_point_app(True)
                        render_battery_level()
                        t_update_battery_ms = ticks_ms()
                        should_refresh_screen = True
                        import gc
                        gc.collect()
                        # app.reset_and_run_app("") # reset
        if ticks_diff(ticks_ms(), t_update_battery_ms) >= 500:
            t_update_battery_ms = ticks_add(t_update_battery_ms, 500)
            with cpu.cpu_speed_context(cpu.FAST):
                render_battery_level()
                if main_layout != None:
                    main_layout.animation()
            should_refresh_screen = True
        else:
            battery.measure()
        if should_refresh_screen:
            hal_screen.refresh()
