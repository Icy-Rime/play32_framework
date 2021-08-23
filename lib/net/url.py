from ubinascii import hexlify

_ALWAYS_SAFE_BYTES = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-'

def url_encode(text, code="utf-8"):
    data = text.encode(code)
    output = bytearray()
    for byt in data:
        if byt == 0x20: # Space
            output.append(0x2B) # '+'
        elif byt not in _ALWAYS_SAFE_BYTES:
            pass
            output.append(0x25) # '%'
            output.extend(hexlify(bytes([byt])))
        else:
            output.append(byt)
    return output.decode(code)

def url_decode(url, code="utf-8"):
    pos = 0
    byts = b''
    while pos < len(url):
        ch = url[pos]
        if ch == '+':
            byts = byts + b' '
            pos = pos + 1
            continue
        elif ch != '%':
            # ascii code
            byts = byts + ch.encode(code)
            pos = pos + 1
            continue
        else :
            # no ascii code
            hex = url[pos+1:pos+3]
            byts = byts + bytes([int(hex,16)])
            pos = pos + 3
            continue
    return byts.decode(code)

def get_url_path(url):
    if not url:
        return ""
    pos = url.rfind("?")
    if pos >= 0:
        return url[:pos]
    else:
        return url
    
def get_url_params(url):
    # type: (str) -> dict
    qdict = {}
    if not url:
        return {}
    pos = url.rfind("?")
    s_query = None
    if pos >= 0:
        s_query = url[pos+1:]
    else:
        s_query = url
    params = s_query.split('&')
    for param in params:
        pair = param.find('=')
        if pair > 0:
            name = url_decode(param[:pair])
            value = url_decode(param[pair+1:])
            qdict[name] = value
    return qdict

def encode_url_params(pdict, sort=False):
    # type: (dict, bool) -> str
    output = ''
    keys = list(pdict.keys())
    if len(keys) <= 0:
        return ''
    if sort:
        keys.sort()
    for k in keys:
        output += url_encode(k)
        output += "="
        output += url_encode(pdict[k])
        output += "&"
    return output[:-1]
