import hal_screen, hal_keypad, hal_battery, usys
from graphic import framebuf_helper
from machine import freq
from play32sys import app, path, network_helper, battery
from utime import ticks_ms, ticks_diff, ticks_add
WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
W, H = hal_screen.get_size()
LINES = H // 8 # 8 line text

last_log = []
status = 0 # 0: main_menu 1: recording 2: show_record 3: apply successful 4: failed
# main_menu and recording
last_record_ms = 0
last_record_s = 0
record_path = "/data/test_battery/battery.log"
record_file = None
# show record
battery_level = []
top_battery_level = 0

def main(app_name, *args, **kws):
    global last_log, record_path
    # init log
    for _ in range(1024):
        last_log.append(hal_battery.get_raw_battery_value())
    app_data_path = path.get_data_path(app_name)
    app_tmp_path = path.get_tmp_path(app_name)
    record_path = path.join(app_data_path, "battery.log")
    path.mkdirs(app_data_path)
    path.mkdirs(app_tmp_path)
    # loop
    render_menu_and_recording()
    main_loop()

def convert_value_to_volt(value):
    return 11 * value / 4096 # 0-4095 across voltage range 0.0v - 1.0v

def measure():
    last_log.append(hal_battery.get_raw_battery_value())
    last_log.pop(0)

def record():
    global last_record_s
    if status == 1:
        last_record_s += 1
        value = sum(last_log) // len(last_log)
        record_file.write(int.to_bytes(value, 2, "big"))
        record_file.flush()

def generate_battery_level():
    if len(battery_level) == 100:
        return
    with open(record_path, "rb") as record_file:
        record_file.seek(0, 2)
        size = record_file.tell() // 2
        # 保留前5%和后5%作为保留电量
        reserved = size * 5 // 100
        avaliable_size = size - reserved - reserved
        for level in range(100):
            index = avaliable_size * level // 100
            index += reserved
            index %= size # limit index, prevent out of range
            record_file.seek(index*2)
            value = int.from_bytes(record_file.read(2), "big")
            battery_level.append(value)
        battery_level.reverse()

def apply_battery_record():
    assert len(battery_level) == 100
    with open(battery.BATTERY_RECORD_PATH, "wb") as f:
        for value in battery_level:
            f.write(int.to_bytes(value, 2, "big"))

def render_menu_and_recording():
    value = sum(last_log) // len(last_log)
    value_v = convert_value_to_volt(value)
    buffer = hal_screen.get_framebuffer()
    if status == 1:
        buffer.fill(WHITE)
        buffer.text("value: {:d}".format(value), 0, 0, 0)
        buffer.text("volt: {:.3f}V".format(value_v), 0, 8, 0)
        buffer.text("Recording...    ", 0, 16, 0)
        buffer.text("Please wait     ", 0, 24, 0)
        buffer.text("until LOW POWER.", 0, 32, 0)
        buffer.text("Time: {:d}s".format(last_record_s), 0, 48, 0)
    elif status == 0:
        buffer.fill(0)
        buffer.text("value: {:d}".format(value), 0, 0, WHITE)
        buffer.text("volt: {:.3f}V".format(value_v), 0, 8, WHITE)
        buffer.text("Press A to start", 0, 16, WHITE)
        buffer.text("record when full", 0, 24, WHITE)
        buffer.text("charged.        ", 0, 32, WHITE)
        buffer.text("B: Exit         ", 0, 40, WHITE)
        buffer.text("UP: Print record", 0, 48, WHITE)
        buffer.text("DOWN: apply REC ", 0, 56, WHITE)
    hal_screen.refresh()

def render_loading(text=""):
    buffer = hal_screen.get_framebuffer()
    buffer.fill(0)
    buffer.text("Loading...      ", 0, 0, WHITE)
    buffer.text(text, 0, 8, WHITE)
    hal_screen.refresh()

def render_battery_level_list():
    buffer = hal_screen.get_framebuffer()
    buffer.fill(0)
    btl = len(battery_level)
    for i in range(LINES):
        level = i + top_battery_level
        if level >= btl:
            continue
        level %= 100
        value = battery_level[level]
        buffer.text("{:d}> {:d} {:.3f}V".format(level, value, convert_value_to_volt(value)), 0, i*8, WHITE)
    hal_screen.refresh()

def render_success():
    buffer = hal_screen.get_framebuffer()
    buffer.fill(0)
    buffer.text("successful!", 0, 0, WHITE)
    hal_screen.refresh()

def render_failed():
    buffer = hal_screen.get_framebuffer()
    buffer.fill(0)
    buffer.text("successful!", 0, 0, WHITE)
    hal_screen.refresh()

def main_loop():
    global record_file, last_record_ms, status, top_battery_level
    while True:
        # 处理按键事件
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            # 按键按下事件
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                # main menu
                if status == 0:
                    try:
                        if key == hal_keypad.KEY_B:
                            # B 键重启到主菜单
                            print("Reboot..")
                            app.reset_and_run_app("") # press B to reset
                        elif key == hal_keypad.KEY_A:
                            record_file = open(record_path, "wb")
                            # max power!
                            freq(240_000_000)
                            network_helper.ap("Play32AP", "12345678")
                            status = 1
                        elif key == hal_keypad.KEY_UP:
                            render_loading()
                            generate_battery_level()
                            status = 2
                            continue
                        elif key == hal_keypad.KEY_DOWN:
                            render_loading()
                            generate_battery_level()
                            apply_battery_record()
                            status = 3
                            continue
                    except:
                        status = 4
                        continue
                if status == 2:
                    if key == hal_keypad.KEY_B:
                        status = 0
                    elif key == hal_keypad.KEY_UP or key == hal_keypad.KEY_DOWN:
                        top_battery_level += LINES if key == hal_keypad.KEY_DOWN else -LINES
                        tbl = len(battery_level)
                        last_offset = LINES if tbl % LINES == 0 else tbl % LINES
                        top_battery_level = 0 if top_battery_level >= tbl else top_battery_level
                        top_battery_level = tbl - last_offset if top_battery_level < 0 else top_battery_level
                if status == 3 or status == 4:
                    if key == hal_keypad.KEY_A or key == hal_keypad.KEY_B:
                        status = 0
        # 测量
        measure()
        # 渲染
        if status == 0 or status == 1:
            # 每秒记录并更新屏幕
            if ticks_diff(ticks_ms(), last_record_ms) >= 1000:
                last_record_ms = ticks_add(last_record_ms, 1000)
                record()
                render_menu_and_recording()
        elif status == 2:
            render_battery_level_list()
        elif status == 3:
            render_success()
        elif status == 4:
            render_failed()
