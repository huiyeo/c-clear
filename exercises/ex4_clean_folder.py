# -*- coding: utf-8 -*-
"""
练习 4：clean_folder_contents —— 清空一个目录（保留目录本身）
===============================================================
难度：★★★☆☆
知识点：列表、for 循环、可选参数（回调函数）、元组返回、计数器

任务：完成 clean_folder_contents(path, progress=None) 函数。
它删除 path 目录里的"所有内容"，但保留目录本身（因为系统还引用着它）。

规则：
  - path 不是目录：直接返回 (0, 0)
  - 用 os.listdir(path) 拿到里面的所有子项（文件和文件夹都有）
  - 对每个子项：
      先算它的大小（scan_path），再删除（_delete_force）
      删除成功 → 释放量加上这个大小
      删除失败 → failed 计数 + 1
  - 每处理完一个子项，如果 progress 不为 None，就调用一次：
      progress(已完成数量, 总数, 子项名字)     ← 界面靠它显示进度
  - 返回 (释放字节数, 失败数量)

下方已经 import 了现成的 scan_path 和 _delete_force
（就是你练习 2、3 写过的函数，这里直接用项目的实现，专注练循环和回调）

提示：想同时拿到"第几个"和"内容"？for i, name in enumerate(列表) 了解一下。

写完运行测试：
  python3 -m unittest discover -s exercises -p "ex4*_test.py"
完成后打开 cleaner.py 里的 clean_folder_contents 对比。
"""

import os

from cleaner import _delete_force, scan_path


def clean_folder_contents(path, progress=None):
    # TODO: 在这里写你的实现（写好后删掉下面这行）
    pass
