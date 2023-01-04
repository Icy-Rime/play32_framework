from play32hw.punix.usdl2 import SDL_Init, SDL_INIT_AUDIO
from play32hw.punix.usdl2 import SDL_AudioSpec, SDL_AUDIO_U8, SDL_AUDIO_CHANNEL_MONO
from play32hw.punix.usdl2 import SDL_OpenAudioDevice, SDL_PauseAudioDevice, SDL_QueueAudio, SDL_GetQueuedAudioSize, SDL_ClearQueuedAudio
from play32hw.shared_timer import get_shared_timer, SharedTimer
from play32hw.buzz_note_sound import parse_bee_frame
from utime import ticks_ms, ticks_add, ticks_diff, sleep_ms
from _thread import get_ident, allocate_lock, start_new_thread
from usys import print_exception
from micropython import const

TYPE_EMIT_EVENT = const(0X00)
TYPE_SET_TEMPO = const(0X01)
TYPE_NOTE_ON = const(0X02)
TYPE_NOTE_OFF = const(0X03)
_DEFAULT_TICKS_PER_BEAT = const(480)
_DEFAULT_TEMPO = const(500_000)

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

class BeeAudioGenerator:
    def __init__(self, audio_freq, audio_channels, audio_sample_size):
        self.channels = audio_channels
        self.rate = audio_freq
        self.sp_size = audio_sample_size # bytes size, SDL_AUDIO_U8 is 1, SDL_AUDIO_U16LSB is 2
        self.freq = 0
        self.duty = 512 # [0, 1024]
        self.volume = 9 # [0, 9]
        self.samples_count = 0
        self.__thd = None
        self.__lock = allocate_lock()
    
    def __protect(fn):
        def func(self, *args, **kwargs):
            if not isinstance(self, BeeAudioGenerator) or get_ident() == self.__thd:
                return fn(self, *args, **kwargs)
            else:
                self.__lock.acquire()
                self.__thd = get_ident()
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    self.__thd = None
                    self.__lock.release()
        return func
    
    @__protect
    def set_freq(self, freq):
        self.freq = freq
        self.samples_count = 0
    
    @__protect
    def set_duty(self, duty):
        assert duty >= 0 and duty <= 1024
        self.duty = duty
        self.samples_count = 0
    
    @__protect
    def set_volume(self, volume):
        assert volume >= 0 and volume <= 9
        self.volume = volume
    
    @__protect
    def gen_buffer(self, buffer_size):
        sample_size = self.channels * self.sp_size
        samples = buffer_size // sample_size
        buffer = bytearray(samples * sample_size)
        rate = self.rate
        freq = self.freq
        duty = self.duty
        volume = self.volume * 255 // 9
        if duty == 0 or freq == 0 or volume == 0:
            return buffer
        elif duty >= 1024:
            for i in len(buffer):
                buffer[i] = volume
            return buffer
        sp_count = self.samples_count
        duty_sp = rate * duty // (1024 * freq)
        for i in range(samples):
            sp = sp_count + i
            sp_in_circle = sp * freq % rate // freq
            if sp_in_circle <= duty_sp:
                value = volume
            else:
                value = 0
            offset = i * sample_size
            offset_end = offset + sample_size
            for p in range(offset, offset_end):
                buffer[p] = value
        self.samples_count = (sp_count + samples) % rate
        return buffer

class SDLAudioFeeder:
    def __init__(self) -> None:
        SDL_Init(SDL_INIT_AUDIO)
        desired = SDL_AudioSpec(44100, SDL_AUDIO_U8, SDL_AUDIO_CHANNEL_MONO, 256)
        obtained = SDL_AudioSpec()
        self.__a_dev = SDL_OpenAudioDevice("", False, desired, obtained, 0)
        SDL_PauseAudioDevice(self.__a_dev, False)
        self.__b_gen = BeeAudioGenerator(44100, 1, 1)
        self.__target_sample_size = 2048 # 100ms, 44100*1*1 / s
        self.__thd = None
        self.__lock = allocate_lock()
        self.__keep = False
        self.__start_background()
    
    def __protect(fn):
        def func(self, *args, **kwargs):
            if not isinstance(self, SDLAudioFeeder) or get_ident() == self.__thd:
                return fn(self, *args, **kwargs)
            else:
                self.__lock.acquire()
                self.__thd = get_ident()
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    self.__thd = None
                    self.__lock.release()
        return func

    @property
    def bee_generator(self):
        return self.__b_gen
    
    def __feeder(self):
        while True:
            try:
                self.__lock.acquire()
                if not self.__keep:
                    continue
                buffered = SDL_GetQueuedAudioSize(self.__a_dev)
                lack_of_bytes = self.__target_sample_size - buffered
                data = self.__b_gen.gen_buffer(lack_of_bytes)
                SDL_QueueAudio(self.__a_dev, data)
            except Exception as e:
                print_exception(e)
            finally:
                self.__lock.release()

    def __start_background(self):
        start_new_thread(self.__feeder, tuple())
    
    def __set_keep(self, keep):
        self.__keep = keep

    @__protect
    def note_off(self):
        SDL_ClearQueuedAudio(self.__a_dev)
        self.__b_gen.set_volume(0)
        self.__b_gen.set_freq(0)
        self.__set_keep(False)
    
    @__protect
    def note_on(self, note, volume, length_ms = -1):
        self.__b_gen.set_freq(_NOTE_FREQ[note])
        self.__b_gen.set_volume(volume)
        if length_ms < 0:
            SDL_ClearQueuedAudio(self.__a_dev)
            data = self.__b_gen.gen_buffer(self.__target_sample_size)
            SDL_QueueAudio(self.__a_dev, data)
            self.__set_keep(True)
        else:
            data = self.__b_gen.gen_buffer(length_ms * 44100 // 1000)
            SDL_QueueAudio(self.__a_dev, data)
            self.__set_keep(False)
    
class SDLBuzzPlayer:
    def __init__(self, timer_id_num):
        self.__timer = get_shared_timer(timer_id_num)
        self.__timer_id = 0
        self.__target_note_time = ticks_ms()
        self.__volume = 9
        self.__note_shift = 0
        self.__buzz_file = None
        self.__frame_pointer = 0
        self.__tempo = _DEFAULT_TEMPO
        self.__event_callback = None
        self.__loop = False
        # SDL
        self.__feeder = SDLAudioFeeder()
        self.__b_gen = self.__feeder.bee_generator
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
        self.__feeder.note_on(note, volume)

    def note_off(self):
        self.__feeder.note_off()

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
                # self.note_off()
                self.__feeder.note_on(0, 0, length_ms=time)
                pass
            elif frame_type == TYPE_NOTE_ON:
                note = frame_data[0] + self.__note_shift
                note = 0 if note < 0 else note
                note = len(_NOTE_FREQ) - 1 if note >= len(_NOTE_FREQ) else note
                self.__feeder.note_on(note, self.__volume, length_ms=time)
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
            print_exception(e)

    def init(self):
        pass

    def deinit(self):
        self.stop()
        self.unload()

    def start(self, loop=False):
        self.__is_playing = True
        self.__loop = loop
        self.__frame_pointer = 0
        self.__buzz_file.file.seek(10)
        self.__target_note_time = ticks_ms()
        self.__timer_id = self.__timer.init(mode=SharedTimer.ONE_SHOT, period=1, callback=self._timer_callback)

    def stop(self):
        self.__timer.deinit(self.__timer_id)
        self.note_off()
        self.__is_playing = False

    def load(self, buzz_sound_file):
        self.__buzz_file = buzz_sound_file

    def unload(self):
        self.__tempo = _DEFAULT_TEMPO
        self.__buzz_file = None

    def set_volume(self, volume):
        ''' set volume 0~9 '''
        volume = 0 if volume < 0 else volume
        volume = 9 if volume > 9 else volume
        self.__volume = volume
    
    def set_note_shift(self, note_shift):
        ''' set volume 0~9 '''
        self.__note_shift = note_shift

    def set_event_callback(self, callback):
        ''' set event callback, (event_data, padding) -> None '''
        self.__event_callback = callback

__inited = False
__buzz = None # type: SDLBuzzPlayer

def init():
    global __inited, __buzz
    if __inited:
        return
    __buzz = SDLBuzzPlayer(0)
    __inited = True

def get_buzz_player():
    return __buzz