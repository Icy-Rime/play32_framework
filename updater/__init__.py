from updater import path, microftpd
import network, utime, uos, usys, uhashlib, machine

FRAMEMEWORK_PACK_PATH = "/tmp/framework.pack"
FRAMEMEWORK_PACK_HASH_PATH = "/tmp/framework.pack.sha256"
TYPE_FILE = 0X00
TYPE_DIR = 0X01
BUFFER_SIZE = 4096

def connect_wifi(ssid, passwd, waiting=False):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, passwd)
        while waiting and not wlan.isconnected():
            pass
    return wlan

def setup_ap(ssid="Play32AP", passwd="12345678"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(dhcp_hostname="play32")
    ap.config(essid=ssid)
    ap.config(max_clients=16)
    ap.config(hidden=False)
    if passwd == None or passwd == "":
        ap.config(authmode=network.AUTH_OPEN)
    else:
        ap.config(password=passwd)
        ap.config(authmode=network.AUTH_WPA_WPA2_PSK)
    return ap

def start_ftp():
    ap = setup_ap("Play32AP", "12345678")
    utime.sleep(1.0)
    ip = ap.ifconfig()[0]
    ftp = microftpd.FTPServer(ip)
    ftp.init()
    print("Connect to WIFI: Play32AP")
    print("with password: 12345678")
    print("FTP started at {}:21".format(ip))
    while True:
        try:
            ftp.loop()
        except KeyboardInterrupt:
            return
        except Exception as e:
            usys.print_exception(e)

def start_ftp_on(ssid, passwd):
    print("Connecting WIFI...")
    wifi = connect_wifi(ssid, passwd, True)
    utime.sleep(1.0)
    ip = wifi.ifconfig()[0]
    ftp = microftpd.FTPServer(ip)
    ftp.init()
    print("FTP started at {}:21".format(ip))
    while True:
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
        if file not in ["updater", "data", "tmp", "apps", "boot.py", "main.py"]:
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
        try:
            uos.mkdir(file_name)
        except: pass
    else:
        if verbose:
            print("FILE: {} SIZE: {}".format(file_name, file_content_length))
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
    if not check_update_file():
        print("Update files not correct.")
        return
    print("Cleaning old files...")
    clear_root_dir()
    print("Unpacking files...")
    unpack_update_packet(True)
    print("Updated.")
    return True

def _on_enter_recovery_mode_():
    try:
        update_framework()
        machine.reset()
    except Exception as e:
        usys.print_exception(e)
    start_ftp()
