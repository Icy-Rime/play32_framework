from ubinascii import hexlify
# see https://en.wikipedia.org/wiki/HMAC#Implementation
class HAMC():
    def __init__(self, key, msg=bytearray(), digestmod=None, block_size_in_bit=512):
        # type: (bytes, bytearray, any, int) -> None
        block_size = block_size_in_bit // 8
        if len(key) > block_size:
            key = digestmod(key).digest()
        if len(key) < block_size:
            key = key + (b'\0' * (block_size - len(key)))
        self.__inner_key = bytes((x ^ 0x36) for x in key)
        self.__outer_key = bytes((x ^ 0x5C) for x in key)
        self.__hasher = digestmod
        self.__msg = msg
        pass
    
    def update(self, msg):
        self.__msg += msg

    def digest(self):
        inner_message = self.__inner_key + self.__msg
        outer_message = self.__outer_key + self.__hasher(inner_message).digest()
        return self.__hasher(outer_message).digest()

    def hexdigest(self):
        return hexlify(self.digest())
