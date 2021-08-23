'''tiny async http server'''
import uos as os
import uasyncio as asyncio

# async def example_server_callback(header_map, body_reader):
#     ''' resp: (response_type,header,content)
#         -------------------------------------
#          response_type    : content
#         -------------------------------------
#          forbidden        : 403 Forbidden √ ignore header and content
#          error            : 500 Internal Server Error, content as info √ ignore header
#          text             : content as text √
#          html             : content as html √
#          json             : content as json √
#          redirect         : content as redirect location √ ignore header
#          static           : content is static file path √
#          stream           : content is stream file path √
#          raw              : raw stream file path √ ignore header
#     '''
#     # url
#     url = header_map['url']
#     # path
#     path = get_url_path(url)
#     # method
#     method = header_map['method']
#     # get body
#     body = None
#     if 'content-length' in header_map.keys():
#         clength = int(header_map['content-length'])
#         body = (await body_reader.read(clength)).decode()
#     # post data
#     form = get_url_params(body)
#     # query data
#     query = get_url_params(url)
#     # return response
#     response_type = "text"
#     header = {"Custom":"Header"}
#     content = "This is test page\n"
#     content += "method: " + method + "\n"
#     content += "  path: " + path + "\n"
#     content += " query: " + str(query) + "\n"
#     content += "  form: " + str(form) + "\n"
#     return (response_type, header, content)

def print_exception(e):
    try:
        import traceback
        traceback.print_exc()
    except:
        import sys
        sys.print_exception(e)

# ================
# http response verb
coding = 'utf8'
memi = {
'txt':'text/plain',
'html':'text/html',
'xhtml':'text/html',
'css':'text/css',
'svg':'image/svg',
'gif':'image/gif',
'png':'image/png',
'bmp':'image/bmp',
'jpg':'image/jpeg',
'jpeg':'image/jpeg',
'ico':'image/ico',
'js':'application/javascript',
'json':'application/json',
'':'application/octet-stream',
}
header_end = '\r\n'
header_200 = 'HTTP/1.0 200 OK\r\n'
header_403 = 'HTTP/1.0 403 Forbidden\r\n'
header_404 = 'HTTP/1.0 404 Not Found\r\n'
header_500 = 'HTTP/1.0 500 Internal Server Error\r\n'
header_text = 'Content-Type: text/plain; charset=%s\r\n' % (coding,)
header_html = 'Content-Type: text/html; charset=%s\r\n' % (coding,)
header_json = 'Content-Type: application/json; charset=%s\r\n' % (coding,)
def header_301(location):
    return 'HTTP/1.0 301 Moved Permanently\r\n'+'Location: '+location+'\r\n'
def header_302(location):
    return 'HTTP/1.0 302 Moved Temporarily\r\n'+'Location: '+location+'\r\n'
def header_static(path):
    ext = (path[path.rfind('.')+1:]).lower()
    if ext in memi.keys():
        ext = memi[ext]
    else :
        ext = memi['']
    return 'Content-Type: %s; charset=UTF-8\r\n' % (ext,)
def header_from_dict(header):
    if header==None or len(header)<=0:
        return ""
    head = ""
    for k in header.keys():
        head = head + k +': '+ header[k] +'\r\n'
    return head
def header_text_content_length(content):
    return 'Content-Length: %s\r\n' % (str(len(bytes(content,coding))),)
def header_stream_content_length(stream_size):
    return 'Content-Length: %s\r\n' % (str(stream_size),)
# helpful function
def url_decode(url):
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
            byts = byts + ch.encode(coding)
            pos = pos + 1
            continue
        else :
            # no ascii code
            hex = url[pos+1:pos+3]
            byts = byts + bytes([int(hex,16)])
            pos = pos + 3
            continue
    return byts.decode(coding)
def get_url_path(url):
    if not url:
        return ""
    pos = url.rfind("?")
    if pos >= 0:
        return url[:pos]
    else:
        return url
def get_url_params(url):
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

# http server
class TinyHttpServer:
    def __init__(self, host="0.0.0.0", port=80, callback=None, buffer_size=64):
        self.host = host
        self.port = port
        self.callback = callback
        self.buffer_size = buffer_size
        self.server = None
    def close(self):
        self.server.close()
    def start_server_async(self):
        asyncio.create_task(self.run_server())
    async def run_server(self):
        server = await asyncio.start_server(self.handler_request, self.host, self.port)
        self.server = server
        await asyncio.sleep(0)
        await server.wait_closed()
    async def wait_closed(self):
        while self.server == None:
            await asyncio.sleep(0)
        await self.server.wait_closed()
    async def handler_request(self, reader, writer):
        gc.collect()
        hmap = {}
        # print('<--------')
        # header
        first_line = None
        first_line = str(await reader.readline(),'utf-8')
        httph = first_line.split(' ',2)
        hmap['method'] = httph[0]
        hmap['url'] = httph[1]
        del first_line, httph
        line = None
        startpos = -1
        param = None
        value = None
        while True:
            # read header line by line
            line = await reader.readline()
            if not line or line == b'\r\n':
                break
            line = str(line, 'utf-8')
            startpos = line.find(':')
            if startpos > 0:
                param = line[0:startpos].strip().lower()
                value = line[startpos+1:].strip()
                hmap[param] = value
        del line, startpos, param, value
        gc.collect()
        # print('url: '+hmap['url'])
        # content
        # deal with request
        if self.callback != None:
            # response
            try:
                resp = await self.callback(hmap, reader)
            except Exception as e:
                resp = ("error",{},str(e))
                print_exception(e)
            gc.collect()
            # return None to stop server
            if resp == None:
                await TinyHttpServer.__response(("html",{},"<h1>Server Exit!</h1>"),writer,self.buffer_size)
                self.server.close()
            else:
                await TinyHttpServer.__response(resp,writer,self.buffer_size)
            del resp
            gc.collect()
        else:
            writer.write(bytes('HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n','utf8'))
            await writer.drain()
            writer.write(bytes('<h1>Hello World!</h1>','utf8'))
            await writer.drain()
        del hmap
        writer.close()
        await writer.wait_closed()
        gc.collect()
        # print('-------->\n')
    # response function
    @staticmethod
    async def __send(writer,text):
        writer.write(bytes(text,coding))
        await writer.drain()
    @staticmethod
    async def __send_data(writer,data):
        writer.write(data)
        await writer.drain()
    @staticmethod
    async def __send_403(writer):
        await TinyHttpServer.__send(writer,header_403)
        await TinyHttpServer.__send(writer,header_text)
        await TinyHttpServer.__send(writer,header_end)
        await TinyHttpServer.__send(writer,'403 Forbidden')
    @staticmethod
    async def __send_404(writer):
        await TinyHttpServer.__send(writer,header_404)
        await TinyHttpServer.__send(writer,header_text)
        await TinyHttpServer.__send(writer,header_end)
        await TinyHttpServer.__send(writer,'404 Not Found')
    @staticmethod
    async def __send_500(writer, info=""):
        await TinyHttpServer.__send(writer,header_500)
        await TinyHttpServer.__send(writer,header_text)
        await TinyHttpServer.__send(writer,header_end)
        await TinyHttpServer.__send(writer,'500 Server Error\r\n')
        await TinyHttpServer.__send(writer,info)
    @staticmethod
    async def __response(resp,writer,buffersize=64):
        response_type, header, content = resp
        if response_type == 'forbidden':
            await TinyHttpServer.__send_403(writer)
        if response_type == 'error':
            await TinyHttpServer.__send_500(writer,content)
        if response_type == 'text':
            await TinyHttpServer.__send(writer,header_200)
            await TinyHttpServer.__send(writer,header_text)
            await TinyHttpServer.__send(writer,header_from_dict(header))
            await TinyHttpServer.__send(writer,header_text_content_length(content))
            await TinyHttpServer.__send(writer,header_end)
            await TinyHttpServer.__send(writer,content)
        if response_type == 'html':
            await TinyHttpServer.__send(writer,header_200)
            await TinyHttpServer.__send(writer,header_html)
            await TinyHttpServer.__send(writer,header_from_dict(header))
            await TinyHttpServer.__send(writer,header_text_content_length(content))
            await TinyHttpServer.__send(writer,header_end)
            await TinyHttpServer.__send(writer,content)
        if response_type == 'json':
            await TinyHttpServer.__send(writer,header_200)
            await TinyHttpServer.__send(writer,header_json)
            await TinyHttpServer.__send(writer,header_from_dict(header))
            await TinyHttpServer.__send(writer,header_text_content_length(content))
            await TinyHttpServer.__send(writer,header_end)
            await TinyHttpServer.__send(writer,content)
        if response_type == 'redirect':
            await TinyHttpServer.__send(writer,header_302(content))
            await TinyHttpServer.__send(writer,header_stream_content_length(0))
            await TinyHttpServer.__send(writer,header_end)
        if response_type == 'static':
            # static
            try:
                file = open(content,'rb')
                s_size = os.stat(content)[6]
            except:
                await TinyHttpServer.__send_404(writer)
                return
            await TinyHttpServer.__send(writer,header_200)
            await TinyHttpServer.__send(writer,header_static(content))
            await TinyHttpServer.__send(writer,header_from_dict(header))
            await TinyHttpServer.__send(writer,header_stream_content_length(s_size))
            await TinyHttpServer.__send(writer,header_end)
            while True:
                data = file.read(buffersize)
                if not data or len(data)==0:
                    break
                await TinyHttpServer.__send_data(writer, data)
            file.close()
        if response_type == 'stream':
            # stream
            try:
                file = open(content,'rb')
                s_size = os.stat(content)[6]
            except:
                await TinyHttpServer.__send_500(writer)
                return
            await TinyHttpServer.__send(writer,header_200)
            await TinyHttpServer.__send(writer,header_from_dict(header))
            await TinyHttpServer.__send(writer,header_stream_content_length(s_size))
            await TinyHttpServer.__send(writer,header_end)
            while True:
                data = file.read(buffersize)
                if not data or len(data)==0:
                    break
                await TinyHttpServer.__send_data(writer, data)
            file.close()
        if response_type == 'raw':
            # raw
            try:
                file = open(content,'rb')
            except:
                await TinyHttpServer.__send_500(writer)
                return
            while True:
                data = file.read(buffersize)
                if not data or len(data)==0:
                    break
                await TinyHttpServer.__send_data(writer, data)
            file.close()