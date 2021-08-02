import usocket, uos, utime
from micropython import const
import gc

# typing
import socket

_BUFFER_SIZE = const(4096)
_BACKLOG = const(5)
_PORT_BASE = const(10000)
_PORT_LIMIT = const(65535)
_MAX_IDLE_TIME = const(60000)
_MAX_TRANSFER_TIME = const(2000)

DEBUG = False
WELCOME_MESSAGE = "Hello, this is Play32."
OK_250_MESSAGE = "250 OK\r\n"
FAIL_550_MESSAGE = "550 Failed\r\n"

class TrySocket():
    def __init__(self, sock:socket.socket, buffer_size=_BUFFER_SIZE):
        if sock != None:
            sock.setblocking(False)
        self.__s = sock
        self.__bfs = buffer_size
        self.__bf = b''
    
    def try_accept(self):
        try:
            return self.__s.accept()
        except:
            return None, None

    def try_read_socket(self):
        try:
            return self.__s.recv(self.__bfs)
        except:
            return b''
    
    def try_readline(self):
        bf = self.__bf + self.try_read_socket()
        index = bf.find(b'\n')
        line = None
        if index >= 0:
            line = bf[:index+1].strip().decode("utf8")
            bf = bf[index+1:]
        self.__bf = bf
        return line

    def is_closed(self):
        try:
            return self.__s.fileno() < 0
        except:
            return True

    def send_all(self, msg):
        if type(msg) == str:
            msg = msg.encode("utf8")
            if DEBUG:
                print("RSP:", msg.strip())
        else:
            if DEBUG:
                print("DATA:", msg)
        try:
            return self.__s.sendall(msg)
        except:
            return None

    def close(self):
        try:
            self.__s.close()
        except: pass

_port_index = _PORT_BASE

def get_a_port():
    global _port_index
    _port_index += 1
    if _port_index >= _PORT_LIMIT:
        _port_index = _PORT_BASE
    return _port_index

def send_list_data(path, dataclient, full):
    try:  # whether path is a directory name
        for fname in sorted(uos.listdir(path), key=str.lower):
            dataclient.send_all(make_description(path, fname, full))
    except:  # path may be a file name or pattern
        pattern = path.split("/")[-1]
        path = path[:-(len(pattern) + 1)]
        if path == "":
            path = "/"
        for fname in sorted(uos.listdir(path), key=str.lower):
            if fncmp(fname, pattern):
                dataclient.send_all(make_description(path, fname, full))

_month_name = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

def make_description(path, fname, full):
    if full:
        return make_description_linux(path, fname)
    else:
        return fname + "\r\n"

def make_description_linux(path, fname):
    stat = uos.stat(get_absolute_path(path, fname))
    file_permissions = ("drwxr-xr-x"
                        if (stat[0] & 0o170000 == 0o040000)
                        else "-rw-r--r--")
    file_size = stat[6]
    tm = stat[8] & 0xffffffff
    tm = utime.localtime(tm if tm < 0x80000000 else tm - 0x100000000)
    if tm[0] != utime.localtime()[0]:
        mtimestr = "{} {} {}".format(_month_name[tm[1]], tm[2], tm[0])
        description = "{} 1 owner group {} {} {} {} {}\r\n".\
            format(file_permissions, file_size,
                _month_name[tm[1]], tm[2], tm[0], fname)
    else:
        mtimestr = "{} {} {:02}:{:02}".format(_month_name[tm[1]], tm[2], tm[3], tm[4])
        description = "{} 1 owner group {} {} {} {:02}:{:02} {}\r\n".\
            format(file_permissions, file_size,
                _month_name[tm[1]], tm[2], tm[3], tm[4], fname)
    return "%s %3s %-8s %-8s %8s %s %s\r\n" % (
                file_permissions, 1, "owner", "group", file_size, mtimestr, fname
            )

def send_file_data(file, dataclient):
    chunk = file.read(_BUFFER_SIZE)
    while len(chunk) > 0:
        dataclient.send_all(chunk)
        chunk = file.read(_BUFFER_SIZE)


def save_file_data(file, dataclient):
    last_active_ms = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), last_active_ms) < _MAX_TRANSFER_TIME:
        chunk = dataclient.try_read_socket()
        if len(chunk) > 0:
            last_active_ms = utime.ticks_ms()
            file.write(chunk)


def get_absolute_path(cwd, payload):
    # Just a few special cases "..", "." and ""
    # If payload start"s with /, set cwd to /
    # and consider the remainder a relative path
    if payload.startswith("/"):
        cwd = "/"
    for token in payload.split("/"):
        if token == "..":
            if cwd != "/":
                cwd = "/".join(cwd.split("/")[:-1])
                if cwd == "":
                    cwd = "/"
        elif token != "." and token != "":
            if cwd == "/":
                cwd += token
            else:
                cwd = cwd + "/" + token
    return cwd


# compare fname against pattern. Pattern may contain
# wildcards ? and *.
def fncmp(fname, pattern):
    pi = 0
    si = 0
    while pi < len(pattern) and si < len(fname):
        if (fname[si] == pattern[pi]) or (pattern[pi] == "?"):
            si += 1
            pi += 1
        else:
            if pattern[pi] == "*":  # recurse
                if (pi + 1) == len(pattern):
                    return True
                while si < len(fname):
                    if fncmp(fname[si:], pattern[pi+1:]):
                        return True
                    else:
                        si += 1
                return False
            else:
                return False
    if pi == len(pattern.rstrip("*")) and si == len(fname):
        return True
    else:
        return False

class FTPServer():
    def __init__(self, host="192.168.4.1", port=21):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
    
    def set_host(self, host):
        self.host = host

    def init(self):
        if self.server_socket != None:
            try:
                self.server_socket.close()
            except: pass
        cmd_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        cmd_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        cmd_socket.bind(usocket.getaddrinfo(self.host, self.port)[0][4])
        cmd_socket.listen(_BACKLOG)
        self.server_socket = TrySocket(cmd_socket)

    def deinit(self):
        if self.server_socket != None:
            self.server_socket.close()
            self.server_socket = None
        for client in self.clients:
            client.close()
        self.clients.clear()

    def loop(self):
        client_socket, remote_addr = self.server_socket.try_accept()
        if client_socket != None:
            c = FTPServerClient(self.host, client_socket, remote_addr)
            self.clients.append(c)
        exit_client = []
        for client in self.clients:
            if client.is_closed():
                exit_client.append(client)
                continue
            client.loop()
        for c in exit_client:
            c.close()
            self.clients.remove(c)

    def run_forever(self):
        self.init()
        print("FTP Server started on", self.host)
        try:
            while True:
                try:
                    self.loop()
                except: pass
        except KeyboardInterrupt:
            pass

class FTPServerClient():
    def __init__(self, host, client_socket, remote_addr):
        self.host = host
        self.client_socket = TrySocket(client_socket)
        self.remote_addr = remote_addr
        self.buffer = "".split()
        self.cwd = "/"
        # self.loop()
        self.client_socket.send_all("220 {}\r\n".format(WELCOME_MESSAGE))
        self.data_port = get_a_port()
        data_server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        data_server.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        data_server.bind(usocket.getaddrinfo(self.host, self.data_port)[0][4])
        data_server.listen(_BACKLOG)
        self.data_server = TrySocket(data_server)
        self.data_client = None
        self.last_active = utime.ticks_ms()
        self.fromname = None

    def wait_data_client(self, timeout_ms=_MAX_TRANSFER_TIME):
        target_time = utime.ticks_add(utime.ticks_ms(), timeout_ms)
        data_socket, _ = self.data_server.try_accept()
        while data_socket == None and utime.ticks_diff(target_time, utime.ticks_ms()) > 0:
            data_socket, _ = self.data_server.try_accept()
        self.data_client = TrySocket(data_socket)

    def close_data_client(self):
        if self.data_client != None:
            self.data_client.close()
            self.data_client = None

    def close(self):
        self.client_socket.close()
        self.data_server.close()
        if self.data_client != None:
            self.data_client.close()
    
    def is_closed(self):
        return self.client_socket.is_closed()

    def loop(self):
        client_socket = self.client_socket
        data = client_socket.try_readline()
        if data == None:
            if utime.ticks_diff(utime.ticks_ms(), self.last_active) > _MAX_IDLE_TIME:
                self.close()
            return
        # CMD
        self.last_active = utime.ticks_ms()
        if DEBUG:
            print("CMD:", data)
        if len(data) <= 0:
            # No data, assume QUIT
            self.close()
            return
        command = data.split()[0].upper()
        payload = data[len(command):].lstrip()  # partition is missing
        path = get_absolute_path(self.cwd, payload)

        # check for log-in state may done here, like
        # if self.logged_in == False and not command in\
        #    ("USER", "PASS", "QUIT"):
        #    client_socket.send_all("530 Not logged in.\r\n")
        #    return

        if command == "USER":
            # self.logged_in = True
            client_socket.send_all("230 Logged in.\r\n")
            # If you want to see a password,return
            #   "331 Need password.\r\n" instead
            # If you want to reject an user, return
            #   "530 Not logged in.\r\n"
        elif command == "PASS":
            # you may check here for a valid password and return
            # "530 Not logged in.\r\n" in case it"s wrong
            # self.logged_in = True
            client_socket.send_all("230 Logged in.\r\n")
        elif command == "OPTS":
            # OPTS UTF8 ON
            client_socket.send_all("200 OK\r\n")
        elif command == "SYST":
            client_socket.send_all("215 UNIX Type: L8\r\n")
        elif command in ("NOOP", "ABOR"):  # just accept & ignore
            client_socket.send_all("200 OK\r\n")
        elif command == "FEAT":
             client_socket.send_all("211 no-features\r\n")
        elif command == "TYPE":
            client_socket.send_all("200 Transfer mode set\r\n")
        elif command == "QUIT":
            client_socket.send_all("221 Bye.\r\n")
            self.close()
        elif command == "PWD" or command == "XPWD":
            client_socket.send_all("257 \"{}\"\r\n".format(self.cwd))
        elif command == "CWD" or command == "XCWD":
            try:
                if (uos.stat(path)[0] & 0o170000) == 0o040000:
                    self.cwd = path
                    client_socket.send_all(OK_250_MESSAGE)
                else:
                    client_socket.send_all(FAIL_550_MESSAGE)
            except:
                client_socket.send_all(FAIL_550_MESSAGE)
        elif command == "PASV":
            self.close_data_client()
            client_socket.send_all("227 Entering Passive Mode ({},{},{}).\r\n".format(
                self.host.replace(".", ","),
                self.data_port >> 8, self.data_port % 256)
            )
        elif command == "LIST" or command == "NLST":
            if not payload.startswith("-"):
                place = path
            else:
                place = self.cwd
            try:
                self.wait_data_client()
                client_socket.send_all("150 Here comes the directory listing.\r\n")
                send_list_data(place, self.data_client, command == "LIST" or payload == "-l")
                client_socket.send_all("226 Listed.\r\n")
            except:
                client_socket.send_all(FAIL_550_MESSAGE)
            finally:
                self.close_data_client()
        elif command == "RETR":
            try:
                self.wait_data_client()
                client_socket.send_all("150 Opened data connection.\r\n")
                with open(path, "rb") as file:
                    send_file_data(file, self.data_client)
                client_socket.send_all("226 Done.\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
            finally:
                self.close_data_client()
        elif command == "STOR":
            try:
                self.wait_data_client()
                client_socket.send_all("150 Opened data connection.\r\n")
                with open(path, "wb") as file:
                    save_file_data(file, self.data_client)
                client_socket.send_all("226 Done.\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
            finally:
                self.close_data_client()
        # todo 整理ftp命令
        elif command == "SIZE":
            try:
                client_socket.send_all("213 {}\r\n".format(uos.stat(path)[6]))
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "MDTM":
            try:
                tm=utime.localtime(uos.stat(path)[8])
                client_socket.send_all("213 {:04d}{:02d}{:02d}{:02d}{:02d}{:02d}\r\n".format(*tm[0:6]))
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "DELE":
            try:
                uos.remove(path)
                client_socket.send_all("250 OK\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "RNFR":
            try:
                # just test if the name exists, exception if not
                uos.stat(path)
                self.fromname = path
                client_socket.send_all("350 Rename from\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "RNTO":
                try:
                    uos.rename(self.fromname, path)
                    client_socket.send_all("250 OK\r\n")
                except:
                    client_socket.send_all("550 Fail\r\n")
                self.fromname = None
        elif command == "RMD" or command == "XRMD":
            try:
                uos.rmdir(path)
                client_socket.send_all("250 OK\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "MKD" or command == "XMKD":
            try:
                uos.mkdir(path)
                client_socket.send_all("250 OK\r\n")
            except:
                client_socket.send_all("550 Fail\r\n")
        elif command == "SITE":
            # site command
            client_socket.send_all("502 Unsupported command.\r\n")
        else:
            client_socket.send_all("502 Unsupported command.\r\n")
        if DEBUG:
            print("========")