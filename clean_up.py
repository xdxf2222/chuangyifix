import os
import shutil


def clean_up():
    """清理临时文件"""
    # 删除 build 目录
    shutil.rmtree('build', ignore_errors=True)

    # 删除 .spec 文件
    if os.path.exists('mouseclick.spec'):
        os.remove('mouseclick.spec')

    # 删除 .spec.bak 文件
    if os.path.exists('mouseclick.spec.bak'):
        os.remove('mouseclick.spec.bak')

    print("临时文件已清理")