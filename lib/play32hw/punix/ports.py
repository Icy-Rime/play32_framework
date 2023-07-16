from play32hw.punix.hal_screen import deinit as scr_deinit
from play32hw.punix.hal_buzz import deinit as buzz_deinit
from play32hw.shared_timer import stop_all_timer
from utime import sleep_ms

def before_reset():
    scr_deinit()
    buzz_deinit()
    stop_all_timer()
    sleep_ms(500)