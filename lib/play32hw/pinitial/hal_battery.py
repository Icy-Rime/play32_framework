from machine import Pin, ADC

PIN_BATTERY = 36

__bat_adc = None

def init():
    global __bat_adc
    if __bat_adc != None:
        return
    __bat_adc = ADC(Pin(PIN_BATTERY))
    __bat_adc.atten(ADC.ATTN_0DB)
    __bat_adc.width(ADC.WIDTH_12BIT)

def get_raw_battery_value():
    return __bat_adc.read()
