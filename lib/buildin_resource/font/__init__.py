__font_8 = None
__font_16 = None

def get_font_8px():
    global __font_8
    if __font_8 == None:
        from graphic import ubmfont
        from buildin_resource.font.pix8x8 import data, width_data
        from buildin_resource import BytesStream
        f = BytesStream(data)
        __font_8 = ubmfont.FontDrawUnicode(f, width_data)
    return __font_8

def get_font_16px():
    global __font_16
    if __font_16 == None:
        from graphic import ubmfont
        from buildin_resource.font.pix16x16 import data, width_data
        from buildin_resource import BytesStream
        f = BytesStream(data)
        __font_16 = ubmfont.FontDrawUnicode(f, width_data)
    return __font_16
