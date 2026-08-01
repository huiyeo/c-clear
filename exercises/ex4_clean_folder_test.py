# -*- coding: utf-8 -*-
"""练习 4 的测试：验证你的 clean_folder_contents 实现。"""

import importlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("EX_SOURCE", HERE))
ex4 = importlib.import_module("ex4_clean_folder")
clean_folder_contents = ex4.clean_folder_contents


class TestCleanFolderContents(unittest.TestCase):
    def test_not_a_directory(self):
        self.assertEqual(clean_folder_contents("/definitely/not/a/dir"), (0, 0))

    def test_clears_contents_keeps_folder(self):
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "sub")
            os.makedirs(sub)
            with open(os.path.join(d, "a.txt"), "wb") as f:
                f.write(b"a" * 100)
            with open(os.path.join(sub, "b.txt"), "wb") as f:
                f.write(b"b" * 200)
            freed, failed = clean_folder_contents(d)
            self.assertEqual(failed, 0)
            self.assertEqual(freed, 300)
            # 目录还在，但里面已经空了
            self.assertTrue(os.path.isdir(d))
            self.assertEqual(os.listdir(d), [])

    def test_progress_callback_is_called(self):
        # progress 回调应该被调用 2 次（里面有 2 个子项），且参数合理
        with tempfile.TemporaryDirectory() as d:
            for name in ("f1.txt", "f2.txt"):
                with open(os.path.join(d, name), "w") as f:
                    f.write("x")
            calls = []
            clean_folder_contents(d, progress=lambda done, total, text: calls.append((done, total)))
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[-1], (2, 2))  # 最后一次：已完成 2 / 共 2


if __name__ == "__main__":
    unittest.main(verbosity=2)
