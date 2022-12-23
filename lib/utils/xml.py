import micropython
from micropython import const
from ure import compile
from uio import BytesIO

# status const
STATUS_DEFAULT = const(0X00)
STATUS_TAG_START = const(0X01)
STATUS_RAW_STRING_START = const(0X02)
STATUS_TAG_IGNORE = const(0x03)
STATUS_TAG_OPENING = const(0x04)
STATUS_TAG_OPENED = const(0x05)
STATUS_TAG_PARAM = const(0x06)
STATUS_TAG_VALUE = const(0x07)
# TYPE_CONST
TYPE_TAG = const(0b00)
TYPE_STRING = const(0b0001)
TYPE_ATTRIBUTE = const(0b0010)
TYPE_VALUE = const(0b0011)
# char const
CHAR_SPACE = const(0x20)
CHAR_R = const(0x0D)
CHAR_N = const(0x0A)
CHAR_T = const(0x09)
CHAR_V = const(0x0B)
CHAR_LT = const(0x3C) # <
CHAR_GT = const(0x3E) # >
CHAR_EXCLA = const(0x21) # !
CHAR_QUEST = const(0x3F) # ?
CHAR_SLASH = const(0x2F) # /
CHAR_EQUAL = const(0x3D) # =
CHAR_QUOTE = const(0x22) # "

def xml_parse_token(read_func, buffer_size:int):
    # return [(token_type_and_depth, token_offset, token_size), ...]
    buffer_pointer:int = buffer_size
    buffer = b""
    lst = []
    offset:int = 0
    depth:int = 0
    status:int = STATUS_DEFAULT
    t_type:int = 0 # 0bxxxxxxxx_xxxx1111 type, 0b11111111_1111xxxx depth
    t_offset:int = 0
    t_size:int = 0
    while True:
        # read next char
        if buffer_pointer >= buffer_size:
            tmp_bytes = read_func(buffer_size)
            buffer_size = int(len(tmp_bytes))
            buffer_pointer = 0
            buffer = tmp_bytes
        if buffer_pointer >= buffer_size:
            return lst
        ch:int = buffer[buffer_pointer]
        buffer_pointer += 1
        offset += 1
        # process char
        if status == STATUS_DEFAULT:
            if ch == CHAR_SPACE or ch == CHAR_R or ch == CHAR_N or ch == CHAR_T or ch == CHAR_V:
                continue
            elif ch == CHAR_LT:
                status = STATUS_TAG_START
                t_offset = offset
                t_type = TYPE_TAG
            else:
                status = STATUS_RAW_STRING_START
                # t_offset = offset - 1
                t_type = TYPE_STRING
        elif status == STATUS_RAW_STRING_START:
            if ch == CHAR_LT:
                t_size = offset - t_offset - 1
                t_type = TYPE_STRING | (depth << 4)
                lst.append((t_type, t_offset, t_size))
                status = STATUS_TAG_START
                t_offset = offset
                t_type = TYPE_TAG
        elif status == STATUS_TAG_START:
            if ch == CHAR_EXCLA or ch == CHAR_QUEST:
                status = STATUS_TAG_IGNORE
            elif ch == CHAR_SLASH:
                depth -= 1
                status = STATUS_TAG_IGNORE
            else:
                status = STATUS_TAG_OPENING
        elif status == STATUS_TAG_OPENING:
            if ch == CHAR_SPACE or ch == CHAR_R or ch == CHAR_N or ch == CHAR_T or ch == CHAR_V or ch == CHAR_GT or ch == CHAR_SLASH:
                t_size = offset - t_offset - 1
                t_type = TYPE_TAG | (depth << 4)
                lst.append((t_type, t_offset, t_size))
                if ch == CHAR_GT:
                    depth += 1
                    t_offset = offset
                    status = STATUS_DEFAULT
                elif ch == CHAR_SLASH:
                    status = STATUS_TAG_IGNORE
                else:
                    t_offset = offset
                    status = STATUS_TAG_OPENED
        elif status == STATUS_TAG_OPENED:
            if ch == CHAR_SPACE or ch == CHAR_R or ch == CHAR_N or ch == CHAR_T or ch == CHAR_V or ch == CHAR_EQUAL:
                continue
            elif ch == CHAR_SLASH:
                status = STATUS_TAG_IGNORE
            elif ch == CHAR_GT:
                depth += 1
                t_offset = offset
                status = STATUS_DEFAULT
            elif ch == CHAR_QUOTE:
                t_offset = offset
                status = STATUS_TAG_VALUE
            else:
                t_offset = offset - 1
                status = STATUS_TAG_PARAM
        elif status == STATUS_TAG_PARAM:
            if ch == CHAR_EQUAL:
                t_size = offset - t_offset - 1
                t_type = TYPE_ATTRIBUTE | (depth << 4)
                lst.append((t_type, t_offset, t_size))
                status = STATUS_TAG_OPENED
        elif status == STATUS_TAG_VALUE:
            if ch == CHAR_QUOTE:
                t_size = offset - t_offset - 1
                t_type = TYPE_VALUE | (depth << 4)
                lst.append((t_type, t_offset, t_size))
                status = STATUS_TAG_OPENED
        elif status == STATUS_TAG_IGNORE:
            if ch == CHAR_GT:
                t_offset = offset
                status = STATUS_DEFAULT
        # return lst

def xml_token_get_info(token):
    typ = token[0]
    return typ & 0b1111, typ >> 4

def xml_token_get_data(seekable_stream, token, base_offset=0):
    _, offset, size = token
    seekable_stream.seek(base_offset + offset)
    return seekable_stream.read(size)

def xml_token_print(token, tid=-1, seekable_stream=None, base_offset=0):
    _, off, siz = token
    typ, dep = xml_token_get_info(token)
    if seekable_stream != None:
        data = xml_token_get_data(seekable_stream, token, base_offset)
    else:
        data = b""
    if tid >= 0:
        print("{:> 4d}:{}{}".format(tid, "  " * dep, (bin(typ), off, siz)), data)
    else:
        print("{}{}".format("  " * dep, (bin(typ), off, siz)), data)

def xml_get_children(xml_tokens = [], node_id = 0):
    lst = []
    typ, dep = xml_token_get_info(xml_tokens[node_id])
    if typ != TYPE_TAG:
        return lst
    node_id += 1
    size = len(xml_tokens)
    while node_id < size:
        token = xml_tokens[node_id]
        t_type, t_depth = xml_token_get_info(token)
        if t_type == TYPE_TAG or t_type == TYPE_STRING:
            if t_depth == dep + 1:
                lst.append(node_id)
            elif t_depth <= dep:
                break
        node_id += 1
    return lst

def xml_get_attributes(xml_tokens = [], node_id = 0):
    lst = []
    typ, _ = xml_token_get_info(xml_tokens[node_id])
    if typ != TYPE_TAG:
        return lst
    node_id += 1
    size = len(xml_tokens)
    while node_id < size:
        token = xml_tokens[node_id]
        t_type, _ = xml_token_get_info(token)
        if t_type == TYPE_ATTRIBUTE or t_type == TYPE_VALUE:
            if t_type == TYPE_ATTRIBUTE:
                lst.append(node_id)
        else:
            break
        node_id += 1
    return lst

def xml_get_attribute_value(xml_tokens = [], attribute_id = 0):
    # -2: no attribute -1: no value
    typ, _ = xml_token_get_info(xml_tokens[attribute_id])
    if typ != TYPE_ATTRIBUTE:
        return -2
    size = len(xml_tokens)
    attribute_id += 1
    if attribute_id >= size:
        return -1
    typ, _ = xml_token_get_info(xml_tokens[attribute_id])
    if typ == TYPE_VALUE:
        return attribute_id
    else:
        return -1

class XMLNode():
    def __init__(self, seekable_stream=b"", xml_tokens = [], node_id = 0, parent_node_id=-1, base_offset=0):
        self.__stm = seekable_stream
        self.__toks = xml_tokens
        self.__id = node_id
        self.__pid = parent_node_id
        self.__bof = base_offset
    
    @property
    def children(self):
        tokens = self.__toks
        sid = self.__id
        return [XMLNode(self.__stm, tokens, nid, sid, self.__bof) for nid in xml_get_children(tokens, sid)]
    
    @property
    def parent(self):
        pid = self.__pid
        if pid >= 0:
            return XMLNode(self.__stm, self.__toks, pid, self.__id, self.__bof)
        else:
            return None
    
    @property
    def attributes(self):
        dic = {}
        tokens = self.__toks
        stm = self.__stm
        bof = self.__bof
        sid = self.__id
        for aid in xml_get_attributes(tokens, sid):
            value_id = xml_get_attribute_value(tokens, aid)
            if value_id >= 0:
                value = xml_token_get_data(stm, tokens[value_id], bof)
            else:
                value = None
            dic[xml_token_get_data(stm, tokens[aid], bof)] = value
        return dic

    @property
    def value(self):
        return xml_token_get_data(self.__stm, self.__toks[self.__id], self.__bof)

    @property
    def is_string(self):
        return xml_token_get_info(self.__toks[self.__id])[0] == TYPE_STRING

    def __iterate_attributes_name(self):
        tokens = self.__toks
        stm = self.__stm
        bof = self.__bof
        sid = self.__id
        for aid in xml_get_attributes(tokens, sid):
            attr_name = xml_token_get_data(stm, tokens[aid], bof)
            yield attr_name, aid

    def __contains__(self, key):
        for attr_name, _ in self.__iterate_attributes_name():
            if key == attr_name:
                return True
        return False
    
    def __getitem__(self, key):
        tokens = self.__toks
        stm = self.__stm
        bof = self.__bof
        for attr_name, aid in self.__iterate_attributes_name():
            if key == attr_name:
                value_id = xml_get_attribute_value(tokens, aid)
                if value_id >= 0:
                    return xml_token_get_data(stm, tokens[value_id], bof)
                else:
                    return None
        raise KeyError(key)
    
    def __attribute_Iterator(self):
        for attr_name, _ in self.__iterate_attributes_name():
            yield attr_name

    def __iter__(self):
        return self.__attribute_Iterator()
    
    def iterate_attributes(self):
        tokens = self.__toks
        stm = self.__stm
        bof = self.__bof
        for attr_name, aid in self.__iterate_attributes_name():
            value_id = xml_get_attribute_value(tokens, aid)
            if value_id >= 0:
                yield attr_name, xml_token_get_data(stm, tokens[value_id], bof)
            else:
                yield attr_name, None

    def close(self):
        if self.__id <= 0:
            self.__stm.close()

# ======== Util function ========
__XML_ENTITY_REGEXP = compile("&(\w?\w?\w?\w?);")

def __xml_re_replace(mt):
    e_n = mt.group(1)
    if e_n == "lt":
        return "<"
    elif e_n == "gt":
        return ">"
    elif e_n == "amp":
        return "&"
    elif e_n == "apos":
        return "'"
    elif e_n == "quot":
        return "\""
    else:
        return mt.group(0)

def decode_xml_entity(text):
    if type(text) == bytes:
        text = text.decode("utf8")
        return __XML_ENTITY_REGEXP.sub(__xml_re_replace, text).encode("utf8")
    return __XML_ENTITY_REGEXP.sub(__xml_re_replace, text)

def load_xml_file(path, buffer_size = 1024):
    f = open(path, "rb")
    tokens = xml_parse_token(f.read, buffer_size)
    return XMLNode(f, tokens, 0)

def load_xml_stream(stm, buffer_size = 1024):
    tokens = xml_parse_token(stm.read, buffer_size)
    return XMLNode(stm, tokens, 0)

def load_xml_string(text, buffer_size = 1024):
    stm = BytesIO(text.encode("utf8"))
    tokens = xml_parse_token(stm.read, buffer_size)
    return XMLNode(stm, tokens, 0)
