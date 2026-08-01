# 学习练习（exercises）

> **学习理念**：看 10 遍别人的代码，不如自己写 1 遍。
> 这套练习把项目里最值得学的 5 个函数挖了空，由你亲手补完，
> 再用**现成的单元测试**验证你写得对不对——跑绿 = 你学会了。

---

## 怎么用（每做一个练习的固定流程）

1. 打开练习文件（例如 `ex1_format_bytes.py`），读顶部的**任务说明**
2. 在 `pass` 的位置写出你自己的实现
3. 运行配套测试：

   ```bash
   python3 -m unittest discover -s exercises -p "*_test.py"
   ```

   （只跑某一个：`python3 -m unittest discover -s exercises -p "ex2*_test.py"`）

4. **全绿** ✅ → 打开 `cleaner.py` 里对应的函数，对比你的写法和参考答案，
   想想"哪里一样、哪里不一样、谁更好"
5. 提交一次 git（记录你的学习足迹）

> 先自己写！写不出来可以偷看 `cleaner.py`，但看之前先试 10 分钟。
> 实在写不出，抄一遍再自己默写一遍，也比只看有效。

---

## 练习总览（按难度递进，建议顺序）

| 练习 | 文件 | 你写的函数 | 知识点 | 难度 | 答案在 |
| --- | --- | --- | --- | --- | --- |
| 1 | `ex1_format_bytes.py` | `format_bytes()` | 函数、for 循环、if/else、字符串格式化 | ★☆☆☆☆ | `cleaner.py` 同名 |
| 2 | `ex2_scan_path.py` | `scan_path()` | `os.walk` 递归遍历、异常处理、类型判断 | ★★☆☆☆ | 同名 |
| 3 | `ex3_delete_force.py` | `_delete_force()` | 文件属性、`shutil.rmtree`、回调函数、异常处理 | ★★★☆☆ | 同名 |
| 4 | `ex4_clean_folder.py` | `clean_folder_contents()` | 列表、循环、可选参数（回调）、元组返回 | ★★★☆☆ | 同名 |
| 5 | `ex5_clean_item.py` | `clean_item()` | 字典、分支逻辑、数据驱动、结果汇总 | ★★★★☆ | 同名 |

**完成标准**：能不看答案写出 ex5，并且说得出每个函数"为什么这么写"，
这个项目的核心逻辑你就真的吃透了。

---

## 对应关系：整个项目长什么样

```
c-clear/
├── main.py    界面层：tkinter 窗口、按钮、进度条、日志
│              （WSL 里跑不了，留在 Windows 上体验；知识点见 README）
├── cleaner.py 逻辑层：全部清理功能 ← 练习 1~5 挖的就是这个文件
├── tests/     项目自己的单元测试（和 exercises/ 的测试类似，只是测完整版）
└── exercises/ 你的练习区（本目录）
```

`cleaner.py` 的"骨架"你已经在练习里写过了，所以它对你来说不再是天书——
**你写的函数拼起来，就是这个项目**。
