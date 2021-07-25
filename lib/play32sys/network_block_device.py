'''
dev = NetworkBlockDevice("192.168.31.31", 12588)
try:
    fs = os.VfsLfs2(dev)
except:
    fs = os.VfsLfs2.mkfs(dev)
os.mount(fs, '/mnt')
'''
from micropython import const
import usocket

class RemoteResourceError(Exception):
    pass

# UDP Protocol
CODE_SUCCESS = const(0XFF)
CMD_WRITE = const(0x00)
CMD_READ = const(0x01)
CMD_GET_INFO = const(0x02)
CMD_GET_SERVER_INFO = const(0x03)
CMD_PING = const(0xFF)
class ProtocolUDP:
    def __init__(self, host, port=12588, inject_custom_param=None, unpack_custom_response=None, retry=3, timeout_ms=500):
        self.inject_custom_param = inject_custom_param
        self.unpack_custom_response = unpack_custom_response
        udp = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        udp.settimeout(timeout_ms/1000)
        address = usocket.getaddrinfo(host, port)[0][-1]
        # get basic server info
        req = bytearray(1)
        req[0] = CMD_GET_SERVER_INFO
        if inject_custom_param != None:
            req = inject_custom_param(req, 1, 0, 0)
        udp.sendto(req, address)
        data = udp.recv(8)
        self.param_size = int.from_bytes(data[0:4], 'big')
        self.custom_param_offset = int.from_bytes(data[4:8], 'big')
        self.custom_param_size = self.param_size - self.custom_param_offset
        # now function "__inject_custom_param" is avaliable
        # get remote block device info
        req = bytearray(self.param_size)
        req[0] = CMD_GET_INFO
        req[self.custom_param_offset:self.param_size] = bytearray(self.custom_param_size)
        req = self.__inject_custom_param(req)
        udp.sendto(req, address)
        data = udp.recv(self.param_size)
        self.block_size = int.from_bytes(data[0:4], 'big')
        self.block_count = int.from_bytes(data[4:8], 'big')
        self.pid = 0 # request id
        self.udp = udp
        self.address = address
        self.retry = retry
        self.packet_size = self.param_size + self.block_size
        # packet_size = param_size + block_size
        # param_size = custom_param_offset + custom_param_size
        # custom_param_offset = minial_param_size
        # all above informations are required from server.
    
    def __inject_custom_param(self, data):
        if self.inject_custom_param != None:
            return self.inject_custom_param(data, self.custom_param_offset, self.custom_param_size, self.block_size)
        return data
    
    def __unpack_custom_response(self, data):
        if self.unpack_custom_response != None:
            return self.unpack_custom_response(data, self.custom_param_offset, self.custom_param_size, self.block_size)
        return data

    def get_info(self):
        return self.block_size, self.block_count

    def read_block(self, block_num):
        # print("read:", block_num)
        retry = self.retry
        while retry > 0:
            try:
                id = self.pid % 0xFF
                self.pid += 1
                req = bytearray(self.packet_size)
                req[0] = CMD_READ
                req[1] = id
                req[2:6] = int.to_bytes(block_num, 4, 'big')
                req = self.__inject_custom_param(req)
                self.udp.sendto(req, self.address)
                data = self.udp.recv(self.packet_size)
                data = self.__unpack_custom_response(data)
                if data[0] == CODE_SUCCESS and data[1] == id:
                    return data[self.param_size:self.packet_size]
            except: pass
            retry -= 1
        raise RemoteResourceError()
    
    def write_block(self, block_num, data):
        # print("write:", block_num)
        retry = self.retry
        while retry > 0:
            try:
                id = self.pid % 0xFF
                self.pid += 1
                req = bytearray(self.packet_size)
                req[0] = CMD_WRITE
                req[1] = id
                req[2:6] = int.to_bytes(block_num, 4, 'big')
                req[self.param_size:self.packet_size] = data[:self.block_size]
                req = self.__inject_custom_param(req)
                self.udp.sendto(req, self.address)
                data = self.udp.recv(self.packet_size)
                data = self.__unpack_custom_response(data)
                if data[0] == CODE_SUCCESS and data[1] == id:
                    return
            except: pass
            retry -= 1
        raise RemoteResourceError()


# Cache Protocol
class ProtocolCache():
    def __init__(self, protocol_obj, cache_blocks=5):
        self.__protocol = protocol_obj
        self.get_info = protocol_obj.get_info
        protocol_info = protocol_obj.get_info()
        self.block_size = protocol_info[0] # block_size
        self.block_count = protocol_info[1] # block_count
        self.__cache_list = []
        for i in range(cache_blocks):
            # [block_number, data, visited]
            self.__cache_list.append([-1, bytearray(self.block_size), 0])
            # 按照最不常用原则淘汰缓存。缓存命中时visited+=1，其余缓存不变。缓存未命中时所有visited-1。
            # visited=<0时可以替换，替换时优先替换visited最小的缓存

    def __query_cache(self, block_num):
        for cache in self.__cache_list:
            if cache[0] == block_num:
                cache[2] += 1
                return cache[1]
        # 缓存未命中
        for cache in self.__cache_list:
            cache[2] -= 1
        return None

    def __update_cache(self, block_num, data):
        target_cache = None
        # 找到最不常用的缓存
        for cache in self.__cache_list:
            if target_cache == None or cache[2] < target_cache[2]:
                target_cache = cache
            if cache[0] == block_num:
                # 缓存存在，直接更新
                cache[1][:] = data[:]
                return
        # 改写缓存
        if target_cache != None and target_cache[2] <= 0:
            target_cache[0] = block_num
            target_cache[1][:] = data[:]
            target_cache[2] = 1

    def read_block(self, block_num):
        cache = self.__query_cache(block_num)
        if cache != None:
            # print("cache hit:", block_num)
            return cache
        cache = self.__protocol.read_block(block_num)
        self.__update_cache(block_num, cache)
        # print("cache update:", block_num)
        return cache

    def write_block(self, block_num, data):
        _ = self.__query_cache(block_num)
        self.__protocol.write_block(block_num, data)
        self.__update_cache(block_num, data)
        # print("cache update:", block_num)

# Network Block Device
class NetworkBlockDevice:
    def __init__(self, protocol_obj):
        self.protocol = protocol_obj
        protocol_info = protocol_obj.get_info()
        self.block_size = protocol_info[0] # block_size
        self.block_count = protocol_info[1] # block_count
        # print("bdev:", block_size, block_count)

    def readblocks(self, block_num, buf, offset=0):
        # print(">read:",len(buf),"block:",block_num,"offset:",offset)
        blsz = self.block_size
        blkn = block_num
        size = len(buf)
        index = 0
        if (offset > 0):
            b_end = offset + size
            b_end = blsz if b_end > blsz else b_end
            h_size = b_end - offset
            b_data = self.protocol.read_block(blkn)
            buf[0:h_size] = b_data[offset:b_end]
            index += h_size
            blkn += 1
        while size - index >= blsz:
            b_data = self.protocol.read_block(blkn)
            buf[index: index+blsz] = b_data[:blsz]
            index += blsz
            blkn += 1
        if size != index:
            b_data = self.protocol.read_block(blkn)
            buf[index:size] = b_data[0:size - index]
        # print(buf[:])
        # print("========")

    def writeblocks(self, block_num, buf, offset=0):
        # print(">write:",len(buf),"block:",block_num,"offset:","None" if offset == None else offset)
        # print(buf[:])
        blsz = self.block_size
        blkn = block_num
        size = len(buf)
        index = 0
        if (offset > 0):
            b_end = offset + size
            b_end = blsz if b_end > blsz else b_end
            h_size = b_end - offset
            b_data = bytearray(self.protocol.read_block(blkn))
            b_data[offset:b_end] = buf[0:h_size]
            self.protocol.write_block(blkn, b_data)
            index += h_size
            blkn += 1
        while size - index >= blsz:
            b_data = buf[index: index+blsz]
            self.protocol.write_block(blkn, b_data)
            index += blsz
            blkn += 1
        if size != index:
            b_data = bytearray(self.protocol.read_block(blkn))
            b_data[0:size - index] = buf[index:size]
            self.protocol.write_block(blkn, b_data)
        # print("========")

    def ioctl(self, op, arg):
        if op == 4: # block count
            return self.block_count
        if op == 5: # block size
            return self.block_size
        if op == 6: # block erase, arg is block_num
            try:
                # print(">erase:",arg)
                self.protocol.write_block(arg, bytearray(self.block_size))
                # print("========")
                return 0
            except RemoteResourceError:
                return 16 # Device or resource busy
