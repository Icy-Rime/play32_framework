import machine

# ADDRESS_RTC_FAST_MEMORY_START = 0x3FF8_0000
# ADDRESS_RTC_FAST_MEMORY_END = 0x3FF8_2000
# ADDRESS_RTC_FAST_MEMORY_SIZE = 0x3FF8_2000

# upper 4k reserved by esp-idf?
ADDRESS_RTC_SLOW_MEMORY_START = 0x5000_0000
SIZE_RTC_SLOW_MEMORY = 0x0000_2000

class RTCMemory():
    def __init__(self, offset=0, size=SIZE_RTC_SLOW_MEMORY):
        self.__ofs = offset + ADDRESS_RTC_SLOW_MEMORY_START
        self.__s = size
        assert offset + size <= SIZE_RTC_SLOW_MEMORY

    def __len__(self):
        return self.__s

    def __getitem__(self, key):
        offset = self.__ofs
        if isinstance(key, int):
            assert key >= 0 and key < self.__s
            return machine.mem8[offset + key]
        elif isinstance(key, slice):
            d = bytearray()
            for i in range(*key.indices(self.__s)):
                d.append(machine.mem8[offset + i])
            return d
        raise ValueError(type(key))
    
    def __setitem__(self, key, value):
        offset = self.__ofs
        if isinstance(key, int):
            assert key >= 0 and key < self.__s
            machine.mem8[offset + key] = value
        elif isinstance(key, slice):
            count = 0
            for i in range(*key.indices(self.__s)):
                machine.mem8[offset + i] = value[count]
                count += 1
        else:
            raise ValueError(type(key))
