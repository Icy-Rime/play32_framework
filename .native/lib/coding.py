from io import IOBase
# 编码工具类
def url_decode(url):
    pos = 0
    byts = b''
    while pos < len(url):
        ch = url[pos]
        if ch != '%':
            # ascii code
            byts = byts+ch.encode('utf-8')
            pos = pos + 1
            continue
        else:
            # no ascii code
            hex = url[pos+1:pos+3]
            byts = byts + bytes([int(hex, 16)])
            pos = pos + 3
            continue
    return byts.decode('utf-8')


class UTF16():
    @staticmethod
    def byte_size(first_value):
        if first_value >> 10 == 0b110110: #_00
            return 4
        return 2

    @staticmethod
    def unicode_byte_size(value):
        if value >= 0xD800 and value <= 0xDFFF:
            raise Exception("utf16 can not encode this unicode")
        if value <= 0xFFFF:
            return 2
        elif value <= 0x10FFFF:
            return 4
        raise Exception("unicode too large")

    @staticmethod
    def from_bytes(u8, order='little'):
        fv = int.from_bytes(u8[:2], order)
        l = UTF16.byte_size(fv)
        if l == 2:
            return fv
        else:
            value = int.from_bytes(u8[:2], order)
            value &= 0b00000011_11111111
            value2 = int.from_bytes(u8[:2], order)
            value2 &= 0b00000011_11111111
            return ((value << 10) | value2) + 0x10000


    @staticmethod
    def to_bytes(value, order='little'):
        size = UTF16.unicode_byte_size(value)
        if size == 2:
            return int.to_bytes(value, 2, order)
        else:
            value -= 0x10000
            value1 = ((value & 0b1111111111_0000000000) >> 10) + 0xD800
            value2 = (value & 0b0000000000_1111111111) + 0xDC00
            return bytes([value1, value2])


class UTF8():
    @staticmethod
    def byte_size(first_byte):
        pat = 0x01 << 7  # 1000000
        l = 0  # length
        while first_byte & pat != 0:
            l = l + 1
            pat = pat >> 1
        if l == 0:
            l = 1  # for ascii
        return l

    @staticmethod
    def unicode_byte_size(value):
        if value <= 0x7F:
            return 1 # ascii
        elif value <= 0x7FF:
            return 2 # 110 xxxxx
        elif value <= 0xFFFF:
            return 3 # 1110 xxxx
        elif value <= 0x1FFFF:
            return 4 # 11110 xxx
        elif value <= 0x7FFFFFF:
            return 5 # 111110 xx
        elif value <= 0x80000000:
            return 6 # 1111110 x
            # all above followed by number of bytes: 10 xxxxxx
        else:
            raise Exception("unicode too large")

    @staticmethod
    def from_bytes(u8):
        l = UTF8.byte_size(u8[0])
        value = 0x00
        if l == 1:
            value = value + u8[0]
        else:
            # head
            pat = 0xFF >> (l+1)
            value = value | (u8[0] & pat)  # head byte
            for i in range(1, l):
                value = value << 6
                value = value | (u8[i] & 0x3F)  # following byte
        return value

    @staticmethod
    def to_bytes(value):
        size = UTF8.unicode_byte_size(value)
        u8 = bytearray(size)
        for i in range(size-1, 0, -1):
            # last 6 bit
            u8[i] = 0x80 | (value & 0x3F)
            value = value >> 6
            pass
        if size == 1:
            u8[0] = value
            return u8 # ascii
        lead_bits = (0xFE << (7 - size)) & 0xFF # 0b11111110 << size
        u8[0] = lead_bits | value
        return u8

class GB2312():
    @staticmethod
    def is_unavailable_pos(pos):
        '''GB2312中，不可用区域'''
        area, posi = pos
        # 01-09区收录除汉字外的682(846)个字符。
        # 10-15区为空白区，没有使用。
        # 16-55区收录3755(3760)个一级汉字，按拼音排序。
        # 56-87区收录3008个二级汉字，按部首/笔画排序。
        # 88-94区为空白区，没有使用。
        # 其他中间空白区域
        if (area < 1) or (area > 87) or (area > 9 and area < 16):
            return True
        if area==2 and ((posi>=1 and posi<=16) or (posi>=67 and posi<=68) or (posi>=79 and posi<=80) or (posi>=93 and posi<=94)):
            return True
        if area==4 and posi>=84 and posi<=94:
            return True
        if area==5 and posi>=87 and posi<=94:
            return True
        if area==6 and ((posi>=25 and posi<=32) or (posi>=57 and posi<=94)):
            return True
        if area==7 and ((posi>=34 and posi<=48) or (posi>=82 and posi<=94)):
            return True
        if area==8 and ((posi>=27 and posi<=36) or (posi>=74 and posi<=94)):
            return True
        if area==9 and ((posi>=1 and posi<=3) or (posi>=80 and posi<=94)):
            return True
        if area==55 and posi>=90 and posi<=94:
            return True
        return False

    @staticmethod
    def to_bytes(pos):
        area, posi = pos
        if area == 0:
            return bytes([posi])
        return bytes([area+0xA0, posi+0xA0])

    @staticmethod
    def from_bytes(byts):
        if byts[0] <= 0xA0:
            return (0, byts[0])
        return (byts[0]-0xA0, byts[1]-0xA0)

    @staticmethod
    def from_ascii(ascii_value):
        if ascii_value < b"!"[0] or ascii_value > b"~"[0]:
            # 非字母符号，使用空白
            area = 1
            pos = 1
        elif ascii_value == b"~"[0]:
            area = 1
            pos = 11
        else:
            area = 3
            pos = ascii_value - b"!"[0] + 1
        return (area, pos)

    @staticmethod
    def to_ascii(pos):
        area, posi = pos
        if area == 0:
            return posi
        if area == 1 and posi == 11:
            return b"~"[0]
        if area == 3 and posi >= 1 and posi <= 93:
            return posi + b"!"[0] - 1
        return b" "[0]

    @staticmethod
    def all_available_pos():
        poses = []
        for area in range(1, 94+1):
            for posi in range(1, 94+1):
                if GB2312.is_unavailable_pos((area, posi)):
                    continue
                poses.append((area, posi))
        return poses

    @staticmethod
    def is_available_pos(pos):
        if GB2312.is_unavailable_pos(pos):
            return False
        return True

    @staticmethod
    def to_dict_index(pos):
        '''快速将区位码转换成绝对位置，生成字库用'''
        area, posi = pos
        if area <= 0:
            return GB2312.to_dict_index(GB2312.from_ascii(posi))
        return 94 * (area - 1) + posi - 1

    @staticmethod
    def from_dict_index(a_pos):
        '''快速将绝对位置转换成区位码，生成字库用'''
        area = a_pos // 94 + 1
        posi = a_pos % 94 + 1
        return (area, posi)

class CodeReader(IOBase):
    def __init__(self, stream, init_last_char=-1):
        self._stream = stream
        self._last_char = init_last_char
        pass

    def readable(self):
        return True
    
    def chars(self):
        raise NotImplementedError()

    def is_newline(self, char):
        raise NotImplementedError()

    def read(self, limit=-1):
        buffer = []
        if limit == 0:
            return buffer
        size = 0
        for u in self.chars():
            buffer.append(u)
            size += 1
            if limit > 0 and size >= limit:
                return buffer
        return buffer

    def readline(self, limit=-1):
        buffer = []
        if limit == 0:
            return buffer
        size = 0
        should_stop = False
        for u in self.chars():
            if should_stop:
                if not self.is_newline(u):
                    self._last_char = u
                return buffer
            if self.is_newline(u): # \r \n
                should_stop = True # read one more, for \r\n
            else:
                buffer.append(u)
            size += 1
            if limit > 0 and size >= limit:
                return buffer
        return buffer

class UTF16Reader(CodeReader):
    def __init__(self, byte_stream):
        self.__order = 'little'
        super().__init__(byte_stream)

    def is_newline(self, char):
        return char == 10 or char == 13

    def chars(self):
        # readline read one more last time
        if self._last_char >= 0:
            yield self._last_char
            self._last_char = -1
        byte = self._stream.read(2)
        while byte != b'':
            if byte == b'\xff\xfe':
                self.__order = 'little'
                byte = self._stream.read(2)
                continue
            elif byte == b'\xfe\xff':
                self.__order = 'big'
                byte = self._stream.read(2)
                continue
            size = UTF16.byte_size(int.from_bytes(byte, self.__order))
            if size > 2:
                remain = self._stream.read(size-2)
                byte = byte + remain
            yield UTF16.from_bytes(byte, self.__order)
            byte = self._stream.read(2)

class UTF8Reader(CodeReader):
    def __init__(self, byte_stream):
        super().__init__(byte_stream)

    def is_newline(self, char):
        return char == 10 or char == 13

    def chars(self):
        # readline read one more last time
        if self._last_char >= 0:
            yield self._last_char
            self._last_char = -1
        byte = self._stream.read(1)
        while byte != b'':
            size = UTF8.byte_size(byte[0])
            if size > 1:
                remain = self._stream.read(size-1)
                byte = byte + remain
            yield UTF8.from_bytes(byte)
            byte = self._stream.read(1)

class GB2312Reader(CodeReader):
    def __init__(self, byte_stream):
        super().__init__(byte_stream, None)

    def is_newline(self, char):
        return char[0] == 0 and (char[1] == 10 or char[1] == 13)

    def chars(self):
        # readline read one more last time
        if self._last_char:
            yield self._last_char
            self._last_char = None
        byte = self._stream.read(1)
        while byte != b'':
            if byte[0] > 0xA0:
                remain = self._stream.read(1)
                byte = byte + remain
            yield GB2312.from_bytes(byte)
            byte = self._stream.read(1)
