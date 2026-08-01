# -*- coding: utf-8 -*-
"""
cleaner.py —— C 盘清理的核心逻辑
==================================
本文件只负责"扫描、算大小、删除"，完全不涉及界面。

为什么要把逻辑和界面分开？（这是编程里很重要的习惯）
  1. 逻辑可以单独测试（见 tests/test_cleaner.py），不用打开窗口就能验证对不对
  2. 以后想换界面（命令行版、网页版）或加功能，都不用动这份逻辑
  3. 逻辑文件在 Linux / Windows 上都能跑，方便在你现在的开发环境里练习
"""

import ctypes
import glob
import os
import shutil
import stat
import sys
from ctypes import wintypes

# ---------------------------------------------------------------------------
# 一、平台判断
# ---------------------------------------------------------------------------

def is_windows():
    """当前是否 Windows 系统。sys.platform 在 Windows 上是 'win32'。"""
    return sys.platform == "win32"


# ---------------------------------------------------------------------------
# 二、小工具：路径与环境变量
# ---------------------------------------------------------------------------

def env_sub(var, *parts):
    """取环境变量 var 下的子路径。
    例如 env_sub("TEMP") 在 Windows 上可能得到 C:\\Users\\你\\AppData\\Local\\Temp。
    环境变量不存在时返回 None（调用方自己处理）。
    """
    base = os.environ.get(var)
    if not base:
        return None
    return os.path.join(base, *parts)


def format_bytes(n):
    """把字节数格式化成人话，例如 1572864 -> 1.5 MB。
    这就是一个典型的"循环 + 条件"逻辑练习。
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# ---------------------------------------------------------------------------
# 三、回收站：通过 Windows 系统 API 操作（ctypes 调用 shell32.dll）
# ---------------------------------------------------------------------------
# 说明：回收站不能像普通文件夹那样直接删，否则会破坏系统对它的管理。
# Windows 提供了专门的 API，我们用 Python 的 ctypes 去调用它。

class SHQUERYRBINFO(ctypes.Structure):
    """SHQueryRecycleBinW 需要的结构体，用来接收回收站的统计信息。"""
    _fields_ = [
        ("cbSize", wintypes.DWORD),      # 结构体自身大小（API 要求先填好）
        ("i64Size", ctypes.c_int64),     # 回收站占用字节数
        ("i64NumItems", ctypes.c_int64), # 回收站里的项目数
    ]


def query_recycle_bin_size():
    """查询回收站占用多少字节；非 Windows 环境返回 0。"""
    if not is_windows():
        return 0
    try:
        info = SHQUERYRBINFO()
        info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
        # 第一个参数传 None 表示查询所有驱动器；返回 0 表示成功（S_OK）
        result = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
        if result == 0:
            return int(info.i64Size)
    except Exception:
        pass
    return 0


def empty_recycle_bin():
    """清空回收站。返回 (是否成功, 提示文字)。"""
    if not is_windows():
        return False, "回收站功能仅支持 Windows"
    try:
        # 三个标志位：0x0001 不弹确认框 / 0x0002 不显示进度条 / 0x0004 不播放声音
        flags = 0x0001 | 0x0002 | 0x0004
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        if result == 0:
            return True, "回收站已清空"
        return False, f"清空回收站失败（错误码 {result}）"
    except Exception as e:
        return False, f"清空回收站出错：{e}"


# ---------------------------------------------------------------------------
# 四、定位各种"垃圾"在哪里（每个函数返回路径列表）
# ---------------------------------------------------------------------------
# 注意：这些函数用 glob 通配符匹配，是因为 Chrome/Edge 的缓存目录
# 可能因为用户/版本不同而有多个，写死一个路径会漏。

def path_list_user_temp():
    """用户临时文件：%TEMP% 目录下的内容。"""
    p = env_sub("TEMP")
    return [p] if p else []


def path_list_system_temp():
    """系统临时文件：C:\\Windows\\Temp 下的内容。"""
    p = env_sub("SystemRoot", "Temp")
    return [p] if p else []


def path_list_chrome_cache():
    """Chrome 缓存目录（所有 profile 的 Cache 文件夹）。"""
    base = env_sub("LOCALAPPDATA", "Google", "Chrome", "User Data")
    if not base:
        return []
    return sorted(glob.glob(os.path.join(base, "*", "Cache")))


def path_list_edge_cache():
    """Edge 缓存目录（Edge 和 Chrome 是同内核，位置类似）。"""
    base = env_sub("LOCALAPPDATA", "Microsoft", "Edge", "User Data")
    if not base:
        return []
    return sorted(glob.glob(os.path.join(base, "*", "Cache")))


def path_list_update_cache():
    """Windows 更新缓存：C:\\Windows\\SoftwareDistribution\\Download。"""
    p = env_sub("SystemRoot", "SoftwareDistribution", "Download")
    return [p] if p else []


def path_list_thumbcache():
    """缩略图缓存：Explorer 文件夹里的 thumbcache_*.db 文件。"""
    folder = env_sub("LOCALAPPDATA", "Microsoft", "Windows", "Explorer")
    if not folder:
        return []
    return sorted(glob.glob(os.path.join(folder, "thumbcache_*.db")))


def path_list_icon_cache():
    """图标缓存：和缩略图缓存同目录的 iconcache_*.db 文件。"""
    folder = env_sub("LOCALAPPDATA", "Microsoft", "Windows", "Explorer")
    if not folder:
        return []
    return sorted(glob.glob(os.path.join(folder, "iconcache_*.db")))


def path_list_delivery_opt():
    """更新分发缓存：Windows 更新下载的优化分发文件。"""
    p = env_sub("SystemRoot", "SoftwareDistribution", "DeliveryOptimization")
    return [p] if p else []


def path_list_wer():
    """Windows 错误报告（WER）：程序崩溃留下的记录。
    注意有两个位置：系统级（ProgramData）和用户级（LocalAppData）。"""
    paths = []
    sys_wer = env_sub("ProgramData", "Microsoft", "Windows", "WER")
    if sys_wer:
        paths.append(sys_wer)
    user_wer = env_sub("LOCALAPPDATA", "Microsoft", "Windows", "WER")
    if user_wer:
        paths.append(user_wer)
    return paths


def path_list_dx_shader():
    """DirectX 着色器缓存：游戏/图形程序编译的着色器缓存。"""
    p = env_sub("LOCALAPPDATA", "D3DSCache")
    return [p] if p else []


# ---------------------------------------------------------------------------
# 五、清理项清单（数据驱动：一份清单同时喂给扫描和清理，界面也读它）
# ---------------------------------------------------------------------------
# 每项是一个 dict，字段含义：
#   id    —— 唯一编号，界面用它来对应勾选框和大小标签
#   name  —— 显示给用户的名字
#   desc  —— 一行说明
#   kind  —— 处理方式：
#            "folder"     删除目录里的所有内容（保留目录本身，因为系统还引用它）
#            "files"      直接删除这些文件
#            "recycle_bin"走系统 API 清空回收站
#   paths —— 一个"函数"，调用后返回要处理的路径列表（延迟求值，扫描时才取真实路径）

CACHE_ITEMS = [
    {"id": "temp_user", "name": "用户临时文件", "desc": "%TEMP% 目录，软件运行留下的临时文件",
     "kind": "folder", "paths": path_list_user_temp},
    {"id": "temp_sys", "name": "系统临时文件", "desc": "C:\\Windows\\Temp，系统运行产生的临时文件",
     "kind": "folder", "paths": path_list_system_temp},
    {"id": "recycle", "name": "回收站", "desc": "清空回收站（通过系统 API 安全执行）",
     "kind": "recycle_bin", "paths": lambda: []},
    {"id": "chrome", "name": "Chrome 浏览器缓存", "desc": "网页图片/脚本的缓存，删了不影响书签",
     "kind": "folder", "paths": path_list_chrome_cache},
    {"id": "edge", "name": "Edge 浏览器缓存", "desc": "网页图片/脚本的缓存，删了不影响书签",
     "kind": "folder", "paths": path_list_edge_cache},
    {"id": "update", "name": "Windows 更新缓存", "desc": "已下载的更新安装包，可安全删除",
     "kind": "folder", "paths": path_list_update_cache},
    {"id": "thumb", "name": "缩略图缓存", "desc": "图片/视频预览图缓存，删了会重新生成",
     "kind": "files", "paths": path_list_thumbcache},
    {"id": "icon", "name": "图标缓存", "desc": "文件/程序图标缓存，删了会自动重建",
     "kind": "files", "paths": path_list_icon_cache},
    {"id": "delivery", "name": "更新分发缓存", "desc": "Windows 更新下载的优化分发文件",
     "kind": "folder", "paths": path_list_delivery_opt},
    {"id": "wer", "name": "错误报告", "desc": "程序崩溃记录（WER），可安全删除",
     "kind": "folder", "paths": path_list_wer},
    {"id": "dx", "name": "DirectX 着色器缓存", "desc": "游戏/图形程序的着色器编译缓存",
     "kind": "folder", "paths": path_list_dx_shader},
]


# ---------------------------------------------------------------------------
# 六、扫描：统计大小
# ---------------------------------------------------------------------------

def scan_path(path):
    """统计一个文件或目录占多少字节；不存在返回 0。
    用 os.walk 递归遍历目录，这是文件操作的经典写法。
    单个文件读不到（被占用/无权限）就跳过，不影响整体结果。
    """
    if not os.path.exists(path):
        return 0
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            fp = os.path.join(root, name)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def scan_item(item):
    """扫描一个清理项，返回它当前占用的字节数。"""
    if item["kind"] == "recycle_bin":
        return query_recycle_bin_size()
    total = 0
    for p in item["paths"]():
        total += scan_path(p)
    return total


def scan_all():
    """批量扫描所有清理项。
    返回 (每项大小 dict, 总字节数)——界面用它一次算出"总计可释放"。
    """
    sizes = {}
    total = 0
    for item in CACHE_ITEMS:
        size = scan_item(item)
        sizes[item["id"]] = size
        total += size
    return sizes, total


# ---------------------------------------------------------------------------
# 七、删除：尽力删除
# ---------------------------------------------------------------------------

def _rmtree_force(path):
    """递归删除整个目录；遇到只读文件先去掉只读属性再重试。"""
    def _onerror(func, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)  # S_IWRITE = 允许写入（在 Windows 上即去掉"只读"）
            func(p)                     # 重试刚才失败的操作
        except OSError:
            pass
    try:
        shutil.rmtree(path, onerror=_onerror)
        return True
    except OSError:
        return False


def _delete_force(path):
    """尽力删除单个文件或目录。返回是否成功。
    - 目录：递归删掉整个目录
    - 文件：去只读后删除
    - 不存在：视为成功（没什么可删的）
    """
    if os.path.isdir(path):
        return _rmtree_force(path)
    if os.path.isfile(path):
        try:
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
            return True
        except OSError:
            return False
    return True


def clean_folder_contents(path, progress=None):
    """删除目录里的所有内容（保留目录本身）。
    返回 (释放字节数, 失败数量)。
    progress 是可选回调 progress(done, total, text)，用于界面显示进度。
    """
    freed, failed = 0, 0
    if not os.path.isdir(path):
        return freed, failed
    entries = [os.path.join(path, name) for name in os.listdir(path)]
    for i, entry in enumerate(entries):
        size = scan_path(entry)
        if _delete_force(entry):
            freed += size
        else:
            failed += 1
        if progress:
            progress(i + 1, len(entries), os.path.basename(entry))
    return freed, failed


def clean_item(item, progress=None):
    """清理一个条目，返回结果 dict：
    {"item_id", "item", "freed": 释放字节数, "failed": 失败数, "messages": [提示文字]}
    """
    result = {"item_id": item["id"], "item": item["name"],
              "freed": 0, "failed": 0, "messages": []}

    if item["kind"] == "recycle_bin":
        ok, msg = empty_recycle_bin()
        result["messages"].append(msg)
        result["failed"] = 0 if ok else 1
        return result

    paths = [p for p in item["paths"]() if p]
    if not paths:
        result["messages"].append("未找到目标路径，已跳过")
        return result

    for done, p in enumerate(paths, start=1):
        if item["kind"] == "files":
            size = scan_path(p)
            if _delete_force(p):
                result["freed"] += size
            else:
                result["failed"] += 1
        else:  # "folder"：删内容、留目录
            freed, failed = clean_folder_contents(p, progress)
            result["freed"] += freed
            result["failed"] += failed
        if progress:
            progress(done, len(paths), f"位置 {done}/{len(paths)}")

    result["messages"].append(
        "清理完成" if result["failed"] == 0
        else f"清理完成，但有 {result['failed']} 个文件被占用或无权删除")
    return result
