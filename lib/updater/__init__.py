from micropython import const
from play32sys import path, network_helper
from net import microftpd
from graphic import framebuf_console, framebuf_helper, abmfont
import utime, uos, usys, uhashlib, machine
# screen console
import hal_screen, hal_keypad
hal_screen.init()
hal_keypad.init()
FONT_8X4 = abmfont.FontDrawSmallAscii()
WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
SCR_W, SCR_H = hal_screen.get_size()
console = framebuf_console.Console(
    hal_screen.get_framebuffer(), SCR_W, SCR_H,
    font_draw=FONT_8X4,
    color=WHITE,
    display_update_fun=lambda: hal_screen.refresh()
)

FRAMEMEWORK_PACK_PATH = "/tmp/framework.pack"
FRAMEMEWORK_PACK_HASH_PATH = "/tmp/framework.pack.sha256"
TYPE_FILE = const(0X00)
TYPE_DIR = const(0X01)
BUFFER_SIZE = const(4096)

def start_ftp():
    ap = network_helper.ap("Play32AP", "12345678")
    utime.sleep(1.0)
    ip = ap.ifconfig()[0]
    ftp = microftpd.FTPServer(ip)
    ftp.init()
    print("Connect to WIFI: Play32AP")
    console.log("Connect to WIFI: Play32AP")
    print("with password: 12345678")
    console.log("with password: 12345678")
    print("FTP started at {}:21".format(ip))
    console.log("FTP started at {}:21".format(ip))
    print("")
    console.log("")
    print("Put framework.pack and sha256 file into /tmp .")
    console.log("Put framework.pack and sha256 file into /tmp .")
    print("Press A+B to update.")
    console.log("Press A+B to update.")
    is_key_pressed = hal_keypad.is_key_pressed
    KEY_A = hal_keypad.KEY_A
    KEY_B = hal_keypad.KEY_B
    while True:
        # key event
        if is_key_pressed(KEY_A) and is_key_pressed(KEY_B):
            try:
                if update_framework():
                    machine.reset()
            except:
                print("update failed. Please check your framework pack.")
                console.log("update failed. Please check your framework pack.")
        # serve ftp
        try:
            ftp.loop()
        except KeyboardInterrupt:
            return
        except Exception as e:
            usys.print_exception(e)

def check_update_file():
    try:
        with open(FRAMEMEWORK_PACK_HASH_PATH, "rb") as f:
            sha256_checksum = f.read()
        hasher = uhashlib.sha256()
        with open(FRAMEMEWORK_PACK_PATH, "rb") as f:
            part = f.read(4096)
            while len(part) > 0:
                hasher.update(part)
                part = f.read(4096)
        generated_checksum = hasher.digest()
        if sha256_checksum == generated_checksum:
            return True
        print(sha256_checksum, generated_checksum)
    except Exception as e:
        usys.print_exception(e)
    return False

def clear_root_dir():
    for file in uos.listdir("/"):
        if file not in ["resource", "data", "tmp", "apps"]:
            path.rmtree(path.join("/", file))

def __process_next_file_entry(dio, verbose=False):
    header = dio.read(6)
    if len(header) < 6:
        return False
    file_name_length = int.from_bytes(header[:2], "big")
    file_type = header[2]
    file_content_length = int.from_bytes(header[3:6], "big")
    file_name = dio.read(file_name_length).decode("utf8")
    if file_type == TYPE_DIR:
        if verbose:
            print("DIR: {}".format(file_name))
            console.log("DIR: {}".format(file_name))
        try:
            uos.mkdir(file_name)
        except: pass
    else:
        if verbose:
            print("FILE: {} SIZE: {}".format(file_name, file_content_length))
            console.log("FILE: {} SIZE: {}".format(file_name, file_content_length))
        with open(file_name, "wb") as f:
            count = 0
            buffer = bytearray(BUFFER_SIZE)
            while count + BUFFER_SIZE <= file_content_length:
                size = dio.readinto(buffer)
                f.write(buffer)
                f.flush()
                count += size
            count = file_content_length % BUFFER_SIZE
            if count > 0:
                size = dio.readinto(buffer, count)
                f.write(buffer[:count])
                f.flush()
    return True

def unpack_update_packet(verbose=False):
    with open(FRAMEMEWORK_PACK_PATH, "rb") as f:
        flag = __process_next_file_entry(f, verbose)
        while flag:
            flag = __process_next_file_entry(f, verbose)

def update_framework():
    print("Checking file sha256 checksum...")
    console.log("Checking file sha256 checksum...")
    if not check_update_file():
        print("Update files not correct.")
        console.log("Update files not correct.")
        return False
    print("Cleaning old files...")
    console.log("Cleaning old files...")
    clear_root_dir()
    print("Unpacking files...")
    console.log("Unpacking files...")
    unpack_update_packet(True)
    print("Updated.")
    console.log("Updated.")
    return True

def _on_enter_recovery_mode_():
    try:
        if update_framework():
            machine.reset()
    except Exception as e:
        usys.print_exception(e)
    start_ftp()
