# This file is executed on every boot (including wake-boot from deepsleep)
import usys, esp, machine, micropython
usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
esp.osdebug(None)
machine.freq(160000000)
micropython.alloc_emergency_exception_buf(100)
del esp, machine, micropython
#import webrepl
#webrepl.start()
