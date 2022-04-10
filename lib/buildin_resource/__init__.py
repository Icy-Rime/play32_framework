# global resource

class BytesStream:
    def __init__(self, byts):
        self.__byts = byts
        self.__fp = 0

    def read(self, size=None):
        when = self.__fp
        if size == None:
            self.__fp = len(self.__byts)
            return self.__byts[when:]
        else:
            self.__fp = min(len(self.__byts), self.__fp + size)
            return self.__byts[when: when  + size]

    def seek(self, offset, whence=0):
        if whence >= 2:
            # from tail
            self.__fp = len(self.__byts) - offset
        elif whence >= 1:
            # from current
            self.__fp += offset
        else:
            # from head
            self.__fp = offset
        self.__fp = min(self.__fp, len(self.__byts))
        self.__fp = max(self.__fp, 0)

    def tell(self):
        return self.__fp
