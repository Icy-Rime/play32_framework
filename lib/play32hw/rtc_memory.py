import machine
import ujson as json

# ADDRESS_RTC_SLOW_MEMORY_START = 0x5000_0000
ADDRESS_RTC_SLOW_MEMORY_START = 0x5000_1000
ADDRESS_RTC_SLOW_MEMORY_END = 0x5000_2000
# ADDRESS_RTC_SLOW_MEMORY_SIZE = 0x0000_2000
ADDRESS_RTC_SLOW_MEMORY_SIZE = 0x0000_1000

class RTCMemory():
    def __len__(self):
        return ADDRESS_RTC_SLOW_MEMORY_SIZE

    def __getitem__(self, key):
        if isinstance(key, int):
            return machine.mem8[ADDRESS_RTC_SLOW_MEMORY_START + key]
        elif isinstance(key, slice):
            d = bytearray()
            for i in range(*key.indices(ADDRESS_RTC_SLOW_MEMORY_SIZE)):
                d.append(machine.mem8[ADDRESS_RTC_SLOW_MEMORY_START + i])
            return d
        return None
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            machine.mem8[ADDRESS_RTC_SLOW_MEMORY_START + key] = value
        elif isinstance(key, slice):
            count = 0
            for i in range(*key.indices(ADDRESS_RTC_SLOW_MEMORY_SIZE)):
                machine.mem8[ADDRESS_RTC_SLOW_MEMORY_START + i] = value[count]
                count += 1

__rtcm = RTCMemory()

class RTCDict(dict):
    def __init__(self):
        super().__init__()
        global __rtcm
        try:
            size = int.from_bytes(__rtcm[0:2], 'big')
            # data must start with b'{'[0]
            if __rtcm[2] != 123 or size > ADDRESS_RTC_SLOW_MEMORY_SIZE:
                raise Exception()
            data_str = __rtcm[2:size+2].decode('utf-8')
            obj = json.loads(data_str)
            for k in obj:
                self[k] = obj[k]
            del data_str, obj
        except:
            pass

    def commit_change(self):
        data = json.dumps(self).encode('utf-8')
        if len(data) + 2 > ADDRESS_RTC_SLOW_MEMORY_SIZE:
            raise Exception('RTC dict data too large!')
        size = len(data)
        __rtcm[0:2] = int.to_bytes(size, 2, 'big')
        __rtcm[2:size+2] = data
        del data

rtc_dict = RTCDict()