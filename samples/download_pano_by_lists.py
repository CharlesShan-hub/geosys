import csv
import os
import sys
from pathlib import Path
# from scons.Script import ARGUMENTS, Environment

# 读取CSV文件到列表
def read_csv_to_list(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        return [row for row in csv_reader]

# SCons环境
env = Environment()
python_executable = sys.executable

# 读取CSV文件与其他参数
BASE_DIR = os.getcwd() # 获取当前工作目录
DATA_DIR = ARGUMENTS.get('to', "samples/data") # 数据保存目录(相对于当前程序运行目录)
LEVEL = ARGUMENTS.get('level', 2) # 扩展的次数
DIS = ARGUMENTS.get('dis', 200)   # 限制距离
csv_file_path = ARGUMENTS.get('csv-file', './samples/pids.csv')
tasks = read_csv_to_list(csv_file_path)[1:]  # 跳过标题行

# 为CSV中的每一行创建一个SCons任务
for task in tasks:
    # 构建参数
    PID, FOLDER = task[0], task[6]
    OUT_DIR = Path(BASE_DIR,DATA_DIR,FOLDER)
    SCRIPT1_DIR = Path(BASE_DIR,'./scripts/grab_line_pano_info.py')
    SCRIPT2_DIR = Path(BASE_DIR,'./scripts/download_map_pano.py')

    # 调试输出
    print(f"OUT_DIR: {OUT_DIR}")
    print(f"SCRIPT1_DIR: {SCRIPT1_DIR}")
    print(f"SCRIPT2_DIR: {SCRIPT2_DIR}")

    # 创建文件夹
    env.Command(Path(OUT_DIR, "cache"), [], f'mkdir -p {Path(OUT_DIR, "cache")}')
    env.Command(Path(OUT_DIR, "tmp"), [], f'mkdir -p {Path(OUT_DIR, "tmp")}')
    env.Command(Path(OUT_DIR, "pano"), [], f'mkdir -p {Path(OUT_DIR, "pano")}')

    # 获取全景信息
    print('➡️ Gathering panorama information...')
    env.Execute(f'{python_executable} {SCRIPT1_DIR} {PID} -o {OUT_DIR} -l {LEVEL} -d {DIS}')

    # 检查 PID列表文件正确生成
    PIDS_DIR = Path(OUT_DIR,"tmp/pids.txt")
    if not os.path.exists(PIDS_DIR):
        print(f"Error: {PIDS_DIR} not found.")
        continue

    # 下载全景图片
    print('➡️ Downloading panoramas...')
    with open(f'{PIDS_DIR}','r') as f:
        lines = [line.strip() for line in f.readlines()]
        for pid in lines:
            env.Execute(f'{python_executable} {SCRIPT2_DIR} -t bmap {pid} -o {OUT_DIR}/pano')
    print(f'🍺 {PID}: Panorama download complete.')

# scons -f ./samples/download_pano_by_lists.py csv-file=./samples/pids.csv
