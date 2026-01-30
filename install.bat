@echo off
setlocal enabledelayedexpansion
:: GoodTxt Windows自动安装脚本
:: 零配置安装：自动安装Git、Python、Docker，然后启动GoodTxt

:: 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "NC=[0m"

:: 标题
echo.
echo %WHITE%╔══════════════════════════════════════════════════════════════╗%NC%
echo %WHITE%║                   🚀 GoodTxt 自动安装器 🚀                ║%NC%
echo %WHITE%║               零配置安装：Git + Python + Docker          ║%NC%
echo %WHITE%╚══════════════════════════════════════════════════════════════╝%NC%
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%⚠️  需要管理员权限安装软件%NC%
    echo %YELLOW%请右键点击此文件，选择"以管理员身份运行"%NC%
    pause
    exit /b 1
)

echo %BLUE%ℹ️  开始自动安装GoodTxt...%NC%
echo.

:: 检查Git
echo %PURPLE%🚀 检查Git...%NC%
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ Git已安装: %NC%
    git --version
) else (
    echo %YELLOW%⚠️  Git未安装，开始安装...%NC%
    echo %BLUE%ℹ️  请访问 https://git-scm.com/download/win 下载Git%NC%
    echo %BLUE%ℹ️  下载后请重新运行此脚本%NC%
    pause
    exit /b 1
)

:: 检查Python
echo.
echo %PURPLE%🚀 检查Python...%NC%
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ Python已安装: %NC%
    python --version
    set "PYTHON_CMD=python"
) else (
    echo %YELLOW%⚠️  Python未安装，开始安装...%NC%
    echo %BLUE%ℹ️  请访问 https://python.org 下载Python 3.8+%NC%
    echo %BLUE%ℹ️  下载时请勾选 "Add Python to PATH"%NC%
    echo %BLUE%ℹ️  安装后请重新运行此脚本%NC%
    pause
    exit /b 1
)

:: 检查Docker
echo.
echo %PURPLE%🚀 检查Docker...%NC%
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ Docker已安装: %NC%
    docker --version
    
    :: 检查Docker服务
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo %YELLOW%⚠️  Docker服务未运行%NC%
        echo %BLUE%ℹ️  请启动Docker Desktop%NC%
        pause
    )
) else (
    echo %YELLOW%⚠️  Docker未安装，开始安装...%NC%
    echo %BLUE%ℹ️  请访问 https://docker.com/products/docker-desktop 下载Docker Desktop%NC%
    echo %BLUE%ℹ️  安装后请重新运行此脚本%NC%
    pause
    exit /b 1
)

:: 创建工作目录
echo.
echo %PURPLE%🚀 创建工作目录...%NC%
if exist "goodtxt" (
    echo %YELLOW%⚠️  goodtxt目录已存在%NC%
    cd goodtxt
) else (
    echo %BLUE%ℹ️  克隆GoodTxt仓库...%NC%
    git clone https://github.com/csh2247518314/goodtxt.git
    cd goodtxt
    echo %GREEN%✅ 仓库克隆完成%NC%
)

:: 询问启动方式
echo.
echo %PURPLE%🚀 准备启动GoodTxt%NC%
echo.
echo %YELLOW%请选择启动方式:%NC%
echo 1. 智能启动器（推荐）
echo 2. 快速启动
echo 3. 环境检查
echo 4. 仅克隆，跳过启动
echo.
set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" goto start_launcher
if "%choice%"=="2" goto start_quick
if "%choice%"=="3" goto start_check
if "%choice%"=="4" goto skip_start
goto show_usage

:start_launcher
echo %BLUE%ℹ️  启动智能启动器...%NC%
python3 launcher.py
goto show_usage

:start_quick
echo %BLUE%ℹ️  快速启动...%NC%
python3 quick_start.py
goto show_usage

:start_check
echo %BLUE%ℹ️  运行环境检查...%NC%
python3 env_checker.py
goto show_usage

:skip_start
echo %GREEN%✅ 仓库克隆完成，跳过启动%NC%
echo %BLUE%ℹ️  您可以稍后手动运行: python3 launcher.py%NC%
goto show_usage

:show_usage
echo.
echo %CYAN%================================%NC%
echo %WHITE%GoodTxt 安装完成！%NC%
echo %CYAN%================================%NC%
echo.
echo %YELLOW%启动方式:%NC%
echo %GREEN%  python3 launcher.py%NC%
echo %GREEN%  双击 start.bat%NC%
echo.
echo %YELLOW%访问地址:%NC%
echo %GREEN%  前端: http://localhost:3000%NC%
echo %GREEN%  后端: http://localhost:8000%NC%
echo %GREEN%  文档: http://localhost:8000/docs%NC%
echo.
echo %CYAN%================================%NC%
pause