from play32sys import path
import t_rex_control

def main(app_name, *args, **kws):
    import hal_screen, hal_keypad, hal_buzz
    hal_screen.init()
    hal_keypad.init()
    hal_buzz.init()
    t_rex_control.init(path.get_app_path(app_name))
    t_rex_control.ready()
    t_rex_control.main_loop()
