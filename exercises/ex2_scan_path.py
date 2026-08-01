# -*- coding: utf-8 -*-
"""
练习 2：scan_path —— 递归统计文件/目录占多少字节
==================================================
难度：★★☆☆☆
知识点：os.walk 递归遍历、类型判断（文件/目录）、异常处理

任务：完成 scan_path(path) 函数，返回 path 占用的字节数（整数）。

规则：
  - path 不存在：返回 0
  - path 是单个文件：返回它的大小（用 os.path.getsize(path)）
  - path 是目录：递归累加里面所有文件的大小
  - 某个文件读不到（被占用/无权限）：跳过它，绝不能抛异常

提示（递归遍历目录的经典写法）：
    for root, dirs, files in os.walk(path):
        for name in files:
            fp = os.path.join(root, name)
            # 用 try/except 包住 getsize，读不到就 pass 跳过

写完运行测试：
  python3 -m unittest discover -s exercises -p "ex2*_test.py"
完成后打开 cleaner.py 里的 scan_path 对比。
"""

import os


def scan_path(path):
    # TODO: 在这里写你的实现（写好后删掉下面这行）
    pass
