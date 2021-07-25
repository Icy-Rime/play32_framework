''' Example:
    from play32sys import network_helper, network_file_system
    wlan = network_helper.connect(True)
    network_helper.sync_time()
    network_file_system.mount(b"12345678", b"12345678", "192.168.31.37")
    #                         ^access_id^  ^access_key^ ^host^
    # access_id must be 8 bytes, access_key can be any length. default pote is 12588
    # f = open("/mnt/README.md", "a")
    f = open("/mnt/README.md", "r")
    for l in f:
        print(l, end='')
    f.close()
'''
from play32sys.network_block_device import NetworkBlockDevice, ProtocolUDP, ProtocolCache
from uhashlib import sha256
from ucryptolib import aes
from utils.hmac import HMAC
from utils.time_helper import EPOCH_TIME_DIFFER
import uos, utime, gc

PREFIX_NFS = b"nfs_"

def generate_aes_key_and_iv(access_key):
    sha = HMAC(access_key, access_key, sha256).digest()
    return sha[:16], sha[16:]

def generate_request_sign(access_id, access_key, m_param, data):
    # generate 48byte sign
    # access_id:8, timestamp:8, sign:32
    timestamp = utime.time() + EPOCH_TIME_DIFFER
    timestamp = int.to_bytes(timestamp, 8, 'big')
    sign = HMAC(access_key, access_id+timestamp+m_param+data, sha256).digest()
    return access_id+timestamp+sign

def encode_data(aes_key, iv, data):
    # mode Cipher Block Chaining (CBC)
    data = bytearray(data)
    encoded_len = 0
    enc = aes(aes_key, 2, iv)
    for i in range(len(data) // 16):
        data[i*16:i*16+16] = enc.encrypt(data[i*16:i*16+16])
        encoded_len += 16
    return data

def mount(access_id, access_key, host, port=12588, mount_path="/mnt"):
    assert len(access_id) == 8
    aes_key, aes_iv = generate_aes_key_and_iv(access_key)
    def inject_custom_param(data, mp_size, cp_size, bd_size):
        if len(data) < mp_size+cp_size or cp_size < 48:
            return PREFIX_NFS + data
        m_param = data[0:mp_size]
        c_param = data[mp_size:mp_size+cp_size]
        block_data = data[mp_size+cp_size:mp_size+cp_size+bd_size]
        # encode data
        m_param = encode_data(aes_key, aes_iv, m_param)
        block_data = encode_data(aes_key, aes_iv, block_data)
        # generate sign
        c_param[:48] = generate_request_sign(access_id, access_key, m_param, block_data)
        gc.collect()
        return PREFIX_NFS + m_param + c_param + block_data
    protocol_udp = ProtocolUDP(host, port, inject_custom_param)
    protocol = ProtocolCache(protocol_udp)
    block = NetworkBlockDevice(protocol)
    try:
        fs = uos.VfsLfs2(block)
    except:
        uos.VfsLfs2.mkfs(block)
        fs = uos.VfsLfs2(block)
    uos.mount(fs, mount_path)