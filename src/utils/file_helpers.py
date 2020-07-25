from pathlib import Path
import subprocess as sp

def get_file_name(path):
    return Path(path).stem

def get_file_size(path):
    r = sp.run(f'wc -l {path}', capture_output=True, shell=True)
    return int(r.stdout.split()[0].decode('utf-8'))