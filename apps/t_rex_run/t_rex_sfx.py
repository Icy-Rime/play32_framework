import hal_buzz
from play32hw.buzz_note_sound import BuzzNoteSoundFile
from play32sys import path
BUZZ_IO = 4

buzz = None
sound_press = None
sound_crash = None
def init(app_path):
    global buzz, sound_press, sound_crash
    bns_dir = path.join(app_path, "bns")
    buzz = hal_buzz.get_buzz_player()
    sound_press = BuzzNoteSoundFile(path.join(bns_dir, "t_rex_press.bns"))
    sound_crash = BuzzNoteSoundFile(path.join(bns_dir, "t_rex_crash.bns"))

def press():
    buzz.load(sound_press)
    buzz.start()

def crash():
    buzz.load(sound_crash)
    buzz.start()