import os, io, zlib
from pathlib import PurePath, PurePosixPath
from hashlib import sha256

current_path = os.path.abspath(os.path.dirname(__file__))
output_path = os.path.abspath(os.path.join(current_path, "mpypack_updater", "tmp", "framework.pack"))
output_sha256_path = os.path.abspath(os.path.join(current_path, "mpypack_updater", "tmp", "framework.pack.sha256"))
dist_path = os.path.abspath(os.path.join(current_path, "..", ".build"))

'''pack format:
[2: filename_len][1: type_file_or_dict][3: filedata_len]
[file_name_utf8_str][file_data]
'''

TYPE_FILE = 0X00
TYPE_DIR = 0X01

# build data pack
dist_path_obj = PurePath(dist_path)
root_path_obj = PurePosixPath("/")
pack_stream = io.BytesIO()
def add_dir(relative_path):
    abs_path = root_path_obj.joinpath(relative_path)
    abs_path_data = str(abs_path).encode("utf8")
    pack_stream.write(int.to_bytes(len(abs_path_data), 2, 'big'))
    pack_stream.write(bytes([TYPE_DIR]))
    pack_stream.write(int.to_bytes(0, 3, 'big'))
    pack_stream.write(abs_path_data)
    # pack_stream.write(b'')
def add_file(relative_path):
    abs_path = root_path_obj.joinpath(relative_path)
    abs_path_data = str(abs_path).encode("utf8")
    with open(str(dist_path_obj.joinpath(relative_path)), "rb") as f:
        file_data = f.read()
    pack_stream.write(int.to_bytes(len(abs_path_data), 2, 'big'))
    pack_stream.write(bytes([TYPE_FILE]))
    pack_stream.write(int.to_bytes(len(file_data), 3, 'big'))
    pack_stream.write(abs_path_data)
    pack_stream.write(file_data)
for dirpath, dirnames, filenames in os.walk(dist_path, topdown=True):
    dirpath_obj = PurePath(dirpath)
    dirpath_obj = dirpath_obj.relative_to(dist_path_obj)
    for dir_name in dirnames:
        add_dir(dirpath_obj.joinpath(dir_name))
    for file_name in filenames:
        if str(dist_path_obj.joinpath(dirpath_obj, file_name)) == output_path:
            continue
        if str(dist_path_obj.joinpath(dirpath_obj, file_name)) == output_sha256_path:
            continue
        add_file(dirpath_obj.joinpath(file_name))
    # print(dirpath_obj, dirnames, filenames)

with open(output_path, "wb") as f:
    f.write(pack_stream.getvalue())
    packet_size = f.tell()

hasher = sha256()
with open(output_path, "rb") as f:
    part = f.read(4096)
    while len(part) > 0:
        hasher.update(part)
        part = f.read(4096)
hash = hasher.digest()
print("hash:", hash)
with open(output_sha256_path, "wb") as f:
    f.write(hash)

# test
def __process_next_file_entry(dio, verbose=False):
    header = dio.read(6)
    if len(header) < 6:
        return False
    file_name_length = int.from_bytes(header[:2], "big")
    file_type = header[2]
    file_content_length = int.from_bytes(header[3:6], "big")
    file_name = dio.read(file_name_length).decode("utf8")
    if file_type == TYPE_DIR:
        if verbose:
            print("DIR: {}".format(file_name))
    else:
        if verbose:
            print("FILE: {} SIZE: {}".format(file_name, file_content_length))
        dio.read(file_content_length)
    return True
def unpack_update_packet(verbose=False):
    with open(output_path, "rb") as f:
        flag = __process_next_file_entry(f, verbose)
        while flag:
            flag = __process_next_file_entry(f, verbose)
unpack_update_packet(True)

print("Packet Size:", packet_size)
