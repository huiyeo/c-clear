# -*- coding: utf-8 -*-
"""
练习 3：_delete_force —— 尽力删除一个文件或目录
=================================================
难度：★★★☆☆
知识点：类型判断、文件属性（只读）、shutil.rmtree、回调函数、异常处理

任务：完成 _delete_force(path) 函数，删除成功返回 True，失败返回 False。
规则（按顺序判断）：
  1. path 是目录：递归删除整个目录
     - 目录里可能有只读文件，shutil.rmtree 会删不动，
       这时要用 onerror 回调：删失败 -> 先 chmod 去只读 -> 再重试一次
  2. path 是文件：先 os.chmod(path, stat.S_IWRITE) 去掉只读，再 os.remove
  3. path 不存在：返回 True（没什么可删的，就算成功）
  4. 任何删除失败：返回 False，绝不能抛异常

提示（rmtree + onerror 的固定写法，理解"回调"概念）：
    def onerror(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)          # func 就是刚才失败的那个操作（比如 os.remove）
        except OSError:
            pass
    shutil.rmtree(path, onerror=onerror)

写完运行测试：
  python3 -m unittest discover -s exercises -p "ex3*_test.py"
完成后打开 cleaner.py 里的 _delete_force 对比。
"""

import os
import shutil
import stat


def _delete_force(path):
    # TODO: 在这里写你的实现（写好后删掉下面这行）
    pass
