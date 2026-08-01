# -*- coding: utf-8 -*-
"""
main.py —— C 盘清理助手的界面（tkinter GUI）
==============================================
界面只负责"展示和收集用户操作"，真正的扫描/删除都在 cleaner.py 里。

本文件值得学习的技术点：
  1. 类（class）组织界面组件，事件处理写成方法
  2. 线程（threading）：耗时的扫描/清理放到后台线程，
     界面用 消息队列（queue）+ 定时轮询 来刷新，窗口才不会卡死
"""

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from cleaner import CACHE_ITEMS, clean_item, format_bytes, scan_item


class CleanerApp:
    def __init__(self, root):
        self.root = root
        root.title("C 盘清理助手")
        root.geometry("680x560")
        root.minsize(560, 460)

        # 后台线程 -> 界面的"信箱"：线程不能直接改界面，
        # 只能把消息丢进队列，由界面定时来取（这是 tkinter 的标准做法）
        self.worker_queue = queue.Queue()

        self.check_vars = {}   # 每个清理项对应的勾选状态（tk.BooleanVar）
        self.size_labels = {}  # 每个清理项显示大小的标签
        self.busy = False      # 是否正在扫描/清理（防止同时点两次）

        self._build_ui()
        self._poll_queue()     # 启动定时轮询

    # ----------------------------- 界面搭建 -----------------------------

    def _build_ui(self):
        # 顶部提示
        tip = tk.Label(
            self.root,
            text="勾选要清理的项目 → 点「扫描」看占了多少 → 点「一键清理」\n"
                 "提示：右键本程序「以管理员身份运行」能清理得更干净",
            justify="left", fg="#555", anchor="w", padx=12, pady=8)
        tip.pack(fill="x")

        # 清理项列表区（每一行：勾选框 + 名称说明 + 占用大小）
        list_frame = ttk.Frame(self.root, padding=(12, 0))
        list_frame.pack(fill="both", expand=True)

        for i, item in enumerate(CACHE_ITEMS):
            var = tk.BooleanVar(value=False)
            self.check_vars[item["id"]] = var

            row = ttk.Frame(list_frame)
            row.pack(fill="x", pady=2)

            cb = ttk.Checkbutton(row, text=item["name"], variable=var)
            cb.pack(side="left")

            desc = tk.Label(row, text=item["desc"], fg="#888")
            desc.pack(side="left", padx=8)

            size_label = tk.Label(row, text="", fg="#0a7", width=10, anchor="e")
            size_label.pack(side="right")
            self.size_labels[item["id"]] = size_label

        # 操作按钮
        btn_frame = ttk.Frame(self.root, padding=(12, 6))
        btn_frame.pack(fill="x")

        self.scan_btn = ttk.Button(btn_frame, text="扫 描", command=self.start_scan)
        self.scan_btn.pack(side="left")

        self.clean_btn = ttk.Button(btn_frame, text="一键清理", command=self.start_clean)
        self.clean_btn.pack(side="left", padx=8)

        self.status_label = tk.Label(btn_frame, text="就绪", fg="#555")
        self.status_label.pack(side="right")

        # 进度条 + 日志
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=12)

        log_frame = ttk.Frame(self.root, padding=12)
        log_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # --------------------------- 界面小工具 ----------------------------

    def _log(self, text):
        """往日志区追加一行（先解锁再写再锁，是 Text 组件的固定操作）。"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_busy(self, busy):
        """扫描/清理期间禁用按钮，防止重复点击。"""
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.scan_btn.configure(state=state)
        self.clean_btn.configure(state=state)

    # ------------------------- 按钮事件（前台） -------------------------

    def start_scan(self):
        if self.busy:
            return
        self._set_busy(True)
        self.status_label.config(text="正在扫描…")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def start_clean(self):
        if self.busy:
            return
        selected = [item for item in CACHE_ITEMS
                    if self.check_vars[item["id"]].get()]
        if not selected:
            messagebox.showinfo("提示", "请先勾选要清理的项目")
            return
        if not messagebox.askyesno("确认", f"确定清理这 {len(selected)} 项吗？"):
            return
        self._set_busy(True)
        self.status_label.config(text="正在清理…")
        threading.Thread(target=self._clean_worker, args=(selected,), daemon=True).start()

    # ------------------- 后台线程（真正的干活部分） ----------------------

    def _scan_worker(self):
        """扫描线程：算出每一项的大小，通过队列发回界面。"""
        try:
            for item in CACHE_ITEMS:
                size = scan_item(item)
                self.worker_queue.put(("scan_item", item["id"], size))
            self.worker_queue.put(("done", "扫描完成"))
        except Exception as e:
            self.worker_queue.put(("done", f"扫描出错：{e}"))

    def _clean_worker(self, selected):
        """清理线程：逐项清理，进度通过队列发回界面。"""
        total = len(selected)
        for i, item in enumerate(selected, start=1):
            def progress(done, total_parts, text):
                self.worker_queue.put(
                    ("progress", i, total, f"{item['name']}: {text}"))
            try:
                result = clean_item(item, progress=progress)
                self.worker_queue.put(("clean_item", result))
            except Exception as e:
                self.worker_queue.put(
                    ("clean_item", {"item_id": item["id"], "item": item["name"],
                                    "freed": 0, "failed": 1, "messages": [str(e)]}))
        self.worker_queue.put(("done", "清理完成"))

    # ------------------- 定时轮询：把队列消息刷到界面 -------------------

    def _poll_queue(self):
        """每 100 毫秒来看一次信箱，把后台线程的消息处理掉。
        root.after 是 tkinter 的定时器，会反复调用自己，形成循环。
        """
        try:
            while True:
                msg = self.worker_queue.get_nowait()
                self._handle(msg)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _handle(self, msg):
        kind = msg[0]
        if kind == "scan_item":
            _, item_id, size = msg
            self.size_labels[item_id].config(text=format_bytes(size))
        elif kind == "progress":
            _, current, total, text = msg
            self.progress.configure(maximum=total, value=current)
            self.status_label.config(text=text)
        elif kind == "clean_item":
            result = msg[1]
            self._log(f"[{result['item']}] 释放 {format_bytes(result['freed'])}，"
                      f"失败 {result['failed']} 项")
            for m in result["messages"]:
                self._log("    " + m)
            self.size_labels[result["item_id"]].config(text="")
        elif kind == "done":
            _, text = msg
            self.status_label.config(text=text)
            self.progress.configure(value=0)
            self._set_busy(False)


def main():
    root = tk.Tk()
    CleanerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
