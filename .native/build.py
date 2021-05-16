import sys, os, subprocess, shutil

current_path = os.path.abspath(os.path.dirname(__file__))
source_dir = os.path.join(current_path, "ubmfont_mixin")
output_path = os.path.join(current_path, "ubmfont_mixin", "ubmfont.mpy")
lib_path = os.path.join(current_path, "..", "lib", "ubmfont.mpy")

os.chdir(source_dir)

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    subprocess.run('''bash -c "source ~/esp-idf/export.sh && make ARCH=xtensawin DEBUG=1"''')
    shutil.copy2(output_path, lib_path)
    os.chdir(os.path.join(current_path, ".."))
    subprocess.run('''mpypack sync''')
    subprocess.run('''mpypack repl''')
else:
    subprocess.run('''bash -c "source ~/esp-idf/export.sh && make ARCH=xtensawin" ''')
    shutil.copy2(output_path, lib_path)