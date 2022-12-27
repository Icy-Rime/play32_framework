from machine import Pin, ADC

PIN_BATTERY = 36

__bat_adc = None

def init():
    global __bat_adc
    if __bat_adc != None:
        return
    __bat_adc = ADC(Pin(PIN_BATTERY), atten=ADC.ATTN_0DB)

def get_raw_battery_value():
    # return mv
    return __bat_adc.read_uv() // 1000
