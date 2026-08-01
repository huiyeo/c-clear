# -*- coding: utf-8 -*-
"""
tests/test_cleaner.py —— 核心逻辑测试
======================================
用 Python 自带的 unittest 写测试，不依赖 Windows、不依赖界面。

运行方式（在项目目录下）：
    python3 -m unittest tests.test_cleaner -v
或直接跑本文件：
    python3 tests/test_cleaner.py

"先写测试、再验证逻辑"是很好的学习习惯：
改代码后跑一遍测试，就知道有没有改坏。
"""

import os
import sys
import tempfile
import unittest

# 把项目根目录加进导入路径，保证能 import cleaner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cleaner import (CACHE_ITEMS, _delete_force, clean_folder_contents,
                     clean_item, format_bytes, scan_all, scan_path)


class TestFormatBytes(unittest.TestCase):
    """format_bytes 的边界测试。"""

    def test_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(1023), "1023 B")

    def test_kb(self):
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1536), "1.5 KB")

    def test_mb(self):
        self.assertEqual(format_bytes(1572864), "1.5 MB")


class TestScanPath(unittest.TestCase):
    """扫描大小的测试。"""

    def test_missing_path_is_zero(self):
        self.assertEqual(scan_path(os.path.join(tempfile.gettempdir(), "不存在的_xyz")), 0)

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


class TestDelete(unittest.TestCase):
    """删除逻辑的测试。"""

    def test_delete_force_missing_returns_true(self):
        # 不存在的文件：视为成功（没什么可删）
        self.assertTrue(_delete_force(os.path.join(tempfile.gettempdir(), "不存在的_xyz")))

    def test_delete_force_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"data")
            path = f.name
        self.assertTrue(_delete_force(path))
        self.assertFalse(os.path.exists(path))

    def test_delete_force_readonly_file(self):
        # 只读文件也能删（_delete_force 会先去掉只读属性）
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"data")
            path = f.name
        try:
            os.chmod(path, 0o444)  # 只读
            self.assertTrue(_delete_force(path))
            self.assertFalse(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_clean_folder_contents_keeps_folder(self):
        # 清理目录内容后：目录还在，里面空了
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
            self.assertTrue(os.path.isdir(d))
            self.assertEqual(os.listdir(d), [])  # 目录还在，但已清空


class TestScanAll(unittest.TestCase):
    """scan_all 批量扫描的测试（用 mock 隔离真实文件系统）。"""

    def test_returns_every_item_and_total(self):
        import cleaner
        # 伪造每个清理项的扫描结果：第 i 项 = 100 + i 字节
        fake_sizes = {item["id"]: 100 + i
                      for i, item in enumerate(CACHE_ITEMS)}
        original = cleaner.scan_item
        cleaner.scan_item = lambda item: fake_sizes[item["id"]]
        try:
            sizes, total = scan_all()
        finally:
            cleaner.scan_item = original  # 用完恢复，不影响其他测试

        # 每项都有结果，且 id 集合完整
        self.assertEqual(set(sizes), {item["id"] for item in CACHE_ITEMS})
        # 总计 = 各项之和
        self.assertEqual(total, sum(fake_sizes.values()))
        self.assertEqual(sizes, fake_sizes)

    def test_empty_total_when_no_targets(self):
        # 在非 Windows 环境（没有那些缓存目录）时，总计为 0 且不报错
        sizes, total = scan_all()
        self.assertEqual(total, sum(sizes.values()))
        self.assertGreaterEqual(total, 0)


class TestItems(unittest.TestCase):
    """清理项清单本身的测试（平台无关部分）。"""

    def test_items_are_defined(self):
        self.assertTrue(len(CACHE_ITEMS) > 0)
        ids = [item["id"] for item in CACHE_ITEMS]
        self.assertEqual(len(ids), len(set(ids)), "id 必须唯一")
        for item in CACHE_ITEMS:
            self.assertIn("name", item)
            self.assertIn("desc", item)
            self.assertIn(item["kind"], ("folder", "files", "recycle_bin"))

    def test_paths_function_never_raises(self):
        # 无论 Windows 还是 Linux，取路径都不该抛异常（最多返回空列表）
        for item in CACHE_ITEMS:
            with self.subTest(item=item["id"]):
                paths = item["paths"]()
                self.assertIsInstance(paths, list)

    def test_clean_item_missing_paths_is_safe(self):
        # 在非 Windows / 找不到路径时，清理也不该崩
        fake = {"id": "x", "name": "x", "kind": "folder", "paths": lambda: []}
        result = clean_item(fake)
        self.assertEqual(result["freed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertTrue(result["messages"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
