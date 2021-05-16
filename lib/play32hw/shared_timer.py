from machine import Timer as HardwareTimer
from utime import ticks_ms, ticks_diff, ticks_add
from micropython import schedule
from usys import print_exception
ONE_SHOT = 0
PERIODIC = 1
_shared_timers = []
class SharedTimer():
    def __init__(self, id, *_args, **_kws) -> None:
        self.__id = id
        self.__timer = HardwareTimer(id)
        self.__irq_id = 0
        # sort on insert time, index 0 is the most recent irq
        self.__irqs = [] #(irq_id, callback, target_time_ms, mode, priod)

    @property
    def id(self):
        return self.__id

    def _timer_callback(self, _=None):
        if len(self.__irqs) <= 0:
            return
        irq = self.__irqs[0]
        irq_id, callback, target_time_ms, mode, priod = irq
        try:
            self.__irqs.remove(irq)
        except: pass
        if callback:
            try:
                callback(self)
            except Exception as e:
                print_exception(e)
        if mode == PERIODIC:
            self._insert_irq((irq_id, callback, ticks_add(target_time_ms, priod), mode, priod))
        self._set_timer()
        
    def _insert_irq(self, irq):
        # insert and sort
        target_time = irq[2]
        irqs = self.__irqs
        for i in range(len(irqs)):
            if ticks_diff(irqs[i][2], target_time) > 0:
                irqs.insert(i, irq)
                break
        else:
            irqs.append(irq)

    def _set_timer(self):
        if len(self.__irqs) > 0:
            target_time = self.__irqs[0][2]
            period = ticks_diff(target_time, ticks_ms())
            if period < 1:
                period = 1
            self.__timer.deinit()
            self.__timer.init(
                mode=HardwareTimer.ONE_SHOT,
                period=period,
                callback=lambda t: schedule(self._timer_callback, t)
            )

    def init(self, mode=ONE_SHOT, period=0, callback=None):
        irq_id = self.__irq_id
        self.__irq_id += 1
        irq = (irq_id, callback, ticks_add(ticks_ms(), period), mode, period)
        self._insert_irq(irq)
        self._set_timer()
        return irq_id

    def deinit(self, irq_id=-1):
        self.__timer.deinit()
        if irq_id < 0:
            self.__irqs.clear()
        else:
            for irq in self.__irqs:
                if irq[0] == irq_id:
                    self.__irqs.remove(irq)
        self._set_timer()

def get_shared_timer(id=0):
    for tid, shared_timer in _shared_timers:
        if tid == id:
            return shared_timer
    # not found, create one
    shared_timer = SharedTimer(id)
    _shared_timers.append((id, shared_timer))
    return shared_timer
