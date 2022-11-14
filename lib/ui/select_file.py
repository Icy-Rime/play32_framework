from ui.utils import sleep_save_power
from play32hw.cpu import cpu_speed_context, VERY_SLOW
import uos
from play32sys import path
from ui.progress import progress_gen
from ui.select import select_list_gen

def _get_parent_dir(file_path):
    if file_path == "/":
        return "/"
    end_p = len(file_path)
    if file_path.endswith("/"):
        end_p -= 1
    index = file_path.rfind("/")
    if index > 0:
        return file_path[:index]
    return "/"

def select_file(cwd=None, title="Files", text_yes="OK", text_no="CANCEL", f_file=True, f_dir=True):
    with cpu_speed_context(VERY_SLOW):
        for v in select_file_gen(cwd, title, text_yes, text_no, f_file, f_dir):
            if v != None:
                return v
            sleep_save_power() # save power

def select_file_gen(cwd=None, title="Files", text_yes="OK", text_no="CANCEL", f_file=True, f_dir=True):
    if cwd == None:
        cwd = uos.getcwd()
    cwd = path.abspath(cwd)
    gen_loading = progress_gen("", title)
    while True:
        if f_dir:
            files = [(False, "."), (False, "..")]
        else:
            files = [(False, "..")]
        for item in uos.ilistdir(cwd):
            gen_loading.send(None)
            yield None
            name = item[0]
            file_type = item[1]
            if (not f_file) and file_type != 0x4000:
                continue # filter file
            files.append((file_type != 0x4000, name))
        files.sort()
        files_list = [ x[1] for x in files]
        gen_select_in_list = select_list_gen(title, files_list, text_yes, text_no)
        selected_file_is_file = False
        selected_file = "."
        for v in gen_select_in_list:
            yield None
            if v != None:
                if v < 0:
                    yield "" # cancel
                else:
                    selected_file_is_file = files[v][0]
                    selected_file = files[v][1]
                    break
        if selected_file == ".":
            yield cwd
        elif selected_file == "..":
            cwd = _get_parent_dir(cwd)
            # continue
        else:
            new_path = path.join(cwd, selected_file)
            if selected_file_is_file:
                yield new_path
            else:
                cwd = new_path
                # continue
