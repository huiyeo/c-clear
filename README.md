# C-Clear ｜ C 盘清理助手

一个给**不懂电脑的小白**用的 C 盘清理小工具：勾选 → 扫描 → 一键清理。
图形界面，纯 Python 标准库实现，无需联网、无需安装任何运行库。

**特性**：勾选式清理 ｜ 实时显示各项目占用大小 ｜ 进度条 + 日志 ｜ 自动请求管理员权限

---

## 一、给小白用户（怎么用）

1. 拿到 **`C-Clear.exe`**（由打包脚本生成），双击打开。
2. 勾选想清理的项目，点「扫 描」看看它们占了多大空间。
3. 点「一键清理」，等进度条跑完即可。

> ⚠️ 注意事项
> - 建议右键 →「以管理员身份运行」，否则部分系统文件删不掉。
> - 清理的是**缓存和临时文件**，不影响你的文档、照片、软件。
> - 浏览器缓存删了只是下次打开网页稍慢一点，书签、密码、历史记录都不受影响。

## 二、给开发者 / 学习者（这个项目能学到什么）

### 项目结构

```
c-clear/
├── main.py              # 界面层：tkinter GUI（窗口、按钮、进度条、日志）
├── cleaner.py           # 逻辑层：扫描大小、删除文件、清空回收站
├── tests/
│   └── test_cleaner.py  # 逻辑层的单元测试（unittest）
├── build.bat            # Windows 打包脚本（PyInstaller → exe）
├── requirements.txt     # 打包需要的依赖（运行时只用 Python 标准库）
└── README.md
```

**核心设计：界面与逻辑分离。** `cleaner.py` 里没有任何界面代码，`main.py` 只负责展示。好处是逻辑可以单独测试，将来换界面不用动逻辑。

### 在 Windows 上跑源码

```bat
python main.py
```

### 打包成 exe（给小白用）

```bat
build.bat
```

产物在 `dist\C-Clear.exe`，`--uac-admin` 让 exe 启动时自动申请管理员权限。

### 可以学到的东西

| 知识点 | 在哪儿 |
| --- | --- |
| 变量、函数、`if/else`、`for` 循环 | `cleaner.py` 里到处都是 |
| 列表/字典/`lambda`，数据驱动编程 | `CACHE_ITEMS` 一份清单同时驱动扫描、清理、界面 |
| `os.walk` 递归遍历目录 | `scan_path()` |
| 异常处理 `try/except` | 文件被占用、无权限时程序不崩 |
| 文件属性（只读）与强制删除 | `_delete_force()` |
| 用 `ctypes` 调用 Windows 系统 API | 清空回收站（`SHEmptyRecycleBinW`）|
| 多线程 + 消息队列 | `main.py` 后台线程 + `queue` + `root.after` 轮询，界面不卡死 |
| 单元测试 | `tests/test_cleaner.py`，改代码后跑一遍验证没改坏 |

### 跑测试（Linux / Windows 都行）

```bash
python3 -m unittest tests.test_cleaner -v
```

### 开发路线（如果还想继续）

- [ ] 每个清理项支持"展开看具体删了哪些文件"
- [ ] 清理前自动备份/可撤销
- [ ] 自定义扫描规则（用户自己添加文件夹）
- [ ] 显示预计可释放空间 vs 实际释放空间
- [ ] 加图标、加"开机自动提醒清理"

---

## 三、技术说明

- 运行时**零第三方依赖**：GUI 用 `tkinter`，全是 Python 标准库。
- 回收站不直接删文件，而是通过 `ctypes` 调用 `shell32.dll` 的
  `SHQueryRecycleBinW`（查大小）和 `SHEmptyRecycleBinW`（清空），更规范安全。
- 删除文件前先去掉只读属性，尽量"尽力而为"，删不掉的（被占用）会统计为失败并在日志里说明。
