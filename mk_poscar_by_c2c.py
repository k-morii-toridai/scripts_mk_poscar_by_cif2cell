import re
import sys
import time
import itertools
import subprocess
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np


def iterdir_func(poscar_dir):
    return list(poscar_dir.iterdir())


def flatten_func(list_2dim):
    return list(itertools.chain.from_iterable(list_2dim))


def get_subdir_list(dir_list):
    return flatten_func(list(map(iterdir_func, dir_list)))


args = sys.argv  # receive a directory of cif/ path from command line
p = Path(args[1])
p_s_list = [p_sub_folder for p_sub_folder in p.glob('[1-9]')]
p_ssss_list = get_subdir_list(get_subdir_list(get_subdir_list(p_s_list)))


def cif_file_filter(path):
    pattern = r'.+\.cif$'
    string = str(path)
    return bool(re.search(pattern, string))


# make cif_file_filter
cif_file_path_list_filter = list(map(cif_file_filter, p_ssss_list))
# apply cif_file_filter to p_ssss_list
cif_file_path_list = np.array(p_ssss_list)[cif_file_path_list_filter]
print(f'len(cif_file_path_list): {len(cif_file_path_list)}')


def poscar_folder_filter(path):
    pattern = '[0-9]{6}$'  # 正規表現（：末尾が数字６文字で終わる）
    string = str(path)
    return bool(re.search(pattern, string))


# make filter
poscar_folder_path_list_filter = list(map(poscar_folder_filter, p_ssss_list))
# apply poscar_folder_filter to p_ssss_list
poscar_folder_path_list = np.array(p_ssss_list)[poscar_folder_path_list_filter]
print(f'len(poscar_folder_path_list): {len(poscar_folder_path_list)}')


# convert Path to str
cif_file_path_str_list = [str(p_cif) for p_cif in cif_file_path_list]
poscar_file_path_str_list = [str(p_folder) + '/POSCAR' for p_folder in poscar_folder_path_list]
poscar_folder_path_str_list = [str(p_folder) for p_folder in poscar_folder_path_list]
# zip above three lists
params = list(zip(cif_file_path_str_list, poscar_file_path_str_list, poscar_folder_path_str_list))


# convert cif to POSCAR and write out a standard output and error log as 'cif2cell_log.txt' at each directory
def cif2cell(cif_path, poscar_path, poscar_folder):
    with open(poscar_folder + '/cif2cell_log.txt', mode='w') as f:
        cp = subprocess.run(['cif2cell', cif_path, '-p', 'vasp', '-o', poscar_path, '--vasp-format=5'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,)
        print(cp.stdout, file=f)


def wrap_cif2cell(args):
    return cif2cell(*args)


# run cif2cell by using parallelization
before = time.time()
try:
    p = Pool(cpu_count() - 1)
    print("Now converting cif to POSCAR by cif2cell!!!")
    list(tqdm(p.imap(wrap_cif2cell, params), total=len(params)))
finally:
    p.close()
    p.join()
after = time.time()
print(f"it took {after - before}sec to run cif2cell all files.")
