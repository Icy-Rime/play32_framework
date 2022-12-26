''' 生成自定义格式的unicode点阵字体
FILE:
[font_width: 1B][font_height: 1B]
[area_index: 256 * [block_offset: 2B][block_size: 1B]] # area_index[0] is 'number of block', because 0x00 always start at offset 0
[[pos_index: 1B]*'number of block'... [font_data: font_data_size]*'number of block'...]... # (font_data_size + 1) * 'number of block'
unicode序号大端编码，得到两byte，第一byte为pos_index，第二byte为area_index
'''
import sys, os
from typing import List, Tuple

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_path)

from PIL import Image, ImageFont, ImageDraw
import math
import coding, framebuf

def _get_char_data(char_str, block_w, block_h, fnt, position_offset=(0, 0), invert=False):
    block_size = math.ceil(block_w / 8) * block_h
    char_left, char_top, char_right, char_bottom = fnt.getbbox(char_str)
    char_width = char_right - char_left
    char_height = char_bottom - char_top
    char_x_offset = (block_w - char_width) // 2
    char_y_offset = char_top
    char_offset = (position_offset[0] + char_x_offset, position_offset[1] + char_y_offset)
    # draw char
    fnt_img = Image.new("1", (block_w, block_h), color=255)
    fnt_draw = ImageDraw.Draw(fnt_img)
    try:
        fnt_draw.text(char_offset, char_str, fill=0, font=fnt, anchor="lt", spacing=0)
    except: pass
    # draw framebuffer
    buffer = bytearray(block_size)
    frame = framebuf.FrameBuffer(buffer, block_w, block_h, framebuf.MONO_HLSB)
    for y in range(block_h):
        for x in range(block_w):
            pixel = fnt_img.getpixel((x, y))
            pixel = 1 if ((pixel == 0) ^ invert) else 0
            frame.pixel(x, y, pixel)
    # print(frame)
    # fnt_img.save('l.png')
    return buffer, fnt_img



def make_unicode_font(block_w, block_h, font_file, font_size, unicodes=list(c for c in range(32, 127)), position_offset=(0, 0), invert=False, ignore_bytes=[], output_path=None, preview_path=None, get_char_data=None):
    '''生成unicode点阵字体文件，自定义格式'''
    fnt = ImageFont.truetype(font_file, size=font_size)
    if get_char_data == None:
        get_char_data = _get_char_data
    unicodes.sort()
    # preview img
    preview = Image.new("1", (block_w*16, block_h*math.ceil(len(unicodes)/16)), color=255)
    preview_x_count = 0
    preview_y_count = 0
    used_unicode = []
    # make char data
    char_area = list() # type: List[List[Tuple[int, bytearray]]]
    for _ in range(256):
        char_area.append(list())
    count = 0
    for unic in unicodes:
        try:
            char = coding.UTF8.to_bytes(unic).decode("utf8")
        except:
            # print('error unic:', unic)
            continue
        buffer, fnt_img = get_char_data(char, block_w, block_h, fnt, position_offset, invert)
        count += 1
        print("{}/{}".format(count, len(unicodes)), end="\r")
        # filter
        # print(buffer)
        continue_flag = False
        for ignore_b in ignore_bytes:
            if callable(ignore_b):
                if ignore_b(char, buffer):
                    continue_flag = True
            else:
                if buffer == ignore_b:
                    continue_flag = True
        if int.bit_length(unic) > 16: # must small than 2 byte
            continue_flag = True
        if continue_flag:
            continue
        # add char data
        unic_bytes = int.to_bytes(unic, 2, 'big')
        pos_index = unic_bytes[0]
        area_index = unic_bytes[1]
        char_area[area_index].append((pos_index, buffer))
        # preview
        preview_pos = preview_x_count*block_w, preview_y_count*block_h
        preview.paste(fnt_img, preview_pos)
        preview_x_count += 1
        if preview_x_count >= 16:
            preview_x_count = 0
            preview_y_count += 1
        used_unicode.append(unic)
    # make font
    head = bytearray()
    head.extend(block_w.to_bytes(1, 'big'))
    head.extend(block_h.to_bytes(1, 'big'))
    body = bytearray()
    number_of_block = int.to_bytes(len(used_unicode), 2, 'big')
    count = 0
    for i in range(256):
        chars_in_area = char_area[i]
        chars_in_area.sort(key=lambda v: v[0])
        # update area index
        offset = int.to_bytes(count, 2, 'big')
        block_size = int.to_bytes(len(chars_in_area), 1, 'big')
        if i == 0:
            head.extend(number_of_block)
        else:
            head.extend(offset)
        head.extend(block_size)
        # update area_data
        pos_index = bytearray()
        pos_data = bytearray()
        for info in chars_in_area:
            pos_index.append(info[0])
            pos_data.extend(info[1])
        body.extend(pos_index)
        body.extend(pos_data)
        #
        count += len(chars_in_area)

    data = bytearray()
    data.extend(head)
    data.extend(body)
    if preview_path != None:
        preview.save(preview_path)
    if output_path != None:
        with open(output_path, "wb") as f:
            f.write(data)
    return data, preview, used_unicode
