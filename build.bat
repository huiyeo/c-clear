@echo off
chcp 65001 >nul
REM ============================================================
REM  C-Clear 打包脚本 —— 在 Windows 上双击运行
REM
REM  1. 安装 PyInstaller（只需一次，之后可注释掉）
REM  2. 把 main.py 打包成单个 exe
REM  产物：dist\C-Clear.exe
REM ============================================================

echo [1/2] 检查并安装 PyInstaller ...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo [2/2] 开始打包 ...
REM --onefile     打成单个 exe，方便拷贝给小白
REM --noconsole   不弹黑色控制台窗口（纯 GUI）
REM --uac-admin   exe 启动时自动请求"管理员权限"，清理更彻底
REM --name C-Clear 生成的 exe 文件名
python -m PyInstaller --noconfirm --clean --onefile --noconsole --uac-admin --name C-Clear main.py

echo.
echo 打包完成！exe 在 dist\C-Clear.exe
echo 把它拷给朋友就能直接双击用了。
pause
