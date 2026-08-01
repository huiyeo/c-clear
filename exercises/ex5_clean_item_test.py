# -*- coding: utf-8 -*-
"""练习 5 的测试：验证你的 clean_item 实现。"""

import importlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("EX_SOURCE", HERE))
ex5 = importlib.import_module("ex5_clean_item")
clean_item = ex5.clean_item


def _make_item(kind, paths):
    return {"id": "test", "name": "测试项", "kind": kind, "paths": lambda: paths}


class TestCleanItem(unittest.TestCase):
    def test_missing_paths_is_safe(self):
        # 找不到路径：不报错，返回空结果 + 提示
        result = clean_item(_make_item("folder", []))
        self.assertEqual(result["freed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertTrue(any("未找到" in m for m in result["messages"]))

    def test_files_kind(self):
        # kind=files：删掉单文件，freed 记大小
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 50)
            path = f.name
        result = clean_item(_make_item("files", [path]))
        self.assertEqual(result["freed"], 50)
        self.assertEqual(result["failed"], 0)
        self.assertFalse(os.path.exists(path))

    def test_folder_kind(self):
        # kind=folder：删内容留目录
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.txt"), "wb") as f:
                f.write(b"a" * 80)
            result = clean_item(_make_item("folder", [d]))
            self.assertEqual(result["freed"], 80)
            self.assertEqual(result["failed"], 0)
            self.assertTrue(os.path.isdir(d))
            self.assertEqual(os.listdir(d), [])

    def test_result_contains_expected_keys(self):
        with tempfile.TemporaryDirectory() as d:
            result = clean_item(_make_item("folder", [d]))
            for key in ("item_id", "item", "freed", "failed", "messages"):
                self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
