import gc
from ui.select import select_list
from ui.progress import progress_gen
from ui.input_text import input_text
from ui.dialog import dialog
import hal_network
from play32sys.sys_config import get_sys_config, set_sys_config, save_sys_config
from utime import ticks_ms, ticks_diff
from components.app_selector import ftp_mode

def wifi_menu():
    wlan = hal_network.get_wlan()
    while True:
        gc.collect()
        # sel = select_list("WIFI", ["SSID", "Password", "Connect", "Info", "Disconnect"])
        sel = select_list("WIFI", ["SSID", "Password"])
        if sel < 0:
            return
        elif sel == 0:
            pg = progress_gen("Scaning...", "SSID")
            next(pg)
            wlan.active(True)
            wifis = []
            for info in wlan.scan():
                try:
                    name = info[0].decode("utf-8") # type: bytes
                except:
                    name = "[BAD_SSID]"
                wifis.append(name)
            sel = select_list("SSID", wifis)
            if sel < 0:
                continue
            ssid = wifis[sel]
            if ssid == "[BAD_SSID]":
                continue
            set_sys_config("wifi_ssid", ssid)
            save_sys_config()
        elif sel == 1:
            pwd = get_sys_config("wifi_pass", "")
            pwd = input_text(pwd, "Password")
            set_sys_config("wifi_pass", pwd)
            save_sys_config()
        elif sel == 2:
            start_time = ticks_ms()
            pg = progress_gen("Connecting...", "WIFI")
            next(pg)
            hal_network.connect()
            while not wlan.isconnected():
                next(pg)
                if ticks_diff(ticks_ms(), start_time) > 10000:
                    # wait 10 s to connect
                    break
        elif sel == 3:
            if not wlan.isconnected():
                dialog("Not Connected.")
            else:
                info = wlan.ifconfig()
                dialog(f"IP: {info[0]}\nGW: {info[2]}\nDNS: {info[3]}\nSUB: {info[1]}")
        elif sel == 4:
            pg = progress_gen("Disconnecting...", "WIFI")
            next(pg)
            if (wlan.active()):
                wlan.disconnect()
            next(pg)
            wlan.active(False)

def settings_menu():
    while True:
        gc.collect()
        sel = select_list("Settings", ["WIFI", "FTP Mode"])
        if sel < 0:
            return
        elif sel == 0:
            wifi_menu()
        elif sel == 1:
            gc.collect()
            pg = progress_gen("Loading...", "FTP Mode")
            next(pg)
            try:
                ftp_mode.main()
            except:
                dialog("Failed to start FTP Mode.")

def main():
    settings_menu()
    