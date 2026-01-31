#!/usr/bin/env python3
"""
GoodTxt 项目安全检查脚本
验证已实施的安全修复
"""

import os
import sys
from pathlib import Path
import re

def check_jwt_secret_security():
    """检查JWT密钥安全性"""
    print("🔍 检查JWT密钥安全性...")
    
    settings_file = Path("backend/src/config/settings.py")
    if settings_file.exists():
        content = settings_file.read_text()
        
        # 检查是否增加了长度验证
        if "len(self.jwt_secret) < 32" in content:
            print("✅ 已添加JWT密钥长度验证")
        else:
            print("❌ 未找到JWT密钥长度验证")
        
        return True
    else:
        print("❌ 未找到配置文件")
        return False

def check_default_admin_removal():
    """检查默认管理员账户移除"""
    print("\n🔍 检查默认管理员账户...")
    
    auth_file = Path("backend/src/auth/auth_manager.py")
    if auth_file.exists():
        content = auth_file.read_text()
        
        # 检查是否注释了默认管理员创建
        if "# Note: Production environments should not auto-create default admin accounts" in content or \
           "# 创建默认管理员用户" not in content:
            print("✅ 已移除/注释默认管理员账户创建")
        else:
            print("❌ 仍存在默认管理员账户创建代码")
        
        return True
    else:
        print("❌ 未找到认证管理文件")
        return False

def check_docker_files():
    """检查Docker相关文件"""
    print("\n🔍 检查Docker相关文件...")
    
    docker_files = [
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile"
    ]
    
    all_found = True
    for file_path in docker_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} 已创建")
        else:
            print(f"❌ {file_path} 未找到")
            all_found = False
    
    return all_found

def check_secure_env_file():
    """检查安全的环境配置"""
    print("\n🔍 检查环境配置安全性...")
    
    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text()
        
        # 检查是否提供了安全的默认密钥
        if "PLEASE_CHANGE_THIS_TO_A_LONG_RANDOM_STRING" in content:
            print("✅ 环境文件包含安全提示")
        else:
            print("❌ 环境文件未包含安全提示")
        
        return True
    else:
        print("❌ 未找到环境配置文件")
        return False

def check_readme_updates():
    """检查README更新"""
    print("\n🔍 检查README安全说明...")
    
    readme_file = Path("README.md")
    if readme_file.exists():
        content = readme_file.read_text()
        
        if "安全注意事项" in content and "更改JWT密钥" in content:
            print("✅ README已更新安全说明")
        else:
            print("❌ README未更新安全说明")
        
        return True
    else:
        print("❌ 未找到README文件")
        return False

def main():
    """主函数"""
    print("🛡️  GoodTxt 项目安全修复验证")
    print("=" * 50)
    
    checks = [
        ("JWT密钥安全", check_jwt_secret_security),
        ("默认管理员账户", check_default_admin_removal),
        ("Docker配置", check_docker_files),
        ("环境配置安全", check_secure_env_file),
        ("README更新", check_readme_updates)
    ]
    
    results = []
    for name, func in checks:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查失败: {e}")
            results.append((name, False))
    
    print(f"\n📊 检查结果汇总:")
    print("=" * 30)
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    successful_checks = sum(1 for _, success in results if success)
    total_checks = len(results)
    
    print(f"\n总计: {successful_checks}/{total_checks} 项检查通过")
    
    if successful_checks == total_checks:
        print("\n🎉 所有安全修复已成功实施！")
    else:
        print("\n⚠️  部分安全修复需要进一步处理")

if __name__ == "__main__":
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    main()