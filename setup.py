from distutils.core import setup
import py2exe
import sys
import os

# 添加对图标的支持
sys.argv.append('py2exe')

# 设置图标路径
icon_path = r"D:\Backup\Documents\PycharmProjects\venv\mouseclick\icon.ico"

setup(
    options={
        'py2exe': {
            'bundle_files': 1,  # 打包成单个可执行文件
            'compressed': True,  # 压缩文件
            'optimize': 2,      # 优化级别
            'includes': ['ctypes', 'keyboard', 'tkinter'],  # 包含的额外模块
            'excludes': ['MSVCP90.dll'],  # 排除的 DLL
            'dll_excludes': ['MSVCP90.dll'],  # 排除的 DLL
        }
    },
    console=[
        {
            'script': r"D:\Backup\Documents\PycharmProjects\venv\mouseclick\main.py",  # 使用原始字符串
            'icon_resources': [(1, icon_path)],
        }
    ],
    zipfile=None,  # 打包成单个文件时使用
)
