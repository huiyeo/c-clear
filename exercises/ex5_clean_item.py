# -*- coding: utf-8 -*-
"""
练习 5（挑战）：clean_item —— 统一调度一个清理项
==================================================
难度：★★★★☆
知识点：字典、分支逻辑、数据驱动（一份清单驱动整个程序）、结果汇总

这是项目里最"综合"的一个函数，把前 4 个练习全部串起来。
完成它，你就理解了整个 cleaner.py 的骨架。

任务：完成 clean_item(item, progress=None)，返回一个"结果字典"。

参数 item 是一个字典（界面上每个复选框对应一个）：
    {"id": "唯一编号", "name": "显示名", "kind": ..., "paths": 函数, ...}
    kind 有三种：
      "recycle_bin" —— 回收站，特殊处理
      "folder"      —— 目录，删内容留目录
      "files"       —— 单个文件，直接删

逻辑（照抄这个顺序写）：
  1. 先准备返回字典：
       result = {"item_id": item["id"], "item": item["name"],
                 "freed": 0, "failed": 0, "messages": []}
  2. 如果 kind 是 "recycle_bin"：
       调用 empty_recycle_bin()，得到 (是否成功, 提示文字)
       把提示文字 append 进 result["messages"]
       失败的话 result["failed"] 记 1
       直接 return result
  3. 否则：paths = item["paths"]() 得到路径列表，过滤掉空串
       - 列表为空：messages 加一句"未找到目标路径"，return result
       - kind 是 "files"：对每个路径 p：
            size = scan_path(p)
            删除成功（_delete_force）→ freed += size，否则 failed += 1
       - kind 是 "folder"：对每个路径 p：
            freed, failed = clean_folder_contents(p, progress)  ← 注意元组拆包
            累加到 result
       （每处理完一个位置可以调 progress 报告进度，界面会显示）
  4. 收尾：messages 加总结，有 failed 就说明"有 X 个文件被占用或无权删除"，
     否则加"清理完成"。
  5. return result

已为你 import 好所有工具：scan_path, _delete_force, clean_folder_contents, empty_recycle_bin

写完运行测试：
  python3 -m unittest discover -s exercises -p "ex5*_test.py"
完成后打开 cleaner.py 里的 clean_item 对比。
"""

from cleaner import (_delete_force, clean_folder_contents, empty_recycle_bin,
                     scan_path)


def clean_item(item, progress=None):
    # TODO: 在这里写你的实现（写好后删掉下面这行）
    pass
