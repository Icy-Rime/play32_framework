'''Read and write PBM format image file
PBM format: http://netpbm.sourceforge.net/doc/pbm.html
Only support single image in a file
'''

def _is_space(char):
    r'''C isspace function'''
    return char in [0x20, 0x09 ,0x0a ,0x0b, 0x0c, 0x0d] #[ \t\n\v\f\r]

def _is_new_line(char):
    r''' char is \r or \n'''
    return char in [0x0a ,0x0d] #[\n\r]
def _is_comment_start(char):
    ''' char is #'''
    return char == 0x23 #[#]

def _read_header(instream):
    r'''Read file header, get basic information
    :param: instream: stream that support seek, tell, read
    :returns: (
        width,
        hetght,
        raster_data_format_P1_or_P4_or_UNKNOWN,
        raster_start_position,
        comment
    )
    '''
    # magic number
    instream.seek(0)
    mg = instream.read(2)
    if mg != b"P1" and mg != b"P4":
        return (-1, -1, b"UNKNOWN", -1)
    # state machine
    comment = bytearray()
    buffer = bytearray() # list to store bytes
    is_reading_info = False
    is_reading_comment = False
    width = -1
    height = -1
    byts = instream.read(1)
    while len(byts) == 1:
        char = byts[0]
        # reading comment state
        if is_reading_comment:
            comment.append(char)
            if _is_new_line(char):
                is_reading_comment = False
        # reading info state
        elif is_reading_info:
            if _is_comment_start(char):
                is_reading_comment = True
            elif _is_space(char):
                if width < 0:
                    width = int(buffer.decode(),10)
                elif height < 0:
                    height = int(buffer.decode(),10)
                buffer = bytearray()
                is_reading_info = False
                if width >= 0 and height >= 0:
                    # read header finished
                    break
            else:
                buffer.append(char)
        # normal state
        elif not is_reading_info and not is_reading_comment:
            if _is_space(char):
                pass
            elif _is_comment_start(char):
                is_reading_comment = True
            else:
                buffer.append(char)
                is_reading_info = True
        byts = instream.read(1)
    pos = instream.tell()
    return (width, height, mg, pos, comment)

def _read_data(instream, width, height, format, offset=-1):
    r'''Read image data
    :param: instream: stream that support seek, tell, read
            width: image width
            height: image height
            format: b'P1' or b'P4'
    :return: data in MONO_HLSB(only on micropython, MSB on other platform) format bytes
    '''
    if format != b"P1" and format != b"P4":
        return bytearray(0)
    if offset >= 0:
        instream.seek(offset)
    width_count = width // 8
    width_count += 0 if width % 8 == 0 else 1
    size = width_count * height
    # bytecode format
    if format == b"P4":
        return bytearray(instream.read(size))
    # text format
    data = bytearray(size)
    byte_data = 0
    bitp = 0
    width_p = 0
    index = 0
    byts = instream.read(1)
    while index < size and len(byts) == 1:
        char = byts[0]
        if _is_space(char):
            pass
        else:
            byte_data = (byte_data << 1) | ((char-0x30) & 0x01)
            bitp += 1
            width_p += 1
            if width_p == width:
                byte_data <<= 8 - bitp
                data[index] = byte_data
                index += 1
                byte_data = 0
                bitp = 0
                width_p = 0
            elif (bitp >= 8):
                data[index] = byte_data
                index += 1
                byte_data = 0
                bitp = 0
        byts = instream.read(1)
    return data

def read_image(instream):
    r'''Read image file, return basic information and data
    :param: instream: stream that support seek, tell, read
    :returns: (
        width,
        hetght,
        raster_data_format_P1_or_P4_or_UNKNOWN,
        image_data,
        comment,
    )
    '''
    width, height, mg, _, comment = _read_header(instream)
    data = _read_data(instream, width, height, mg)
    return (width, height, mg, data, comment)

def make_image(outstream, width, height, data, format='P4', comment="made with bpm.py"):
    r'''Write an image file
    :param: outstream: file to write
            width: image width
            height: image height
            data: image data in MONO_HLSB(only on micropython, MSB on other platform) format
            format: "P1" or "P4"
            comment: string
    :return: file size
    '''
    if isinstance(format, bytes) or isinstance(format, bytearray):
        format = format.decode("utf8")
    assert format == "P4" or format == "P1"
    if isinstance(comment, bytes) or isinstance(comment, bytearray):
        comment = comment.decode("utf8")
    outstream.write("{:s}\n#{:s}\n{:d} {:d}\n".format(format, comment, width, height).encode())
    if format == "P4":
        outstream.write(data)
    else:
        wbyte = width // 8
        wbyte += 0 if width % 8 == 0 else 1
        for y in range(height):
            for x in range(width):
                offset = (y * wbyte) + (x // 8)
                bit = (7 - (x % 8))
                value = (data[offset] >> bit) & 0x01
                if x != 0:
                    outstream.write(b' ')
                outstream.write(b'0' if value == 0 else b'1')
            outstream.write("\n".encode())
    size = outstream.tell()
    return size
