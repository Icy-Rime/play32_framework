class WordDictBlock():
    '''字典块对象，可用于读取候选词，获取下一块等操作'''
    def __init__(self):
        '''创建字典块对象'''
        self.block_size = 0 # 当前块的大小，包含结尾连续两个0x00的大小
        self.block_offset = 0 # 当前块在字典中的偏移
        self.words_offset = 0 # 候选词列表的偏移
        self.next_block_offset = {} # 下一个输入块地址列表,byte->int
        self.__current_word = 0 # 当前候选词的偏移，用于读取字符，单向移动或reset
    def reset_word(self):
        '''重置词汇指针，next_word将返回第一个候选词汇'''
        self.__current_word = self.words_offset
    def next_word(self,dict_fp):
        '''读取下一个候选词汇，以字节串的形式返回，不关心编码。读取到末尾时返回None'''
        if self.__current_word == 0:
            self.__current_word = self.words_offset
        if self.__current_word >= self.block_offset + self.block_size -1:
            return None
        dict_fp.seek(self.__current_word)
        buffer = dict_fp.read(1)
        chars = bytearray()
        while buffer[0] != 0x00:
            chars.extend(buffer)
            buffer = dict_fp.read(1)
        self.__current_word = dict_fp.tell()
        return chars
    def next_block(self,dict_fp,next_char_byte):
        '''返回下一个字典块，根据输入字符byte确定，如果输入字符没有对应的字典块，返回None'''
        key = next_char_byte
        if key in self.next_block_offset:
            return WordDictBlock.read_block(dict_fp,self.next_block_offset[key])
        return None
    def avaliable_input(self):
        '''获取下一有效的输入字符，字节形式byte没有s'''
        return list(self.next_block_offset.keys())
    def __repr__(self):
        return '''<WordDictBlock bs={} boff={} woff={} nextc={}/>'''.format(
            self.block_size,
            self.block_offset,
            self.words_offset,
            str(self.next_block_offset)
        )
    @staticmethod
    def read_block(fp,offset):
        '''从文件中offset处读取一个字典块对象'''
        fp.seek(offset) # 跳转到块开头
        blk = WordDictBlock() # 块对象
        blk.block_offset = offset
        buffer = fp.read(1) # 读取下一索引的数量
        for i in range(buffer[0]):
            buffer = fp.read(5) # 读取下一输入列表和偏移量
            blk.next_block_offset[buffer[0]] = int.from_bytes(buffer[1:5],"big")
        # 此时偏移量 = 列表数量x5 + offset + 1
        blk.words_offset = offset + len(blk.next_block_offset)*5 + 1
        # fp.seek(blk.words_offset)
        buffer = fp.read(1)
        while buffer[0] != 0x00:
            buffer2 = fp.read(1)
            while buffer2[0] != 0x00:
                buffer2 = fp.read(1)
            buffer = fp.read(1)
        # 此时根据偏移量可算出块大小
        blk.block_size = fp.tell() - offset
        return blk
class InputMethod():
    def __init__(self, dict_stream):
        self.__dict_fp = dict_stream
        self.__offset_list = [] # 历史有效输入的偏移量
        self.__input = bytearray() # 历史输入，但是有效的输入长度要看offset_list
        self.__current_block = WordDictBlock.read_block(self.__dict_fp,0) # 当前状态所处的字典块
    def clear(self):
        '''清空当前输入'''
        self.__offset_list.clear()
        self.__input = bytearray()
        self.__current_block = WordDictBlock.read_block(self.__dict_fp,0)
    def input_byte(self,byt):
        '''输入一个字符的ascii数值，只接受小写字母和退格键0x08，返回是否需要更新候选词'''
        if byt == 0x08 or byt == 0x7F:
            # backspace
            if len(self.__input) == 0:
                return
            # self.__input.pop()
            self.__input[-1:] = b""
            if len(self.__offset_list) > len(self.__input):
                offset = self.__offset_list.pop()
                self.__current_block = WordDictBlock.read_block(self.__dict_fp,offset)
                return True
        elif byt >= b"a"[0] and byt <= b"z"[0]:
            self.__input.append(byt)
            # 如果已经处于无效输入状态了，就不需要查找下一块了
            if len(self.__offset_list)+1 < len(self.__input):
                return False
            # 正常输入
            blk = self.__current_block.next_block(self.__dict_fp,byt)
            if blk != None:
                # 属于有效输入
                self.__offset_list.append(self.__current_block.block_offset)
                self.__current_block = blk
                return True
        return False
    def reset_word(self):
        '''重置候选词'''
        self.__current_block.reset_word()
    def next_word(self):
        '''下一个候选词，没有了返回None'''
        word = self.__current_block.next_word(self.__dict_fp).decode("utf8")
        return word.decode("utf8") if word != None else None
    def some_word(self,limit):
        '''批量读取候选词，没有了返回空列表'''
        words = []
        while len(words) < limit:
            word = self.__current_block.next_word(self.__dict_fp)
            if word == None:
                break
            words.append(word.decode("utf8"))
        return words
    def all_words(self):
        '''读取全部候选词'''
        self.__current_block.reset_word()
        return self.some_word(0xFFFF)
    def avaliable_input(self):
        '''获取可用于下一次输入的有效字符，返回ascii数值的列表'''
        return self.__current_block.avaliable_input()
    def get_input_code(self):
        '''获取当前输入的ascii字符序列'''
        return self.__input.decode("ascii")
