# -*- coding: utf-8 -*-
"""练习 3 的测试：验证你的 _delete_force 实现。"""

import importlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("EX_SOURCE", HERE))
ex3 = importlib.import_module("ex3_delete_force")
_delete_force = ex3._delete_force


class TestDeleteForce(unittest.TestCase):
    def test_missing_returns_true(self):
        missing = os.path.join(tempfile.gettempdir(), "不存在的_xyz_练习3")
        self.assertTrue(_delete_force(missing))

    def test_delete_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"data")
            path = f.name
        self.assertTrue(_delete_force(path))
        self.assertFalse(os.path.exists(path))

    def test_delete_readonly_file(self):
        # 只读文件也能删：_delete_force 要先去掉只读属性
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"data")
            path = f.name
        try:
            os.chmod(path, 0o444)
            self.assertTrue(_delete_force(path))
            self.assertFalse(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_delete_directory_with_readonly_child(self):
        # 目录里套着只读文件，也要能整个删掉
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "sub")
            os.makedirs(sub)
            child = os.path.join(sub, "ro.txt")
            with open(child, "w") as f:
                f.write("x")
            os.chmod(child, 0o444)
            self.assertTrue(_delete_force(d))
            self.assertFalse(os.path.exists(d))


if __name__ == "__main__":
    unittest.main(verbosity=2)
