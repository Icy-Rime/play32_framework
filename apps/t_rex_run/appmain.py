from play32sys import path
import t_rex_control

def main(app_name, *args, **kws):
    t_rex_control.init(path.get_app_path(app_name))
    t_rex_control.ready()
    t_rex_control.main_loop()
