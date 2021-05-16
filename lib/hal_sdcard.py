# sdcard
import machine, os #, sdcard
def init_sdcard():
    # hspi = machine.SPI(2, baudrate=80000000)
    # sd = sdcard.SDCard(hspi, machine.Pin(22))
    sd = machine.SDCard(
        slot=3,
        width=1,
        sck=machine.Pin(18),
        miso=machine.Pin(19),
        mosi=machine.Pin(23),
        cs=machine.Pin(22),
        # freq=80000000
    )
    os.mount(sd, '/sd')

def get_sdcard_path():
    return '/sd'
