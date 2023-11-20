# for making cif_path_list
import time
from pathlib import Path
import re
from tqdm import tqdm
import subprocess


def get_subdir_list(p_sub_list):
    """
    To get a sub directory path list, Use thie func().
    
    pram: p_aub_list: specify a directory which sub dirs is gotten from.
    """
    # 引数の直下のディレクトリ・パスの一覧を取得
    sub_dir_list_temp = []
    for p_sub in tqdm(p_sub_list):
        sub_dir_list_temp.append([p_s_s for p_s_s in p_sub.iterdir()])
    # ２次元リストを１次元リスト化
    return sum(sub_dir_list_temp, [])


p = Path('../cif/')
p_sub_list = [p_s for p_s in p.glob('[0-9]')]


before = time.time()
cif_path_list = get_subdir_list(get_subdir_list(get_subdir_list(p_sub_list)))
after = time.time()
print(f"it took {after - before}sec to get all of subdir list.")


def cif_filter(cif_file_path):
    pattern = '.*\.cif'
    cif_file_path_str = str(cif_file_path)
    return bool(re.match(pattern, cif_file_path_str))


cif_path_list = [str(path) for path in cif_path_list if cif_filter(path)]


cif_path_list = [str(path) for path in cif_path_list if cif_filter(path)]
poscar_path_list = [str(cif_path)[0:-4] + '/POSCAR' for cif_path in cif_path_list]


error_list = []
before = time.time()

# TEST
# for cif_path, poscar_path in tqdm(zip(cif_path_list[0:10], poscar_path_list[0:10]), total=len(cif_path_list)):
# PERFORM
for cif_path, poscar_path in tqdm(zip(cif_path_list, poscar_path_list), total=len(cif_path_list)):
    try:
        subprocess.run(['cif2cell', cif_path, '-p', 'vasp', '-o', poscar_path, '--vasp-format=5'])
    except Exception as e:
        error_list.append(e)

after = time.time()
print(f"it took {after - before}sec to run cif2cell all files.")
