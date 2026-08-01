# -*- coding: utf-8 -*-
"""练习 2 的测试：验证你的 scan_path 实现。"""

import importlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("EX_SOURCE", HERE))
ex2 = importlib.import_module("ex2_scan_path")
scan_path = ex2.scan_path


class TestScanPath(unittest.TestCase):
    def test_missing_path_is_zero(self):
        missing = os.path.join(tempfile.gettempdir(), "不存在的_xyz_练习2")
        self.assertEqual(scan_path(missing), 0)

    def test_single_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 100)
            path = f.name
        try:
            self.assertEqual(scan_path(path), 100)
        finally:
            os.remove(path)

    def test_directory_recursive(self):
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "sub")
            os.makedirs(sub)
            with open(os.path.join(d, "a.txt"), "wb") as f:
                f.write(b"a" * 10)
            with open(os.path.join(sub, "b.txt"), "wb") as f:
                f.write(b"b" * 20)
            # 10 + 20 = 30 字节
            self.assertEqual(scan_path(d), 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
