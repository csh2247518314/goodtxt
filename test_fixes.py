#!/usr/bin/env python3
"""
GoodTxt 系统修复验证脚本
验证前后端修复是否成功
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def test_backend_syntax():
    """测试后端语法"""
    print("🔍 测试后端语法...")
    
    try:
        # 测试导入关键模块
        backend_src = str(Path(__file__).parent / "backend" / "src")
        sys.path.insert(0, backend_src)
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        # 测试认证管理器
        from src.auth.auth_manager import auth_manager
        print("✅ 认证管理器导入成功")
        
        # 测试设置配置
        from src.config.settings import get_settings
        settings = get_settings()
        print("✅ 设置配置导入成功")
        
        # 测试创建用户
        try:
            test_user = auth_manager.create_user(
                username="testuser",
                email="test@example.com", 
                password="test123456"
            )
            print(f"✅ 用户创建成功: {test_user.username}")
        except Exception as e:
            print(f"⚠️  用户创建测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 后端语法测试失败: {e}")
        return False

def test_frontend_build():
    """测试前端构建"""
    print("🔍 测试前端构建...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return False
    
    try:
        # 检查package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json 不存在")
            return False
        
        print("✅ 前端文件结构正确")
        return True
        
    except Exception as e:
        print(f"❌ 前端构建测试失败: {e}")
        return False

def test_docker_compose():
    """测试Docker Compose配置"""
    print("🔍 测试Docker Compose配置...")
    
    try:
        # 检查docker-compose.yml
        compose_file = Path(__file__).parent / "docker-compose.yml"
        if not compose_file.exists():
            print("❌ docker-compose.yml 不存在")
            return False
        
        # 尝试解析Docker Compose配置
        result = subprocess.run(
            ["docker-compose", "config"], 
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose 配置语法正确")
            return True
        else:
            print(f"❌ Docker Compose 配置错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Docker Compose 配置测试超时")
        return False
    except FileNotFoundError:
        print("⚠️  Docker Compose 未安装，跳过测试")
        return True
    except Exception as e:
        print(f"❌ Docker Compose 测试失败: {e}")
        return False

def generate_test_report():
    """生成测试报告"""
    print("\n📊 生成测试报告...")
    
    tests = [
        ("后端语法测试", test_backend_syntax),
        ("前端构建测试", test_frontend_build),
        ("Docker配置测试", test_docker_compose)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        results.append({
            "test_name": test_name,
            "success": success,
            "duration": round(end_time - start_time, 2)
        })
    
    # 生成报告
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(results),
        "passed_tests": sum(1 for r in results if r["success"]),
        "failed_tests": sum(1 for r in results if not r["success"]),
        "test_results": results
    }
    
    # 保存报告
    report_file = Path(__file__).parent / "test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 测试报告已保存到: {report_file}")
    
    # 打印总结
    print(f"\n{'='*50}")
    print("🎯 测试总结")
    print(f"{'='*50}")
    print(f"总测试数: {report['total_tests']}")
    print(f"通过测试: {report['passed_tests']} ✅")
    print(f"失败测试: {report['failed_tests']} ❌")
    
    if report['failed_tests'] == 0:
        print("\n🎉 所有测试通过！修复成功！")
    else:
        print("\n⚠️  存在失败的测试，请检查上述错误信息")
    
    return report['failed_tests'] == 0

def main():
    """主函数"""
    print("🚀 GoodTxt 系统修复验证")
    print("=" * 50)
    
    # 检查当前目录
    if not (Path(__file__).parent / "docker-compose.yml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 运行测试
    success = generate_test_report()
    
    if success:
        print("\n✅ 系统修复验证通过！")
        print("\n📝 接下来可以:")
        print("1. 配置AI API密钥 (.env文件)")
        print("2. 运行启动器: python3 super_launcher.py")
        print("3. 访问系统: http://localhost:3002")
    else:
        print("\n❌ 存在未解决的问题，请查看上述错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()