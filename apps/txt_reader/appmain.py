from play32sys import path, battery
from play32hw import cpu
from micropython import const
from machine import lightsleep
import uos
import hal_screen, hal_keypad, hal_battery
import book_reader, book_ui

CPU_CONTEXT_FAST = cpu.cpu_speed_context(cpu.FAST)
CPU_CONTEXT_SLOW = cpu.cpu_speed_context(cpu.FAST)

# const
STATUS_MENU = const(0)
STATUS_READER = const(1)

# status
status = STATUS_MENU
reader = None

# operation
def main(app_name, *args, **kws):
    global status, reader
    hal_screen.init()
    hal_keypad.init()
    hal_battery.init()
    reader = book_reader.BookReader()
    book_ui.render_loading("加载书签")
    # 加载文件
    data_dir = path.get_data_path(app_name)
    if not path.exist(data_dir):
        path.mkdirs(data_dir)
    txt_file_path = None
    for info in uos.ilistdir(data_dir):
        f_name = info[0]
        if f_name.endswith(".txt") or f_name.endswith(".TXT"):
            txt_file_path = path.join(data_dir, f_name)
    if txt_file_path == None:
        book_ui.render_loading("找不到文本文件")
        return
    reader.load_book(txt_file_path)
    # 进入主循环
    reader.render()
    status = STATUS_READER
    main_loop()

def main_loop():
    global status
    # hal_keypad.enable_wake_on_press0(hal_keypad.KEY_RIGHT)
    # hal_keypad.enable_wake_on_press1([hal_keypad.KEY_DOWN])
    battery.init_battery_value_cache(256) # smaller buffer
    with CPU_CONTEXT_SLOW:
        while True:
            if status == STATUS_MENU:
                pass
            elif status == STATUS_READER:
                for event in hal_keypad.get_key_event():
                    event_type, key = hal_keypad.parse_key_event(event)
                    if event_type != hal_keypad.EVENT_KEY_PRESS:
                        continue
                    if key == hal_keypad.KEY_UP or key == hal_keypad.KEY_DOWN or key == hal_keypad.KEY_LEFT or key == hal_keypad.KEY_RIGHT:
                        with CPU_CONTEXT_FAST:
                            page_offset = 1 if key == hal_keypad.KEY_DOWN or key == hal_keypad.KEY_RIGHT else -1
                            reader.flip_page_by(page_offset)
                            reader.render()
                    elif key == hal_keypad.KEY_A:
                        book_ui.render_status(battery.get_battery_level(), reader.bookmark_load_progress)
                        lightsleep(1000)
                        reader.render()
                    hal_keypad.clear_key_status([key])
            if (reader != None) and (not reader.bookmark_loaded):
                with CPU_CONTEXT_FAST:
                    reader.load_bookmark(8)
            else:
                lightsleep(50)
            battery.measure()
