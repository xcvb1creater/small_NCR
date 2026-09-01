@echo off
REM 双击本文件运行小规模复现（窗口不会闪退）
cd /d "%~dp0.."
echo 项目目录: %CD%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_tiny_demo.ps1"
echo.
echo ========================================
echo 运行结束。输出目录: NCR\output\tiny_demo\
echo ========================================
pause
