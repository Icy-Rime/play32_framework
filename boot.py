# This file is executed on every boot (including wake-boot from deepsleep)
import usys, machine, micropython
usys.path[:] = ['lib', '', '/lib', '/', '.frozen']
micropython.alloc_emergency_exception_buf(100)
del machine, micropython
#import webrepl
#webrepl.start()
