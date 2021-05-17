from graphic import pbm, framebuf_helper
from play32sys import path, app
import framebuf, ujson, uos
import hal_screen as screen
import hal_keypad as keypad
from resource.font import get_font_8px
FONT_8 = get_font_8px()
MANIFEST_FILE = "manifest.json"
MANIFEST_KEY_NAME = "name"
MANIFEST_KEY_ICON = "icon"
ICON_SIZE = (48, 48)
SCREEN_FORMAT = screen.get_format()
COLOR_WHITE = framebuf_helper.get_white_color(SCREEN_FORMAT)

THIS_APP_NAME = "app_selector"
DEFAULT_ICON = None
app_list = []
app_pointer = -1

def main(app_name, *args, **kws):
    # init
    global THIS_APP_NAME
    THIS_APP_NAME = app_name
    init()
    render_point_app()
    # loop forever
    main_loop()
    # end

def init():
    global DEFAULT_ICON, app_list, app_pointer
    with open(path.join(path.get_app_path(THIS_APP_NAME), "images", "fallback_icon.pbm"), "rb") as f:
        w, h, _, data, = pbm.read_image(f)[:4]
    assert (w, h) == ICON_SIZE
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
        assert (w, h) == ICON_SIZE
        icon = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
        icon = framebuf_helper.ensure_same_format(icon, framebuf.MONO_HLSB, w, h, SCREEN_FORMAT, COLOR_WHITE)
        return display_name, icon
    except:
        return display_name, DEFAULT_ICON

def render_point_app():
    if app_pointer < 0:
        return
    app_name = app_list[app_pointer]
    frame = screen.get_framebuffer()
    frame.fill(0)
    display_name, display_icon = get_app_info(app_name)
    # draw arrows
    offset_x_arrows_right = screen.get_size()[0] - FONT_8.get_font_size()[0]
    FONT_8.draw_on_frame("<", frame, 0, 24, COLOR_WHITE)
    FONT_8.draw_on_frame(">", frame, offset_x_arrows_right, 24, COLOR_WHITE)
    # draw app_name
    width_display_name = FONT_8.get_font_size()[0] * len(display_name)
    offset_x_display_name = (screen.get_size()[0] - width_display_name) // 2
    FONT_8.draw_on_frame(display_name, frame, offset_x_display_name, 56, COLOR_WHITE)
    # draw icon
    offset_x_icon = (screen.get_size()[0] - ICON_SIZE[0]) // 2
    frame.blit(display_icon, offset_x_icon, 0)
    screen.refresh()

def run_app():
    if app_pointer < 0:
        return
    app_name = app_list[app_pointer]
    display_name, display_icon = get_app_info(app_name)
    frame = screen.get_framebuffer()
    frame.fill(0)
    # draw icon
    offset_x_icon = (screen.get_size()[0] - ICON_SIZE[0]) // 2
    offset_y_icon = (screen.get_size()[1] - ICON_SIZE[1]) // 2
    frame.blit(display_icon, offset_x_icon, offset_y_icon)
    screen.refresh()
    # reset and run
    app.reset_and_run_app(app_name)

def main_loop():
    global app_pointer
    get_key_event = keypad.get_key_event
    parse_key_event = keypad.parse_key_event
    KEY_LEFT = keypad.KEY_LEFT
    KEY_RIGHT = keypad.KEY_RIGHT
    KEY_A = keypad.KEY_A
    SIZE = len(app_list)
    while True:
        for event in get_key_event():
            event_type, key = parse_key_event(event)
            if event_type == keypad.EVENT_KEY_PRESS:
                if key == KEY_LEFT:
                    app_pointer -= 1
                if key == KEY_RIGHT:
                    app_pointer += 1
                # ensure pointer
                if key == KEY_LEFT or key == KEY_RIGHT:
                    if 0 > app_pointer or SIZE <= app_pointer:
                        app_pointer = (app_pointer + SIZE) % SIZE
                    render_point_app()
                if key == KEY_A:
                    run_app()