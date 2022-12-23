# sdcard
from machine import Pin, SDCard
import uos

PIN_SD_CS = 22
PIN_SD_SCK = 23
PIN_SD_MISO = 25
PIN_SD_MOSI = 26

class __SDCardBlockDevice():
    def __init__(self, sdcard):
        self.__sd = sdcard
        self.deinit = sdcard.deinit
        self.info = sdcard.info
        # self.ioctl = sdcard.ioctl
        self.block_count = sdcard.ioctl(4, None)
        self.block_size = sdcard.ioctl(5, None)
        self.block_size = 512 if self.block_size == None else self.block_size

    def readblocks(self, block_num, buf, offset=0):
        blsz = self.block_size
        blkn = block_num
        size = len(buf)
        sd = self.__sd
        b_data = bytearray(blsz)
        index = 0
        if (offset > 0):
            b_end = offset + size
            b_end = blsz if b_end > blsz else b_end
            h_size = b_end - offset
            sd.readblocks(blkn, b_data)
            buf[0:h_size] = b_data[offset:b_end]
            index += h_size
            blkn += 1
        while size - index >= blsz:
            sd.readblocks(blkn, b_data)
            buf[index: index+blsz] = b_data[:blsz]
            index += blsz
            blkn += 1
        if size != index:
            sd.readblocks(blkn, b_data)
            buf[index:size] = b_data[0:size - index]

    def writeblocks(self, block_num, buf, offset=0):
        blsz = self.block_size
        blkn = block_num
        size = len(buf)
        sd = self.__sd
        b_data = bytearray(blsz)
        index = 0
        if (offset > 0):
            b_end = offset + size
            b_end = blsz if b_end > blsz else b_end
            h_size = b_end - offset
            sd.readblocks(blkn, b_data)
            b_data[offset:b_end] = buf[0:h_size]
            sd.writeblocks(blkn, b_data)
            index += h_size
            blkn += 1
        while size - index >= blsz:
            b_data = buf[index: index+blsz]
            sd.writeblocks(blkn, b_data)
            index += blsz
            blkn += 1
        if size != index:
            sd.readblocks(blkn, b_data)
            b_data[0:size - index] = buf[index:size]
            sd.writeblocks(blkn, b_data)

    def ioctl(self, op, arg):
        if op == 4: # block count
            return self.block_count
        if op == 5: # block size
            return self.block_size
        if op == 6: # block erase, arg is block_num
            if self.__sd.ioctl(6, arg) != 0:
                self.writeblocks(arg, bytearray(self.block_size))
            return 0

__sdcard = None

def init():
    global __sdcard
    if __sdcard == None:
        try:
            sd = SDCard(
                slot=3,
                width=1,
                sck=Pin(PIN_SD_SCK),
                miso=Pin(PIN_SD_MISO),
                mosi=Pin(PIN_SD_MOSI),
                cs=Pin(PIN_SD_CS),
                # freq=20_000_000
            )
            __sdcard = __SDCardBlockDevice(sd)
        except: pass

def mount():
    try:
        uos.mount(__sdcard, "/sd")
        return True
    except:
        return False

def umount():
    try:
        uos.umount("/sd")
        return True
    except:
        return False

def format_fat():
    uos.VfsFat.mkfs(__sdcard)

def format_lfs2():
    uos.VfsLfs2.mkfs(__sdcard)
