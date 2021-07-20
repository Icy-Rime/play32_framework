import hal_screen, hal_keypad, hal_led, utime
from graphic import framebuf_helper
from play32sys import app
WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
W, H = hal_screen.get_size()
HOLD_REPEAT_TIME_MS = 200

color = [0, 0, 0]
hold_value = 0
hold_timer = 0
point = 0

def main(app_name, *args, **kws):
    render()
    main_loop()

def render():
    # 一行文字有3*3，framebuf的text默认8x8
    # 一列文字有3个，两个光标指示器，一个数值，间隔4pix
    require_pixel_w = 3 * 3 * 8
    require_pixel_h = 3 * 8 + 8
    start_y = (H - require_pixel_h) // 2
    space_x = (W - require_pixel_w) // 4
    start_x = space_x
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    for i in range(3):
        text = "{:^ 3}".format(color[i])
        frame.text(text, start_x, start_y + 12, WHITE)
        if point == i:
            frame.text(" + ", start_x, start_y, WHITE)
            frame.text(" - ", start_x, start_y + 24, WHITE)
        start_x += space_x + 24
    hal_screen.refresh()


def hold_event():
    global hold_timer
    if hold_value == 0:
        return
    now = utime.ticks_ms()
    if utime.ticks_diff(now, hold_timer) > 0:
        color[point] += hold_value
        color[point] %= 256
        hold_timer += HOLD_REPEAT_TIME_MS

def main_loop():
    global point, hold_value, hold_timer
    while True:
        # 备份参考对象
        color_copy = list(color)
        # 处理按键事件
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            # 按键按下事件
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                if key == hal_keypad.KEY_LEFT or key == hal_keypad.KEY_RIGHT:
                    point += 1 if key == hal_keypad.KEY_RIGHT else -1
                    point %= 3 # 确保point在0到2之间
                    hold_value = 0 # 取消按住按键的变化
                elif key == hal_keypad.KEY_UP or key == hal_keypad.KEY_DOWN:
                    hold_value += 1 if key == hal_keypad.KEY_UP else -1
                    # # 执行一次
                    # color[point] += hold_value
                    # color[point] %= 256
                    # 保持按住的状态的话，会在一定时间后继续执行
                    hold_timer = utime.ticks_ms()
                elif key == hal_keypad.KEY_B:
                    # B 键重启到主菜单
                    print("Reboot..")
                    app.reset_and_run_app("") # press B to reset
            elif key == hal_keypad.KEY_UP or key == hal_keypad.KEY_DOWN:
                # 按键松开事件，取消按住按键状态
                hold_value = 0
        # 执行按键按住事件
        hold_event()
        # 输出值到led
        if color_copy != color:
            hal_led.set_color(*color)
        del color_copy
        # 绘制屏幕
        render()
