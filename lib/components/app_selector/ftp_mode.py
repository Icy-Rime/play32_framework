from play32sys import network_helper, app
from net import microftpd
import hal_keypad, hal_screen
from graphic import framebuf_helper
import utime
COLOR_WHITE = framebuf_helper.get_white_color(hal_screen.get_format())

class ScropedFTPClientInterface(microftpd.DefaultClientInterface):
    def valid_path(self, path:str):
        if path == "/":
            return True
        if path.startswith("/apps") or path.startswith("/data") or path.startswith("/resource") or path.startswith("/sd") or path.startswith("/tmp"):
            return True
        return False

def main():
    hal_screen.init()
    hal_keypad.init()
    network_helper.deactive_all()
    hal_screen.get_framebuffer().fill(0)
    hal_screen.get_framebuffer().text("FTP MODE", 0, 0, COLOR_WHITE)
    hal_screen.refresh()
    utime.sleep_ms(1000)
    ftp = microftpd.FTPServer()
    ftp.set_client_interface_class(ScropedFTPClientInterface)
    try:
        ap = network_helper.ap("Play32AP", "12345678")
        wlan = network_helper.connect()
    except Exception as e:
        import usys
        usys.print_exception(e)
        hal_screen.get_framebuffer().fill(0)
        hal_screen.get_framebuffer().text("Error...", 0, 0, COLOR_WHITE)
        hal_screen.get_framebuffer().text("Exiting...", 0, 16, COLOR_WHITE)
        hal_screen.refresh()
        utime.sleep_ms(2000)
        app.reset_and_run_app("")
        return
    wlan_connected = wlan.isconnected()
    def start():
        frame = hal_screen.get_framebuffer()
        frame.fill(0)
        frame.text("\"B\" EXIT", 0, 0, COLOR_WHITE)
        frame.text("-Port 21", 0, 40, COLOR_WHITE)
        if wlan.isconnected():
            frame.text("-WIFI:", 0, 8, COLOR_WHITE)
            frame.text("Your WIFI", 0, 16, COLOR_WHITE)
            frame.text("-PASSWD:", 0, 24, COLOR_WHITE)
            frame.text("Your pass", 0, 32, COLOR_WHITE)
            frame.text(wlan.ifconfig()[0], 0, 48, COLOR_WHITE)
            ip = wlan.ifconfig()[0]
        else:
            frame.text("-WIFI:", 0, 8, COLOR_WHITE)
            frame.text("Play32AP", 0, 16, COLOR_WHITE)
            frame.text("-PASSWD:", 0, 24, COLOR_WHITE)
            frame.text("12345678", 0, 32, COLOR_WHITE)
            frame.text(ap.ifconfig()[0], 0, 48, COLOR_WHITE)
            ip = ap.ifconfig()[0]
        ftp.deinit()
        ftp.set_host(ip)
        ftp.init()
        hal_screen.refresh()
    start()
    _loop = True
    while _loop:
        try:
            ftp.loop()
        except Exception as e:
            import usys
            usys.print_exception(e)
            hal_screen.get_framebuffer().fill(0)
            hal_screen.get_framebuffer().text("Error...", 0, 0, COLOR_WHITE)
            hal_screen.get_framebuffer().text("Exiting...", 0, 16, COLOR_WHITE)
            hal_screen.refresh()
            utime.sleep_ms(2000)
            ftp.deinit()
            wlan.disconnect()
            _loop = False # exit
        if wlan.isconnected() != wlan_connected:
            wlan_connected = wlan.isconnected()
            start()
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                if key == hal_keypad.KEY_B:
                    ftp.deinit()
                    wlan.disconnect()
                    _loop = False # exit
        utime.sleep_ms(50) # other thread need time to run.
    network_helper.deactive_all()