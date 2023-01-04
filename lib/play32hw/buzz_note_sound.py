''' bee_note_sound
special sound format for bee
BeeNoteSoundFrame: Tuple[time, type, padding, data]
'''
import ustruct as struct
from micropython import const
from utime import ticks_ms, ticks_diff, ticks_add
from play32hw.shared_timer import SharedTimer, get_shared_timer

TYPE_EMIT_EVENT = const(0X00)
TYPE_SET_TEMPO = const(0X01)
TYPE_NOTE_ON = const(0X02)
TYPE_NOTE_OFF = const(0X03)
_DEFAULT_TICKS_PER_BEAT = const(480)
_DEFAULT_TEMPO = const(500_000)
_FREQ_QUITE = const(100_000)
# index 0 is note C0
_NOTE_FREQ = [
    16,    17,    18,    19,    21,    22,    23,    24,    26,    28,    29,    31,
    33,    35,    37,    39,    41,    44,    46,    49,    52,    55,    58,    62,
    65,    69,    73,    78,    82,    87,    92,    98,    104,   110,   117,   123,
    131,   139,   147,   156,   165,   175,   185,   196,   208,   220,   233,   247,
    262,   277,   294,   311,   330,   349,   370,   392,   415,   440,   466,   494,
    523,   554,   587,   622,   659,   698,   740,   784,   831,   880,   932,   988,
    1046,  1109,  1175,  1244,  1318,  1397,  1480,  1568,  1661,  1760,  1865,  1976,
    2093,  2218,  2349,  2489,  2637,  2794,  2960,  3136,  3322,  3520,  3729,  3951,
    4186,  4435,  4699,  4978,  5274,  5588,  5920,  6272,  6645,  7040,  7459,  7902,
    8372,  8870,  9397,  9956,  10548, 11175, 11840, 12544, 13290, 14080, 14917, 15804
]
_VOLUME_DUTY = [1023, 1022, 1020, 1017, 1015, 1010, 1000, 985, 960, 512]

def parse_bee_frame(data):
    ''' return: (time, frame_type, padding, frame_data) '''
    return struct.unpack(">HBB4s", data)

def parse_bee_header(data):
    ''' return: (b'bns\x00', ticks_per_beat, frame_count) '''
    return struct.unpack(">4sHI", data)

class BuzzNoteSoundFile():
    def __init__(self, file_name):
        self.file = open(file_name, "rb")
        header_data = self.file.read(10)
        magic, ticks_per_beat, frame_count = parse_bee_header(header_data)
        assert magic == b'bns\x00'
        self.ticks_per_beat = ticks_per_beat
        self.frame_count = frame_count

class BuzzPlayer():
    def __init__(self, bee_gpio_num, timer_id_num):
        from machine import Pin, PWM
        self.__pwm = PWM(Pin(bee_gpio_num), freq=_FREQ_QUITE, duty=_VOLUME_DUTY[0])
        self.__timer = get_shared_timer(timer_id_num)
        self.__timer_id = 0
        self.__target_note_time = ticks_ms()
        self.__volume = len(_VOLUME_DUTY) - 1
        self.__note_shift = 0
        self.__buzz_file = None
        # self.__ticks_per_beat = _DEFAULT_TICKS_PER_BEAT
        # self.__frame_count = 0
        self.__frame_pointer = 0
        self.__tempo = _DEFAULT_TEMPO
        self.__event_callback = None
        self.__loop = False
        # status
        self.__is_playing = False
    
    @property
    def is_playing(self):
        return self.__is_playing
    
    @property
    def volume(self):
        return self.__volume

    @property
    def note_shift(self):
        return self.__note_shift

    def _timer_callback(self, _=None):
        # schedule(self.play_next_note, True)
        self.play_next_note(True)

    def note_on(self, note, volume):
        note = note + self.__note_shift
        note = 0 if note < 0 else note
        note = len(_NOTE_FREQ) - 1 if note >= len(_NOTE_FREQ) else note
        self.__pwm.freq(_NOTE_FREQ[note])
        self.__pwm.duty(_VOLUME_DUTY[volume])

    def note_off(self):
        self.__pwm.duty(_VOLUME_DUTY[0])

    def play_next_note(self, play_next_note=False):
        try:
            time, frame_type, padding, frame_data = parse_bee_frame(self.__buzz_file.file.read(8))
            time = time * self.__tempo // self.__buzz_file.ticks_per_beat // 1000 # us -> ms
            # play next note
            self.__frame_pointer += 1
            if self.__frame_pointer < self.__buzz_file.frame_count and play_next_note and time > 0:
                # set timer event as soon as possible
                self.__target_note_time = ticks_add(self.__target_note_time, time)
                target_period = ticks_diff(self.__target_note_time, ticks_ms())
                self.__timer_id = self.__timer.init(mode=SharedTimer.ONE_SHOT, period=target_period, callback=self._timer_callback)
            # deal with frame
            if frame_type == TYPE_SET_TEMPO:
                self.__tempo = int.from_bytes(frame_data, 'big')
            elif frame_type == TYPE_NOTE_OFF:
                self.note_off()
            elif frame_type == TYPE_NOTE_ON:
                self.note_on(frame_data[0], self.__volume)
            elif frame_type == TYPE_EMIT_EVENT and self.__event_callback != None:
                self.__event_callback(frame_data, padding)
            # control next note
            if self.__frame_pointer < self.__buzz_file.frame_count and play_next_note and time <= 0:
                self.play_next_note(True)
                return time
            if self.__frame_pointer >= self.__buzz_file.frame_count:
                if self.__loop:
                    self.start(True)
                else:
                    self.stop()
            return time
        except Exception as e:
            import usys
            usys.print_exception(e)

    def init(self):
        self.__pwm.init(freq=_FREQ_QUITE, duty=_VOLUME_DUTY[0])

    def deinit(self):
        self.stop()
        self.unload()
        self.__pwm.deinit()

    def start(self, loop=False):
        self.__is_playing = True
        self.__loop = loop
        self.__frame_pointer = 0
        self.__buzz_file.file.seek(10)
        self.__target_note_time = ticks_ms()
        self.__timer_id = self.__timer.init(mode=SharedTimer.ONE_SHOT, period=1, callback=self._timer_callback)

    def stop(self):
        self.__timer.deinit(self.__timer_id)
        self.__pwm.freq(_FREQ_QUITE)
        self.__pwm.duty(_VOLUME_DUTY[0])
        self.__is_playing = False

    def load(self, buzz_sound_file):
        self.__buzz_file = buzz_sound_file

    def unload(self):
        self.__tempo = _DEFAULT_TEMPO
        self.__buzz_file = None

    def set_volume(self, volume):
        ''' set volume 0~9 '''
        volume = 0 if volume < 0 else volume
        volume = len(_VOLUME_DUTY) - 1 if volume >= len(_VOLUME_DUTY) else volume
        self.__volume = volume
    
    def set_note_shift(self, note_shift):
        ''' set volume 0~9 '''
        self.__note_shift = note_shift

    def set_event_callback(self, callback):
        ''' set event callback, (event_data, padding) -> None '''
        self.__event_callback = callback

class DummyBuzzPlayer():
    def __init__(self, bee_gpio_num, timer_id_num):
        pass
    
    @property
    def is_playing(self):
        return False
    
    @property
    def volume(self):
        return 0

    @property
    def note_shift(self):
        return 0

    def _timer_callback(self, _=None):
        # schedule(self.play_next_note, True)
        pass

    def note_on(self, note, volume):
        pass

    def note_off(self):
        pass

    def play_next_note(self, play_next_note=False):
        pass

    def init(self):
        pass

    def deinit(self):
        pass

    def start(self, loop=False):
        pass

    def stop(self):
        pass

    def load(self, buzz_sound_file):
        pass

    def unload(self):
        pass

    def set_volume(self, volume):
        ''' set volume 0~9 '''
        pass
    
    def set_note_shift(self, note_shift):
        ''' set volume 0~9 '''
        pass

    def set_event_callback(self, callback):
        ''' set event callback, (event_data, padding) -> None '''
        pass
