#!/usr/bin/env python3
"""
GoodTxt 多AI协同小说生成系统 - 超级启动器
整合环境检查、自动修复、服务监控、快速启动的智能系统
"""

import os
import sys
import time
import json
import requests
import subprocess
import platform
import socket
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 尝试导入psutil，如果失败则设为None
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False


class Color:
    """终端颜色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    MAGENTA = '\033[95m'  # Alias for PURPLE
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SuperLauncher:
    """超级启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        self.services = {
            "backend": {
                "name": "后端API",
                "url": "http://localhost:8000/health",
                "check_url": "http://localhost:8000/agents",
                "status": "unknown",
                "last_check": None,
                "response_time": None,
                "error_count": 0
            },
            "frontend": {
                "name": "前端界面", 
                "url": "http://localhost:3002",
                "check_url": None,
                "status": "unknown",
                "last_check": None,
                "response_time": None,
                "error_count": 0
            }
        }
    
    def print_banner(self):
        """打印横幅"""
        print(f"{Color.BOLD}{Color.CYAN}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🚀 GoodTxt 超级启动器 🚀                  ║")
        print("║          多AI协同小说生成系统智能管理                   ║")
        print("║                    一站式解决方案                         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Color.RESET}")
    
    def print_header(self):
        """打印标题"""
        print(f"{Color.BOLD}{Color.CYAN}")
        print("=" * 60)
        print("🚀 GoodTxt 多AI协同小说生成系统 - 智能管理")
        print("=" * 60)
        print(f"{Color.RESET}")
    
    def print_step(self, step_num: int, total: int, title: str):
        """打印步骤"""
        print(f"{Color.BLUE}[{step_num}/{total}] {Color.BOLD}{title}{Color.RESET}")
    
    def print_status(self, message: str, status: str = "info"):
        """打印状态信息"""
        if status == "success":
            print(f"  {Color.GREEN}✅ {message}{Color.RESET}")
        elif status == "warning":
            print(f"  {Color.YELLOW}⚠️  {message}{Color.RESET}")
        elif status == "error":
            print(f"  {Color.RED}❌ {message}{Color.RESET}")
        elif status == "info":
            print(f"  {Color.CYAN}ℹ️  {message}{Color.RESET}")
        elif status == "fix":
            print(f"  {Color.PURPLE}🔧 {message}{Color.RESET}")
    
    def run_command(self, command: str, capture_output: bool = True) -> Tuple[bool, str, str]:
        """执行命令"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令超时"
        except Exception as e:
            return False, "", str(e)
    
    def get_local_ip(self):
        """获取本地IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def get_public_ip(self):
        """获取公网IP地址"""
        try:
            services = [
                "https://api.ipify.org",
                "https://ipinfo.io/ip",
                "https://icanhazip.com",
                "https://ident.me"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=3)
                    if response.status_code == 200:
                        public_ip = response.text.strip()
                        if public_ip and len(public_ip.split('.')) == 4:
                            return public_ip
                except:
                    continue
            
            return None
        except:
            return None
    
    def detect_environment(self):
        """检测当前环境类型"""
        local_ip = self.get_local_ip()
        public_ip = self.get_public_ip()
        
        is_server = False
        reason = ""
        
        if public_ip and local_ip != "127.0.0.1":
            if not local_ip.startswith("192.168.") and not local_ip.startswith("10.") and not local_ip.startswith("172."):
                is_server = True
                reason = "检测到公网IP"
            elif public_ip != local_ip:
                is_server = True
                reason = "公网IP与内网IP不同"
        
        return {
            "local_ip": local_ip,
            "public_ip": public_ip,
            "is_server": is_server,
            "reason": reason,
            "frontend_url": f"http://{public_ip if is_server else 'localhost'}:3002",
            "backend_url": f"http://{public_ip if is_server else 'localhost'}:8000",
            "docs_url": f"http://{public_ip if is_server else 'localhost'}:8000/docs"
        }
    
    def check_docker(self) -> bool:
        """检查Docker环境"""
        self.print_step(1, 8, "检查Docker环境")
        
        # 检查Docker是否安装
        success, stdout, stderr = self.run_command("docker --version")
        if not success:
            self.issues.append("Docker未安装")
            self.print_status("Docker未安装", "error")
            return False
        
        self.print_status(f"Docker版本: {stdout.strip()}", "success")
        
        # 检查Docker是否运行
        success, _, _ = self.run_command("docker info")
        if not success:
            self.issues.append("Docker服务未运行")
            self.print_status("Docker服务未运行", "error")
            return False
        
        self.print_status("Docker服务正常运行", "success")
        
        # 检查docker-compose
        success, stdout, stderr = self.run_command("docker-compose --version")
        if not success:
            success, stdout, stderr = self.run_command("docker compose --version")
            if not success:
                self.warnings.append("docker-compose未安装")
                self.print_status("docker-compose未安装，将使用Docker Compose插件", "warning")
            else:
                self.print_status(f"Docker Compose版本: {stdout.strip()}", "success")
        else:
            self.print_status(f"docker-compose版本: {stdout.strip()}", "success")
        
        return True
    
    def check_system_resources(self) -> bool:
        """检查系统资源"""
        self.print_step(2, 8, "检查系统资源")
        
        if not HAS_PSUTIL:
            self.print_status("psutil未安装，跳过详细系统资源检查", "warning")
            return True
        
        # 检查内存
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            total_gb = memory.total / (1024**3)
            
            self.print_status(f"总内存: {total_gb:.1f}GB，可用: {available_gb:.1f}GB", "info")
            
            if available_gb < 2:
                self.warnings.append("可用内存少于2GB")
                self.print_status("可用内存少于2GB，可能影响性能", "warning")
            elif available_gb > 4:
                self.print_status("内存充足", "success")
        except Exception as e:
            self.print_status(f"内存检查失败: {e}", "warning")
        
        # 检查磁盘空间
        try:
            disk = psutil.disk_usage('.')
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            
            self.print_status(f"磁盘空间: 总计{total_gb:.1f}GB，可用{free_gb:.1f}GB", "info")
            
            if free_gb < 5:
                self.warnings.append("可用磁盘空间少于5GB")
                self.print_status("可用磁盘空间少于5GB，可能影响Docker镜像下载", "warning")
            elif free_gb > 10:
                self.print_status("磁盘空间充足", "success")
        except Exception as e:
            self.print_status(f"磁盘空间检查失败: {e}", "warning")
        
        return True
    
    def check_ports(self) -> bool:
        """检查端口占用"""
        self.print_step(3, 8, "检查端口占用")
        
        required_ports = [8000, 3002, 6379, 8001]
        available_ports = []
        
        for port in required_ports:
            if self.is_port_available(port):
                available_ports.append(port)
                self.print_status(f"端口{port}可用", "success")
            else:
                self.warnings.append(f"端口{port}被占用")
                self.print_status(f"端口{port}被占用", "warning")
        
        return len(available_ports) == len(required_ports)
    
    def is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def check_project_files(self) -> bool:
        """检查项目文件"""
        self.print_step(4, 8, "检查项目文件")
        
        required_files = [
            "docker-compose.yml",
            "backend/Dockerfile",
            "frontend/Dockerfile",
            "backend/main.py",
            "frontend/package.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.print_status(f"文件存在: {file_path}", "success")
            else:
                missing_files.append(file_path)
                self.print_status(f"文件缺失: {file_path}", "error")
        
        if missing_files:
            self.issues.extend([f"缺失文件: {f}" for f in missing_files])
            return False
        
        return True
    
    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        self.print_step(5, 8, "检查目录结构")
        
        required_dirs = [
            "data",
            "data/database",
            "data/chroma", 
            "logs",
            "config",
            "config/nginx",
            "monitoring"
        ]
        
        created_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_path)
                    self.print_status(f"创建目录: {dir_path}", "fix")
                except Exception as e:
                    self.print_status(f"创建目录失败: {dir_path} - {e}", "error")
            else:
                self.print_status(f"目录存在: {dir_path}", "success")
        
        if created_dirs:
            self.fixes_applied.extend([f"创建目录: {d}" for d in created_dirs])
        
        return True
    
    def check_python_environment(self) -> bool:
        """检查Python环境"""
        self.print_step(6, 8, "检查Python环境")
        
        python_version = sys.version_info
        self.print_status(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}", "info")
        
        if python_version < (3, 8):
            self.warnings.append("Python版本过低，建议使用3.8+")
            self.print_status("Python版本过低，可能影响依赖安装", "warning")
        else:
            self.print_status("Python版本满足要求", "success")
        
        return True
    
    def test_docker_compose_syntax(self) -> bool:
        """测试Docker Compose语法"""
        self.print_step(7, 8, "验证Docker Compose配置")
        
        success, stdout, stderr = self.run_command("docker-compose config")
        if success:
            self.print_status("Docker Compose配置语法正确", "success")
        else:
            self.issues.append("Docker Compose配置语法错误")
            self.print_status("Docker Compose配置语法错误", "error")
            return False
        
        return True
    
    def run_environment_check(self) -> bool:
        """运行环境检查"""
        self.print_header()
        print(f"\n{Color.BOLD}{Color.YELLOW}🔍 环境检查和修复{Color.RESET}")
        print("=" * 50)
        
        checks = [
            ("Docker环境", self.check_docker),
            ("系统资源", self.check_system_resources), 
            ("端口检查", self.check_ports),
            ("项目文件", self.check_project_files),
            ("目录结构", self.check_directory_structure),
            ("Python环境", self.check_python_environment),
            ("Docker配置", self.test_docker_compose_syntax)
        ]
        
        success_count = 0
        for i, (name, check_func) in enumerate(checks, 1):
            try:
                if check_func():
                    success_count += 1
            except Exception as e:
                self.print_status(f"{name}检查失败: {e}", "error")
        
        return len(self.issues) == 0
    
    def start_services(self) -> bool:
        """启动服务"""
        print(f"\n{Color.BOLD}{Color.GREEN}🚀 启动服务{Color.RESET}")
        print("=" * 50)
        
        # 停止现有服务
        print("停止现有服务...")
        os.system("docker-compose down > /dev/null 2>&1")
        
        # 启动服务
        print("启动服务中...")
        result = os.system("docker-compose up -d")
        
        if result == 0:
            print(f"{Color.GREEN}✅ 服务启动成功！{Color.RESET}")
            return True
        else:
            print(f"{Color.RED}❌ 服务启动失败！{Color.RESET}")
            return False
    
    def wait_for_services(self, timeout: int = 120) -> bool:
        """等待服务启动"""
        print(f"\n{Color.BOLD}{Color.BLUE}⏳ 等待服务启动{Color.RESET}")
        print("=" * 50)
        
        print("正在等待服务启动...")
        
        # 获取环境信息
        env_info = self.detect_environment()
        backend_url = env_info["backend_url"]
        frontend_url = env_info["frontend_url"]
        
        start_time = time.time()
        backend_healthy = False
        frontend_healthy = False
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            print(f"\r等待中... {elapsed}s / {timeout}s", end="", flush=True)
            
            # 检查后端
            try:
                response = requests.get(backend_url, timeout=5)
                if response.status_code == 200:
                    backend_healthy = True
                    print(f"\n{Color.GREEN}✅ 后端服务已就绪！{Color.RESET}")
                    break
            except:
                pass
            
            time.sleep(3)
        
        print(f"\n")
        
        # 检查前端
        try:
            response = requests.get(frontend_url, timeout=5)
            if response.status_code == 200:
                frontend_healthy = True
                print(f"{Color.GREEN}✅ 前端服务已就绪！{Color.RESET}")
        except:
            print(f"{Color.YELLOW}⚠️  前端服务检查超时，可能仍在启动中{Color.RESET}")
        
        return backend_healthy
    
    def check_service(self, service_name: str) -> Dict:
        """检查单个服务状态"""
        service = self.services[service_name]
        start_time = time.time()
        
        try:
            response = requests.get(service["url"], timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                status = "healthy"
                service["error_count"] = 0
                
                # 检查具体内容
                if service_name == "backend" and service["check_url"]:
                    try:
                        agents_response = requests.get(service["check_url"], timeout=5)
                        if agents_response.status_code == 200:
                            agents_data = agents_response.json()
                            service["agent_count"] = agents_data.get("total_agents", 0)
                    except:
                        service["agent_count"] = "unknown"
            else:
                status = "unhealthy"
                service["error_count"] += 1
                
        except requests.exceptions.Timeout:
            status = "timeout"
            response_time = 10.0
            service["error_count"] += 1
        except requests.exceptions.ConnectionError:
            status = "connection_error"
            response_time = None
            service["error_count"] += 1
        except Exception as e:
            status = "error"
            response_time = None
            service["error_count"] += 1
        
        # 更新服务状态
        service["status"] = status
        service["last_check"] = datetime.now()
        service["response_time"] = response_time
        
        return service
    
    def verify_deployment(self) -> bool:
        """验证部署"""
        print(f"\n{Color.BOLD}{Color.PURPLE}🔍 验证部署{Color.RESET}")
        print("=" * 50)
        
        # 获取环境信息
        env_info = self.detect_environment()
        backend_url = env_info["backend_url"]
        frontend_url = env_info["frontend_url"]
        
        # 更新服务URL
        self.services["backend"]["url"] = backend_url
        self.services["frontend"]["url"] = frontend_url
        
        # 检查后端API
        try:
            response = requests.get(backend_url, timeout=10)
            if response.status_code == 200:
                agents_data = response.json()
                agent_count = agents_data.get("total_agents", 0)
                print(f"{Color.GREEN}✅ 后端API正常工作{Color.RESET}")
                print(f"{Color.CYAN}ℹ️  已配置AI代理数量: {agent_count}{Color.RESET}")
                
                if agent_count == 0:
                    print(f"{Color.YELLOW}💡 提示: 当前未配置AI API密钥，AI功能暂时不可用{Color.RESET}")
                    print(f"{Color.CYAN}   要启用AI功能，请编辑 docker-compose.yml 添加API密钥{Color.RESET}")
            else:
                print(f"{Color.RED}❌ 后端API返回错误: {response.status_code}{Color.RESET}")
                return False
        except Exception as e:
            print(f"{Color.RED}❌ 后端API连接失败: {e}{Color.RESET}")
            return False
        
        # 检查前端
        try:
            response = requests.get(frontend_url, timeout=10)
            if response.status_code == 200:
                print(f"{Color.GREEN}✅ 前端服务正常{Color.RESET}")
            else:
                print(f"{Color.YELLOW}⚠️  前端服务返回: {response.status_code}{Color.RESET}")
        except Exception as e:
            print(f"{Color.YELLOW}⚠️  前端服务检查失败: {e}{Color.RESET}")
        
        return True
    
    def print_success_summary(self):
        """打印成功总结"""
        print(f"\n{Color.BOLD}{Color.GREEN}🎉 部署成功！{Color.RESET}")
        print("=" * 50)
        
        # 获取环境信息
        env_info = self.detect_environment()
        
        print(f"{Color.CYAN}📱 访问地址:{Color.RESET}")
        print(f"   🌐 前端界面: {Color.BLUE}{env_info['frontend_url']}{Color.RESET}")
        print(f"   🔧 后端API: {Color.BLUE}{env_info['backend_url']}{Color.RESET}")
        print(f"   📚 API文档: {Color.BLUE}{env_info['docs_url']}{Color.RESET}")
        
        print(f"\n{Color.CYAN}📋 使用说明:{Color.RESET}")
        print(f"   1. 访问前端界面开始使用")
        print(f"   2. 创建小说项目")
        print(f"   3. 如果需要AI功能，请配置API密钥")
        
        print(f"\n{Color.CYAN}🔧 常用命令:{Color.RESET}")
        print(f"   停止服务: {Color.YELLOW}docker-compose down{Color.RESET}")
        print(f"   查看日志: {Color.YELLOW}docker-compose logs{Color.RESET}")
        print(f"   重启服务: {Color.YELLOW}docker-compose restart{Color.RESET}")
        print(f"   监控服务: {Color.YELLOW}python3 super_launcher.py --monitor{Color.RESET}")
        
        print(f"\n{Color.GREEN}✨ 享受您的AI小说创作之旅！{Color.RESET}")
    
    def run_quick_start(self):
        """快速启动"""
        print(f"{Color.CYAN}🚀 GoodTxt 快速启动...{Color.RESET}")
        print("=" * 40)
        
        # 检查Docker
        print("1. 检查Docker...")
        if subprocess.run(["docker", "--version"], capture_output=True).returncode != 0:
            print("❌ Docker未安装，请先运行安装脚本")
            return False
        
        print("✅ Docker环境正常")
        
        # 启动服务
        print("\n2. 启动服务...")
        subprocess.run(["docker-compose", "up", "-d"], capture_output=True)
        print("✅ 服务启动命令已执行")
        
        # 等待启动
        print("\n3. 等待服务启动...")
        time.sleep(30)
        
        # 检查服务状态
        print("\n4. 检查服务状态...")
        env_info = self.detect_environment()
        try:
            response = requests.get(env_info["backend_url"], timeout=10)
            if response.status_code == 200:
                print("✅ 后端服务正常")
            else:
                print(f"⚠️  后端状态: {response.status_code}")
        except:
            print("⚠️  后端检查失败，可能仍在启动中")
        
        # 获取访问地址
        print("\n5. 访问地址:")
        print(f"   前端: {env_info['frontend_url']}")
        print(f"   后端: {env_info['backend_url']}")
        print(f"   文档: {env_info['docs_url']}")
        
        print("\n✅ 快速启动完成！")
        return True
    
    def run_quick_check(self):
        """快速服务检查"""
        print(f"{Color.CYAN}🔍 快速服务检查{Color.RESET}")
        print("=" * 40)
        
        for service_name in self.services.keys():
            service = self.check_service(service_name)
            status_emoji = {
                "healthy": "✅",
                "unhealthy": "❌",
                "timeout": "⏰", 
                "connection_error": "🔌",
                "error": "💥",
                "unknown": "❓"
            }.get(service["status"], "❓")
            
            print(f"{status_emoji} {service['name']}: {service['status']}")
            if service['response_time']:
                print(f"   响应时间: {service['response_time']:.2f}s")
            print(f"   URL: {service['url']}")
        
        # Docker状态
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"\n🐳 Docker容器:")
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            container_info = json.loads(line)
                            containers.append(container_info)
                        except json.JSONDecodeError:
                            continue
                
                for container in containers:
                    state = container.get('State', 'unknown')
                    status_emoji = "🟢" if state == "running" else "🔴"
                    print(f"{status_emoji} {container.get('Name', 'unknown')}: {state}")
        except:
            print("\n🐳 无法获取Docker状态")
    
    def run_interactive_monitoring(self):
        """交互式监控"""
        print(f"启动服务监控...")
        print(f"按 Ctrl+C 退出监控")
        time.sleep(2)
        
        try:
            while True:
                # 检查所有服务
                for service_name in self.services.keys():
                    self.check_service(service_name)
                
                # 清屏
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"{'=' * 60}")
                print(f"📊 GoodTxt 服务状态监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'=' * 60}")
                
                # 服务状态
                print(f"\n🔍 服务状态:")
                for service_name, service in self.services.items():
                    status_emoji = {
                        "healthy": "✅",
                        "unhealthy": "❌", 
                        "timeout": "⏰",
                        "connection_error": "🔌",
                        "error": "💥",
                        "unknown": "❓"
                    }.get(service["status"], "❓")
                    
                    status_color = {
                        "healthy": "\033[92m",
                        "unhealthy": "\033[91m",
                        "timeout": "\033[93m", 
                        "connection_error": "\033[91m",
                        "error": "\033[91m",
                        "unknown": "\033[90m"
                    }.get(service["status"], "\033[90m")
                    
                    response_time_str = f"{service['response_time']:.2f}s" if service['response_time'] else "N/A"
                    
                    print(f"  {status_emoji} {service['name']}: {status_color}{service['status'].upper()}\033[0m")
                    print(f"     URL: {service['url']}")
                    print(f"     响应时间: {response_time_str}")
                    print(f"     最后检查: {service['last_check'].strftime('%H:%M:%S') if service['last_check'] else 'Never'}")
                    print(f"     错误计数: {service['error_count']}")
                    
                    if service_name == "backend" and hasattr(service, 'agent_count'):
                        print(f"     AI代理数量: {service['agent_count']}")
                    
                    print()
                
                # 快速操作
                print(f"🔧 快速操作:")
                print(f"  [1] 查看日志")
                print(f"  [2] 重启服务") 
                print(f"  [3] 停止服务")
                print(f"  [4] 刷新状态")
                print(f"  [0] 退出")
                
                print(f"\n{'=' * 60}")
                
                # 等待10秒后刷新
                time.sleep(10)
                
        except KeyboardInterrupt:
            print(f"\n退出监控...")
    
    def ask_user_choice(self) -> str:
        """询问用户选择"""
        print(f"\n{Color.BOLD}{Color.CYAN}请选择操作:{Color.RESET}")
        print(f"{Color.GREEN}1. 完整部署 (推荐){Color.RESET} - 运行环境检查 + 启动服务")
        print(f"{Color.YELLOW}2. 快速启动{Color.RESET} - 一键启动，跳过详细检查") 
        print(f"{Color.BLUE}3. 环境检查{Color.RESET} - 仅检查环境，不启动服务")
        print(f"{Color.PURPLE}4. 服务监控{Color.RESET} - 实时监控服务状态")
        print(f"{Color.CYAN}5. 快速检查{Color.RESET} - 检查当前服务状态")
        print(f"{Color.MAGENTA}6. 环境检测{Color.RESET} - 检测网络和IP信息")
        print(f"{Color.RED}0. 退出{Color.RESET}")
        
        while True:
            try:
                choice = input(f"\n{Color.BOLD}请输入选择 (0-6): {Color.RESET}").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6']:
                    return choice
                print(f"{Color.RED}无效选择，请输入 0-6{Color.RESET}")
            except KeyboardInterrupt:
                return '0'
    
    def show_environment_info(self):
        """显示环境信息"""
        print(f"\n{Color.BOLD}{Color.PURPLE}🌐 环境检测结果{Color.RESET}")
        print("=" * 40)
        
        env_info = self.detect_environment()
        
        print(f"本地IP: {env_info['local_ip']}")
        if env_info['public_ip']:
            print(f"公网IP: {env_info['public_ip']}")
        else:
            print(f"公网IP: 无法获取")
            
        if env_info['is_server']:
            print(f"环境类型: 服务器环境 ({env_info['reason']})")
        else:
            print(f"环境类型: 本地环境")
        
        print()
        print("🌐 访问地址:")
        print(f"   前端界面: {env_info['frontend_url']}")
        print(f"   后端API: {env_info['backend_url']}")
        print(f"   API文档: {env_info['docs_url']}")
        print()
        
        input(f"\n{Color.GREEN}按回车键继续...{Color.RESET}")
    
    def run_interactive(self):
        """交互式运行"""
        self.print_banner()
        
        while True:
            choice = self.ask_user_choice()
            
            if choice == '0':
                print(f"{Color.YELLOW}退出程序{Color.RESET}")
                break
            elif choice == '1':
                # 完整部署
                print(f"\n{Color.GREEN}🚀 开始完整部署...{Color.RESET}")
                if self.run_environment_check():
                    if self.start_services():
                        if self.wait_for_services():
                            if self.verify_deployment():
                                self.print_success_summary()
                            else:
                                print(f"{Color.RED}❌ 部署验证失败{Color.RESET}")
                        else:
                            print(f"{Color.YELLOW}⚠️  服务启动超时{Color.RESET}")
                    else:
                        print(f"{Color.RED}❌ 服务启动失败{Color.RESET}")
                else:
                    print(f"{Color.RED}❌ 环境检查未通过{Color.RESET}")
            elif choice == '2':
                # 快速启动
                print(f"\n{Color.BLUE}🚀 快速启动...{Color.RESET}")
                self.run_quick_start()
            elif choice == '3':
                # 环境检查
                print(f"\n{Color.YELLOW}🔍 运行环境检查...{Color.RESET}")
                self.run_environment_check()
            elif choice == '4':
                # 服务监控
                print(f"\n{Color.PURPLE}📊 启动服务监控...{Color.RESET}")
                self.run_interactive_monitoring()
            elif choice == '5':
                # 快速检查
                print(f"\n{Color.CYAN}🔍 快速检查服务状态...{Color.RESET}")
                self.run_quick_check()
                input(f"\n{Color.GREEN}按回车键继续...{Color.RESET}")
            elif choice == '6':
                # 环境检测
                self.show_environment_info()
            
            # 询问是否继续
            if choice != '0':
                print(f"\n{Color.CYAN}是否继续其他操作? (y/n): {Color.RESET}", end="")
                try:
                    continue_choice = input().strip().lower()
                    if continue_choice not in ['y', 'yes', '是']:
                        break
                except KeyboardInterrupt:
                    break
                print()
    
    def run_auto(self):
        """自动运行（用于脚本调用）"""
        self.print_banner()
        print(f"{Color.CYAN}自动模式：完整部署流程{Color.RESET}\n")
        
        if not self.run_environment_check():
            print(f"{Color.RED}❌ 环境检查失败，退出{Color.RESET}")
            return False
        
        if not self.start_services():
            print(f"{Color.RED}❌ 服务启动失败，退出{Color.RESET}")
            return False
        
        if not self.wait_for_services():
            print(f"{Color.YELLOW}⚠️  服务启动超时，但继续验证{Color.RESET}")
        
        if not self.verify_deployment():
            print(f"{Color.RED}❌ 部署验证失败{Color.RESET}")
            return False
        
        self.print_success_summary()
        return True


def main():
    """主函数"""
    launcher = SuperLauncher()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            launcher.run_auto()
        elif sys.argv[1] == "--quick":
            launcher.run_quick_start()
        elif sys.argv[1] == "--check":
            launcher.run_environment_check()
        elif sys.argv[1] == "--monitor":
            launcher.run_interactive_monitoring()
        elif sys.argv[1] == "--quick-check":
            launcher.run_quick_check()
        else:
            print("用法: python3 super_launcher.py [--auto|--quick|--check|--monitor|--quick-check]")
    else:
        launcher.run_interactive()


if __name__ == "__main__":
    main()