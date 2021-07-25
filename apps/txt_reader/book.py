# bookmark tools
# file format:
# [current_page_number:4][reserved:4]
# [page_size_at_index:2]... * pages
import ustruct

def get_text_utf8_length(text):
    return len(text.encode('utf8'))

class Bookmark():
    def __init__(self, file_path):
        try:
            self.__file = open(file_path, 'rb+')
            tmp = self.__file.read(4)
            self.__page = int.from_bytes(tmp, 'big')
        except:
            self.__file = open(file_path, 'wb+')
            self.__file.write(b'\0\0\0\0\0\0\0\0')
            self.__page = 0
        f = self.__file
        f.flush()
        f.seek(0, 2)
        fs = f.tell()
        self.__count = (fs - 8) // 2

    @property
    def marked_page(self):
        return self.__page
    
    def __len__(self):
        return self.__count

    def __contains__(self, key):
        if isinstance(key, int):
            return key >= 0 and key < self.__count
        return False

    def __getitem__(self, key):
        if isinstance(key, int):
            assert key >= 0 and key < self.__count
            f = self.__file
            f.flush()
            file_offset = 8 + 2 * key
            f.seek(file_offset, 0)
            return int.from_bytes(f.read(2), 'big')
        elif isinstance(key, slice):
            lst = []
            f = self.__file
            f.flush()
            st, ed, stp = key.indices(self.__count)
            if stp == 1:
                file_offset = 8 + 2 * st
                f.seek(file_offset, 0)
                for i in range(st, ed, stp):
                    lst.append(int.from_bytes(f.read(2), 'big'))
            else:
                for i in range(st, ed, stp):
                    file_offset = 8 + 2 * i
                    f.seek(file_offset, 0)
                    lst.append(int.from_bytes(f.read(2), 'big'))
            return lst
        raise ValueError(type(key))
    
    def get_page_offset_fast(self, start_page=0, end_page=None, buffer_count=512):
        if end_page == None:
            end_page = self.__count
        start_page = 0 if start_page < 0 else start_page
        end_page = self.__count if end_page > self.__count else end_page
        assert end_page >= start_page
        count = 0
        f = self.__file
        f.flush()
        f.seek(8 + 2 * start_page, 0) # seek to page size_record start
        for i in range(start_page, end_page, buffer_count):
            if i + buffer_count <= end_page:
                read_count = buffer_count
            else:
                read_count = end_page - i
            byts = f.read(read_count * 2)
            fmt_str = '>' + ('H' * read_count) # as big-endian unsigned short
            sizes = ustruct.unpack_from(fmt_str, byts)
            count += sum(sizes)
            del byts, fmt_str, sizes
        return count

    def update_marked_page(self, page, commit = True):
        self.__page = page
        if commit:
            f = self.__file
            f.seek(0, 0) # seek to start
            f.write(int.to_bytes(page, 4, 'big'))
            f.flush()
    
    def append_page(self, size):
        f = self.__file
        f.seek(0, 2) # seek to the end
        f.write(int.to_bytes(size, 2, 'big'))
        self.__count += 1
        f.flush()
    
    def append_pages(self, sizes):
        f = self.__file
        f.seek(0, 2) # seek to the end
        for size in sizes:
            f.write(int.to_bytes(size, 2, 'big'))
        self.__count += len(sizes)
        f.flush()

class Book():
    def __init__(self, file_path, buffer_size=1024, offset=0):
        self.__buffer_size = buffer_size
        self.__buffer = bytearray(buffer_size)
        self.__file = open(file_path, 'rb')
        self.__offset = offset
        self.__utf8end = 0
        f = self.__file
        f.flush()
        f.seek(0, 2)
        self.__length = f.tell()
        self.seek_to(offset)

    def __len__(self):
        return self.__length

    def get_buffered_string(self):
        return self.__buffer[:self.__utf8end].decode('utf8')

    def seek_by(self, offset):
        ''' offset: offset in bytes '''
        self.__offset += offset
        self.__update_buffer()
    
    def seek_to(self, offset):
        ''' offset: offset in bytes '''
        self.__offset = offset
        self.__update_buffer()
    
    def __update_buffer(self):
        self.__file.seek(self.__offset, 0)
        self.__buffer[:] = self.__file.read(self.__buffer_size)
        self.__utf8end = len(self.__buffer)
        try:
            self.get_buffered_string()
        except:
            # find last utf8 byte
            for i in range(-1, -7, -1):
                byt = self.__buffer[i]
                if ((byt >> 6) == 0b00000011) or (byt < 0b10000000): # utf8 start byte | ascii
                    self.__utf8end = len(self.__buffer) + i
                    break
            self.get_buffered_string()
