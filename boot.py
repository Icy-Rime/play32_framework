# This file is executed on every boot (including wake-boot from deepsleep)
import sys, esp, machine, micropython
sys.path[:] = ['', 'lib', '/', '/lib']
esp.osdebug(None)
machine.freq(240000000)
micropython.alloc_emergency_exception_buf(100)
del sys, esp, machine, micropython
#import webrepl
#webrepl.start()
