@echo off
:: GoodTxt 快速启动脚本 (Windows)
:: 自动检查环境并启动系统

echo.
echo 🚀 GoodTxt 快速启动
echo ==================

:: 设置执行权限（Windows不需要）
echo.

:: 检查Python
echo 🐍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    echo    请访问 https://python.org 下载安装Python 3.8+
    echo    安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python版本: %%i

:: 检查Docker
echo.
echo 🐳 检查Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装
    echo    请访问 https://docker.com/products/docker-desktop 下载Docker Desktop
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('docker --version 2^>^&1') do echo ✅ Docker版本: %%i

:: 检查Docker服务
echo.
echo 🔍 检查Docker服务...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker服务未运行
    echo    请启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker服务运行正常

:: 询问启动方式
echo.
echo 请选择启动方式：
echo 1. 智能启动器（推荐）
echo 2. 快速启动  
echo 3. 环境检查
echo 0. 退出
echo.
set /p choice=请输入选择 (0-3): 

if "%choice%"=="1" goto start_launcher
if "%choice%"=="2" goto start_quick
if "%choice%"=="3" goto start_check
if "%choice%"=="0" goto end
goto invalid

:start_launcher
echo 🚀 启动智能启动器...
python3 launcher.py
goto end

:start_quick
echo ⚡ 快速启动...
python3 quick_start.py
goto end

:start_check
echo 🔍 运行环境检查...
python3 env_checker.py
goto end

:invalid
echo ❌ 无效选择
goto end

:end
pause