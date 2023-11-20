import os
import sys
import itertools
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool, cpu_count


def iterdir_func(poscar_dir):
    return list(poscar_dir.iterdir())


def flatten_func(list_2dim):
    return list(itertools.chain.from_iterable(list_2dim))


def get_subdir_list(dir_list):
    return flatten_func(list(map(iterdir_func, dir_list)))


args = sys.argv  # コマンドラインからcifディレクトリのパスを受け取る
p = Path(args[1])
p_s_list = [p_sub_folder for p_sub_folder in p.glob('[1-9]')]
p_ssss_list = get_subdir_list(get_subdir_list(get_subdir_list(p_s_list)))
cif_num_name_list = [str(cif_p)[:-4] for cif_p in p_ssss_list]

# 並列化して，cifファイル名のフォルダを作成
try:
    pp = Pool(cpu_count() - 1)
    # iterdir
    list(tqdm(pp.imap(os.makedirs, cif_num_name_list), total=len(cif_num_name_list)))
finally:
    pp.close()
    pp.join()
