import logging
import subprocess
import os
import shutil

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量定义
SCRIPT_PATH = r"D:\Backup\Documents\PycharmProjects\venv\mouseclick\main.py"
SPEC_PATH = 'mouseclick.spec'
# ICON_NAME = 'icon.ico'  # 移除路径，只保留文件名
DIST_DIR = 'dist/'

def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

def install_dependencies():
    """安装项目依赖"""
    try:
        subprocess.run([
            'pip', 'install', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple', '-r', 'requirements.txt'
        ], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"安装依赖失败: {e}")
        exit(1)

def generate_spec_file(script_path=SCRIPT_PATH):
    check_file_exists(script_path)
    try:
        subprocess.run([
            'pyinstaller',
            '--name=mouseclick',
            '--onefile',
            '--windowed',
          #  '--icon=' + ICON_NAME,
            script_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"生成 .spec 文件失败: {e}")
        exit(1)

def modify_spec_file(spec_path=SPEC_PATH):
    check_file_exists(spec_path)
    with open(spec_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if 'Analysis([' in line:
            lines[i] += f"    datas=[('{ICON_NAME}', 'res')],\n"
            break

    with open(spec_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def build_executable(spec_path=SPEC_PATH):
    try:
        subprocess.run(['pyinstaller', spec_path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"构建可执行文件失败: {e}")
        exit(1)

def clean_up():
    shutil.rmtree('build', ignore_errors=True)
    for file in [SPEC_PATH, SPEC_PATH + '.bak']:
        if os.path.exists(file):
            os.remove(file)
    logging.info("临时文件已清理")

def main():
    logging.info("mouseclick启动")

    install_dependencies()
    generate_spec_file()
    modify_spec_file()
    build_executable()
    clean_up()

    logging.info("打包完成，可执行文件位于 %s 目录下", DIST_DIR)

if __name__ == "__main__":
    main()
