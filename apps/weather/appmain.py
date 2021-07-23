import hal_keypad, ntptime
from play32sys import app, network_helper
from hashlib import sha1
from utils.hmac import HMAC
from binascii import b2a_base64
from uhttp import urequests
from uhttp.url import url_encode, encode_url_params
from utils.time_helper import EPOCH_TIME_DIFFER
from config import PUBLIC_KEY, PRIVATE_KEY
# config.py:
# PUBLIC_KEY = ""
# PRIVATE_KEY = ""
# 

def encode_xin_zhi_weather_url_v4(public_key, private_key, pdict, ttl=300):
    pdict["public_key"] = public_key
    pdict["ts"] = str(EPOCH_TIME_DIFFER + int(ntptime.time()))
    pdict["ttl"] = str(ttl)
    private_key = private_key.encode("ascii")
    params = ''
    keys = list(pdict.keys())
    keys.sort()
    for k in keys:
        params += k
        params += "="
        params += pdict[k]
        params += "&"
    if len(keys) > 0:
        params = params[:-1]
    sig = HMAC(private_key, params, sha1).digest()
    params += "&sig="
    params += url_encode(b2a_base64(sig).decode("ascii").strip())
    return "https://api.seniverse.com/v4?" + params

def encode_xin_zhi_weather_url_v3(public_key, private_key, api_path, pdict, ttl=300):
    sign_dict = {
        "uid": public_key,
        "ts": str(EPOCH_TIME_DIFFER + int(ntptime.time())),
        "ttl": str(ttl),
    }
    private_key = private_key.encode("ascii")
    params = ''
    keys = list(sign_dict.keys())
    keys.sort()
    for k in keys:
        params += k
        params += "="
        params += sign_dict[k]
        params += "&"
    if len(keys) > 0:
        params = params[:-1]
    print(params)
    sig = HMAC(private_key, params, sha1).digest()
    params += "&sig="
    params += url_encode(b2a_base64(sig).decode("ascii").strip())
    params = encode_url_params(pdict) + "&" + params
    print(params)
    return "https://api.seniverse.com/v3/" + api_path + "?" + params

def main(app_name, *args, **kws):
    hal_keypad.init()
    print("================")
    print('you are running {:}'.format(app_name))
    print(args)
    # console.log(args)
    print(kws)
    # console.log(kws)
    network_helper.connect(True)
    network_helper.sync_time()
    params = {
        "location": "ip",
        "language": "zh-Hans",
        "unit": "c",
    }
    url = encode_xin_zhi_weather_url_v3(PUBLIC_KEY, PRIVATE_KEY, "weather/daily.json", params)
    print(url)
    resp = urequests.get(url)
    print(resp.json())
    print('{:} end'.format(app_name))
    print("================")
    main_loop()

def main_loop():
    while True:
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                print("Reboot..")
                app.reset_and_run_app("") # press any key to reset