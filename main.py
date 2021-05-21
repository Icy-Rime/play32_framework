# >>>> init <<<<
import hal_screen, hal_keypad, hal_buzz
hal_screen.init()
hal_keypad.init()
hal_buzz.init()

# >>>> main <<<<
from play32sys import app
app._on_boot_(True)

# test below
