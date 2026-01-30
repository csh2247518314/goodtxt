#!/usr/bin/env python3
"""
项目部署验证脚本
验证项目是否可以正常启动
"""

import os
import sys
import subprocess
from pathlib import Path

def check_docker():
    """检查Docker是否可用"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker 可用")
            return True
        else:
            print("❌ Docker 不可用")
            return False
    except FileNotFoundError:
        print("❌ Docker 未安装")
        return False

def check_compose():
    """检查Docker Compose是否可用"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose 可用")
            return True
        else:
            print("❌ Docker Compose 不可用")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose 未安装")
        return False

def check_env_file():
    """检查环境配置文件"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env 文件存在")
        return True
    elif env_example.exists():
        print("⚠️ .env 文件不存在，但 .env.example 存在")
        print("💡 请运行: cp .env.example .env")
        return False
    else:
        print("❌ .env 和 .env.example 都不存在")
        return False

def check_project_structure():
    """检查项目结构"""
    required_files = [
        'docker-compose.yml',
        'backend/main.py',
        'backend/src/api/main.py',
        'backend/requirements.txt',
        'frontend/package.json',
        'frontend/index.html',
        'scripts/setup-database.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺失文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ 项目结构完整")
        return True

def main():
    """主函数"""
    print("🚀 GoodTxt 多AI协同小说生成系统 - 部署验证")
    print("="*50)
    
    checks = [
        ("Docker", check_docker),
        ("Docker Compose", check_compose),
        ("项目结构", check_project_structure),
        ("环境配置", check_env_file)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 检查 {name}:")
        result = check_func()
        results.append(result)
    
    # 总结
    print("\n" + "="*50)
    print("📋 验证总结")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    print(f"通过检查: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有检查通过！")
        print("\n下一步:")
        print("1. 编辑 .env 文件，配置AI API密钥")
        print("2. 运行 python scripts/setup-database.py 初始化数据库")
        print("3. 运行 docker-compose up -d 启动服务")
        print("4. 访问 http://localhost:3002 开始使用")
        return 0
    else:
        print("⚠️ 部分检查未通过，请修复上述问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)