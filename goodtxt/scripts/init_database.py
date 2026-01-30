#!/usr/bin/env python3
"""
数据库初始化脚本
用于初始化GoodTxt系统的数据库结构
"""

import sys
import os
from pathlib import Path

# 添加后端路径到Python路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database.init_db import init_database
from database.db_manager import user_db, project_db, chapter_db
from src.auth.auth_manager import UserRole

def main():
    """主函数"""
    print("🚀 GoodTxt 数据库初始化工具")
    print("=" * 50)
    
    # 1. 初始化数据库结构
    print("\n📊 步骤 1: 初始化数据库结构")
    success = init_database()
    if not success:
        print("❌ 数据库结构初始化失败")
        return False
    
    # 2. 创建默认管理员用户
    print("\n👤 步骤 2: 创建默认管理员用户")
    try:
        # 检查管理员用户是否已存在
        admin_user = user_db.get_user_by_username("admin")
        if admin_user:
            print("✅ 默认管理员用户已存在")
        else:
            # 创建管理员用户
            admin_data = {
                'username': 'admin',
                'email': 'admin@goodtxt.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LEvI5hwv4w6w2J5y',  # admin123456
                'role': UserRole.ADMIN.value,
                'api_key': 'gk_admin_default_key_123456789',
                'settings': {"theme": "dark", "language": "zh-CN"}
            }
            
            user_id = user_db.create_user(admin_data)
            print(f"✅ 默认管理员用户创建成功 (ID: {user_id})")
            print("   用户名: admin")
            print("   密码: admin123456")
    except Exception as e:
        print(f"⚠️  创建管理员用户时出错: {e}")
    
    # 3. 测试数据库连接
    print("\n🔍 步骤 3: 测试数据库连接")
    try:
        users = user_db.get_all_users()
        print(f"✅ 数据库连接正常，当前用户数量: {len(users)}")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False
    
    print("\n🎉 数据库初始化完成！")
    print("\n📝 后续步骤:")
    print("1. 启动后端服务: docker-compose up -d")
    print("2. 启动前端服务: cd frontend && npm run dev")
    print("3. 访问应用: http://localhost:3000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
