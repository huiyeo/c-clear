@echo off
chcp 65001 >nul
REM ============================================================
REM  C-Clear 打包脚本 —— 在 Windows 上双击运行
REM
REM  1. 安装 PyInstaller（只需一次，之后可注释掉）
REM  2. 把 main.py 打包成单个 exe
REM  产物：dist\C-Clear.exe
REM ============================================================

echo [1/2] 检查并安装依赖 ...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo [2/2] 开始打包 ...
REM 参数说明（安全优先）：
REM   --onefile       打成单个 exe，方便拷贝给小白
REM   --noconsole     不弹黑色控制台窗口（纯 GUI）
REM   --uac-admin     exe 启动时自动申请"管理员权限"，清理更彻底
REM   --hidden-import send2trash   显式声明依赖，确保"删除进回收站"一定被打包
REM                                （不依赖 PyInstaller 自动分析，防止漏装）
REM   --exclude-module unittest    排除测试代码，减小体积、降低杀软误报概率
REM   --version-file  版本信息文件，让 exe 显示正式版本（降低误报/SmartScreen 拦截）
REM   --name C-Clear  生成的 exe 文件名
python -m PyInstaller --noconfirm --clean --onefile --noconsole --uac-admin ^
    --hidden-import send2trash ^
    --exclude-module unittest ^
    --exclude-module tests ^
    --version-file version.txt ^
    --name C-Clear main.py

REM 打包后自检：确认 exe 确实生成了
if exist dist\C-Clear.exe (
    echo.
    echo [自检] dist\C-Clear.exe 已生成。
    echo.
) else (
    echo.
    echo [自检失败] 没有找到 dist\C-Clear.exe，打包可能出错！
    pause
    exit /b 1
)

echo.
echo 打包完成！exe 在 dist\C-Clear.exe
echo 把它拷给朋友就能直接双击用了。
pause
