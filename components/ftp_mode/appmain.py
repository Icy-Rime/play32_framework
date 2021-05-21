from play32sys import network_helper
import hal_keypad as keypad
import hal_screen as screen
from graphic import framebuf_helper
import uftpd, utime
COLOR_WHITE = framebuf_helper.get_white_color(screen.get_format())

def main(app_name, *args, **kws):
    network_helper.deactive_all()
    screen.get_framebuffer().fill(0)
    screen.get_framebuffer().text("FTP MODE", 0, 0, COLOR_WHITE)
    screen.refresh()
    utime.sleep_ms(1000)
    try:
        ap = network_helper.ap("Play32AP", "12345678")
        wlan = network_helper.connect()
    except Exception as e:
        import usys
        usys.print_exception(e)
        screen.get_framebuffer().fill(0)
        screen.get_framebuffer().text("Error...", 0, 0, COLOR_WHITE)
        screen.get_framebuffer().text("Restart...", 0, 16, COLOR_WHITE)
        screen.refresh()
        utime.sleep_ms(2000)
        return
    wlan_connected = wlan.isconnected()
    def start():
        frame = screen.get_framebuffer()
        frame.fill(0)
        frame.text("\"B\" EXIT", 0, 0, COLOR_WHITE)
        frame.text("-WIFI:", 0, 8, COLOR_WHITE)
        frame.text("Play32AP", 0, 16, COLOR_WHITE)
        frame.text("-PASSWD:", 0, 24, COLOR_WHITE)
        frame.text("12345678", 0, 32, COLOR_WHITE)
        frame.text("-Port 21", 0, 40, COLOR_WHITE)
        frame.text(ap.ifconfig()[0], 0, 48, COLOR_WHITE)
        if wlan.isconnected():
            frame.text(wlan.ifconfig()[0], 0, 56, COLOR_WHITE)
        screen.refresh()
        uftpd.restart()
    start()
    _loop = True
    while _loop:
        for event in keypad.get_key_event():
            event_type, key = keypad.parse_key_event(event)
            if event_type == keypad.EVENT_KEY_PRESS:
                if key == keypad.KEY_B:
                    _loop = False # exit
        if wlan.isconnected() != wlan_connected:
            wlan_connected = wlan.isconnected()
            start()
        utime.sleep_ms(100)
    network_helper.deactive_all()