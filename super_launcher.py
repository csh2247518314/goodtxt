#!/usr/bin/env python3
"""
GoodTxt 多AI协同小说生成系统 - 超级启动器 v2.0
整合环境检查、自动修复、服务监控、快速启动、Docker安装、数据库初始化的一站式解决方案
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
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib

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
    """超级启动器 - 整合所有功能的智能系统"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        self.installed_packages = []
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
        print("║              🚀 GoodTxt 超级启动器 v2.0 🚀                  ║")
        print("║          多AI协同小说生成系统智能管理                   ║")
        print("║                    一站式解决方案                         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Color.RESET}")
    
    def print_header(self):
        """打印标题"""
        print(f"{Color.BOLD}{Color.CYAN}")
        print("=" * 80)
        print("🚀 GoodTxt 多AI协同小说生成系统 - 智能管理系统")
        print("=" * 80)
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
        elif status == "install":
            print(f"  {Color.BLUE}📦 {message}{Color.RESET}")
    
    def run_command(self, command: str, capture_output: bool = True, timeout: int = 30) -> Tuple[bool, str, str]:
        """执行命令"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=timeout
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
    
    def detect_os(self):
        """检测操作系统"""
        if platform.system() == "Windows":
            return "windows"
        elif platform.system() == "Darwin":
            return "macos"
        elif platform.system() == "Linux":
            if os.path.exists("/etc/debian_version"):
                return "debian"
            elif os.path.exists("/etc/redhat-release"):
                return "redhat"
            else:
                return "linux"
        else:
            return "unknown"
    
    def check_root(self):
        """检查是否为root用户"""
        if os.geteuid() == 0:
            self.warnings.append("检测到root用户，建议使用普通用户运行此脚本")
            return True
        return False
    
    def update_system(self):
        """更新系统包"""
        self.print_step(1, 10, "更新系统包")
        
        os_type = self.detect_os()
        
        if os_type in ["debian", "ubuntu"]:
            success, stdout, stderr = self.run_command("sudo apt update -y")
            if success:
                self.print_status("系统包更新成功", "success")
            else:
                self.print_status("系统包更新失败", "warning")
        
        elif os_type in ["redhat", "centos"]:
            success, stdout, stderr = self.run_command("sudo yum update -y")
            if success:
                self.print_status("系统包更新成功", "success")
            else:
                self.print_status("系统包更新失败", "warning")
        
        return True
    
    def install_dependencies(self):
        """安装基础依赖"""
        self.print_step(2, 10, "安装基础依赖")
        
        os_type = self.detect_os()
        
        if os_type == "debian":
            packages = ["curl", "wget", "git", "python3", "python3-pip", "build-essential"]
            success, stdout, stderr = self.run_command(f"sudo apt install -y {' '.join(packages)}")
        elif os_type == "redhat":
            packages = ["curl", "wget", "git", "python3", "python3-pip", "gcc", "gcc-c++", "make"]
            success, stdout, stderr = self.run_command(f"sudo yum install -y {' '.join(packages)}")
        elif os_type == "macos":
            success, stdout, stderr = self.run_command("brew install git python3")
        else:
            success, stdout, stderr = self.run_command("curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh")
        
        if success:
            self.print_status("基础依赖安装成功", "success")
        else:
            self.print_status("基础依赖安装失败", "warning")
        
        return success
    
    def configure_docker_mirror(self):
        """配置Docker国内镜像源"""
        self.print_step(3, 10, "配置Docker镜像源")
        
        os_type = self.detect_os()
        
        if os_type in ["debian", "redhat", "linux"]:
            # 创建Docker配置目录
            os.system("sudo mkdir -p /etc/docker")
            
            # 创建daemon.json配置文件
            daemon_config = {
                "registry-mirrors": [
                    "https://docker.mirrors.ustc.edu.cn",
                    "https://hub-mirror.c.163.com",
                    "https://mirror.baidubce.com",
                    "https://ccr.ccs.tencentyun.com",
                    "https://swr.cn-north-1.nvidia.com"
                ],
                "log-driver": "json-file",
                "log-opts": {
                    "max-size": "10m",
                    "max-file": "3"
                }
            }
            
            config_content = json.dumps(daemon_config, indent=2)
            os.system(f"echo '{config_content}' | sudo tee /etc/docker/daemon.json > /dev/null")
            
            self.print_status("Docker镜像源配置完成", "success")
        
        return True
    
    def install_docker(self):
        """安装Docker"""
        self.print_step(4, 10, "安装Docker")
        
        os_type = self.detect_os()
        
        if os_type == "debian":
            # 移除旧版本Docker
            os.system("sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true")
            
            # 安装必要的包
            os.system("sudo apt install -y apt-transport-https ca-certificates software-properties-common")
            
            # 添加Docker的官方GPG密钥
            os.system("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg")
            
            # 设置stable存储库
            os.system('echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null')
            
            # 更新包索引
            os.system("sudo apt update")
            
            # 安装Docker CE
            os.system("sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin")
            
        elif os_type == "redhat":
            # 安装Docker
            os.system("sudo yum install -y yum-utils")
            os.system("sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo")
            os.system("sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin")
            
        elif os_type == "macos":
            self.print_status("macOS请手动安装Docker Desktop", "warning")
            return False
        
        # 配置镜像源
        self.configure_docker_mirror()
        
        # 重启Docker服务
        if os_type in ["debian", "redhat"]:
            os.system("sudo systemctl restart docker")
        
        # 添加当前用户到docker组
        os.system("sudo usermod -aG docker $USER")
        
        self.print_status("Docker安装完成", "success")
        return True
    
    def verify_docker_installation(self):
        """验证Docker安装"""
        self.print_step(5, 10, "验证Docker安装")
        
        # 检查Docker
        success, stdout, stderr = self.run_command("docker --version")
        if success:
            self.print_status(f"Docker版本: {stdout.strip()}", "success")
        else:
            self.print_status("Docker未安装", "error")
            return False
        
        # 检查Docker Compose
        success, stdout, stderr = self.run_command("docker compose --version")
        if not success:
            success, stdout, stderr = self.run_command("docker-compose --version")
        
        if success:
            self.print_status(f"Docker Compose版本: {stdout.strip()}", "success")
        else:
            self.print_status("Docker Compose未安装", "warning")
        
        # 测试Docker镜像拉取
        success, stdout, stderr = self.run_command("docker pull hello-world")
        if success:
            self.print_status("Docker镜像拉取正常", "success")
            os.system("docker rmi hello-world > /dev/null 2>&1 || true")
        else:
            self.print_status("Docker镜像拉取可能有问题", "warning")
        
        return True
    
    def setup_project_structure(self):
        """设置项目结构"""
        self.print_step(6, 10, "设置项目结构")
        
        required_dirs = [
            "data",
            "data/database",
            "data/exports",
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
    
    def check_python_environment(self):
        """检查Python环境"""
        self.print_step(7, 10, "检查Python环境")
        
        python_version = sys.version_info
        self.print_status(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}", "info")
        
        if python_version < (3, 8):
            self.warnings.append("Python版本过低，建议使用3.8+")
            self.print_status("Python版本过低，可能影响依赖安装", "warning")
            return False
        else:
            self.print_status("Python版本满足要求", "success")
        
        # 检查pip
        success, stdout, stderr = self.run_command("pip3 --version")
        if success:
            self.print_status(f"pip版本: {stdout.strip()}", "success")
        else:
            self.print_status("pip未安装", "warning")
        
        return True
    
    def init_database(self):
        """初始化数据库"""
        self.print_step(8, 10, "初始化数据库")
        
        db_script_path = self.project_root / "scripts" / "init_database.py"
        
        if db_script_path.exists():
            success, stdout, stderr = self.run_command(f"python3 {db_script_path}")
            if success:
                self.print_status("数据库初始化成功", "success")
                self.fixes_applied.append("数据库初始化")
            else:
                self.print_status(f"数据库初始化失败: {stderr}", "error")
                return False
        else:
            # 如果脚本不存在，尝试直接初始化
            try:
                self.initialize_database_manually()
                self.print_status("数据库手动初始化成功", "success")
            except Exception as e:
                self.print_status(f"数据库初始化失败: {e}", "error")
                return False
        
        return True
    
    def initialize_database_manually(self):
        """手动初始化数据库"""
        db_path = self.project_root / "data" / "database" / "goodtxt.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # SQL初始化脚本
        init_sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        );

        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            genre TEXT,
            length TEXT,
            theme TEXT,
            target_audience TEXT,
            language TEXT DEFAULT 'zh-CN',
            status TEXT DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );

        CREATE TABLE IF NOT EXISTS chapters (
            chapter_id TEXT PRIMARY KEY,
            project_id TEXT,
            chapter_number INTEGER,
            title TEXT,
            content TEXT,
            word_count INTEGER DEFAULT 0,
            quality_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (project_id)
        );

        CREATE TABLE IF NOT EXISTS user_tokens (
            token_id TEXT PRIMARY KEY,
            user_id TEXT,
            token TEXT UNIQUE NOT NULL,
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );

        CREATE TABLE IF NOT EXISTS system_logs (
            log_id TEXT PRIMARY KEY,
            level TEXT,
            message TEXT,
            source TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quality_reports (
            report_id TEXT PRIMARY KEY,
            chapter_id TEXT,
            score REAL,
            issues TEXT,
            suggestions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chapter_id) REFERENCES chapters (chapter_id)
        );

        CREATE TABLE IF NOT EXISTS memory (
            memory_id TEXT PRIMARY KEY,
            category TEXT,
            content TEXT,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agent_performance (
            performance_id TEXT PRIMARY KEY,
            agent_type TEXT,
            model_name TEXT,
            response_time REAL,
            success_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 创建数据库连接并执行SQL
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 执行SQL脚本
        cursor.executescript(init_sql)
        
        # 创建默认管理员用户
        admin_password_hash = hashlib.sha256("admin123456".encode()).hexdigest()
        admin_user_id = "admin_" + str(int(time.time()))
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_user_id, "admin", "admin@goodtxt.com", admin_password_hash, "admin"))
        
        conn.commit()
        conn.close()
    
    def check_project_files(self):
        """检查项目文件"""
        self.print_step(9, 10, "检查项目文件")
        
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
    
    def test_docker_compose_syntax(self):
        """测试Docker Compose语法"""
        self.print_step(10, 10, "验证Docker Compose配置")
        
        success, stdout, stderr = self.run_command("docker-compose config")
        if success:
            self.print_status("Docker Compose配置语法正确", "success")
        else:
            self.issues.append("Docker Compose配置语法错误")
            self.print_status("Docker Compose配置语法错误", "error")
            return False
        
        return True
    
    def run_full_installation(self):
        """运行完整安装流程"""
        self.print_header()
        print(f"\n{Color.BOLD}{Color.YELLOW}🔧 完整安装流程{Color.RESET}")
        print("=" * 50)
        
        self.check_root()
        
        steps = [
            ("更新系统包", self.update_system),
            ("安装基础依赖", self.install_dependencies),
            ("配置Docker镜像源", self.configure_docker_mirror),
            ("安装Docker", self.install_docker),
            ("验证Docker安装", self.verify_docker_installation),
            ("设置项目结构", self.setup_project_structure),
            ("检查Python环境", self.check_python_environment),
            ("初始化数据库", self.init_database),
            ("检查项目文件", self.check_project_files),
            ("验证Docker配置", self.test_docker_compose_syntax)
        ]
        
        success_count = 0
        for i, (name, func) in enumerate(steps, 1):
            try:
                if func():
                    success_count += 1
                    print()
            except Exception as e:
                self.print_status(f"{name}失败: {e}", "error")
        
        print(f"\n{Color.BOLD}{Color.GREEN}安装完成: {success_count}/{len(steps)} 步骤成功{Color.RESET}")
        
        if self.issues:
            print(f"\n{Color.RED}发现的问题:{Color.RESET}")
            for issue in self.issues:
                print(f"  ❌ {issue}")
        
        if self.warnings:
            print(f"\n{Color.YELLOW}警告:{Color.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        return len(self.issues) == 0
    
    def start_services(self):
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
    
    def wait_for_services(self, timeout: int = 120):
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
    
    def verify_deployment(self):
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
        
        print(f"\n{Color.CYAN}🔑 默认管理员账户:{Color.RESET}")
        print(f"   👤 用户名: {Color.YELLOW}admin{Color.RESET}")
        print(f"   🔑 密码: {Color.YELLOW}admin123456{Color.RESET}")
        
        print(f"\n{Color.CYAN}📋 使用说明:{Color.RESET}")
        print(f"   1. 访问前端界面开始使用")
        print(f"   2. 使用默认账户登录或注册新用户")
        print(f"   3. 创建小说项目开始创作")
        print(f"   4. 如果需要AI功能，请配置API密钥")
        
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
            print("❌ Docker未安装，请先运行完整安装")
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
        print(f"{Color.GREEN}1. 完整安装部署 (推荐){Color.RESET} - 安装Docker + 环境检查 + 启动服务")
        print(f"{Color.BLUE}2. 快速启动{Color.RESET} - 一键启动，跳过详细检查") 
        print(f"{Color.YELLOW}3. 环境检查{Color.RESET} - 仅检查环境，不启动服务")
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
        
        print(f"操作系统: {platform.system()} {platform.release()}")
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
                # 完整安装部署
                print(f"\n{Color.GREEN}🚀 开始完整安装部署...{Color.RESET}")
                if self.run_full_installation():
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
                    print(f"{Color.RED}❌ 安装失败{Color.RESET}")
            elif choice == '2':
                # 快速启动
                print(f"\n{Color.BLUE}🚀 快速启动...{Color.RESET}")
                self.run_quick_start()
            elif choice == '3':
                # 环境检查
                print(f"\n{Color.YELLOW}🔍 运行环境检查...{Color.RESET}")
                self.run_full_installation()
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
        print(f"{Color.CYAN}自动模式：完整安装和部署流程{Color.RESET}\n")
        
        if not self.run_full_installation():
            print(f"{Color.RED}❌ 安装失败，退出{Color.RESET}")
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
            launcher.run_full_installation()
        elif sys.argv[1] == "--monitor":
            launcher.run_interactive_monitoring()
        elif sys.argv[1] == "--quick-check":
            launcher.run_quick_check()
        elif sys.argv[1] == "--install":
            launcher.run_full_installation()
        elif sys.argv[1] == "--env":
            launcher.show_environment_info()
        else:
            print("用法: python3 super_launcher.py [--auto|--quick|--check|--monitor|--quick-check|--install|--env]")
            print("  --auto: 完整自动安装部署")
            print("  --quick: 快速启动服务")
            print("  --check: 环境检查和修复")
            print("  --monitor: 服务监控")
            print("  --quick-check: 快速检查服务状态")
            print("  --install: 完整安装流程")
            print("  --env: 环境检测")
    else:
        launcher.run_interactive()


if __name__ == "__main__":
    main()
