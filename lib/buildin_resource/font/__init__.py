__font_8 = None
__font_16 = None

def get_font_8px():
    global __font_8
    if __font_8 == None:
        try:
            from graphic import ubmfont
            f = open('/resource/font/pix8x8.ufnt', "rb")
            __font_8 = ubmfont.FontDrawUnicode(f)
        except:
            from graphic import bmfont
            __font_8 = bmfont.FontDrawAscii()
    return __font_8

def get_font_16px():
    global __font_16
    if __font_16 == None:
        from graphic import ubmfont
        try:
            f = open('/resource/font/pix16x16.ufnt', "rb")
        except:
            from buildin_resource.font.fallback16x16 import data
            from buildin_resource import BytesStream
            f = BytesStream(data)
        __font_16 = ubmfont.FontDrawUnicode(f)

    return __font_16
