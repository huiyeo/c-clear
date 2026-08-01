# -*- coding: utf-8 -*-
"""练习 1 的测试：验证你的 format_bytes 实现。"""

import importlib
import os
import sys
import unittest

# 优先从 EX_SOURCE 目录加载练习模块（这是给"参考答案验证"用的，
# 你正常使用时不用管；没设置就加载本目录下的练习文件）
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("EX_SOURCE", HERE))
ex1 = importlib.import_module("ex1_format_bytes")
format_bytes = ex1.format_bytes


class TestFormatBytes(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(1023), "1023 B")

    def test_kb(self):
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1536), "1.5 KB")

    def test_mb(self):
        self.assertEqual(format_bytes(1572864), "1.5 MB")

    def test_large(self):
        self.assertEqual(format_bytes(1073741824), "1.0 GB")


if __name__ == "__main__":
    unittest.main(verbosity=2)
