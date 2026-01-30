#!/bin/bash

# GoodTxt 多AI协同小说生成系统 - 国内镜像安装脚本
# 集成阿里云镜像源，解决Docker安装网络问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            log_info "检测到 Debian/Ubuntu 系统"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            log_info "检测到 RedHat/CentOS 系统"
        else
            OS="linux"
            log_info "检测到 Linux 系统"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "检测到 macOS 系统"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "检测到root用户，建议使用普通用户运行此脚本"
        echo "请确保已设置Docker用户权限"
    fi
}

# 更新系统包
update_system() {
    log_info "更新系统包管理器..."
    
    case $OS in
        "debian")
            sudo apt update -y
            ;;
        "redhat")
            sudo yum update -y
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                log_info "安装 Homebrew..."
                echo "请手动安装 Homebrew："
                echo "1. 访问 https://brew.sh"
                echo "2. 或运行以下命令："
                echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo "3. 然后重新运行此脚本"
                exit 1
            fi
            ;;
        "linux")
            # 对于其他Linux发行版，尝试通用命令
            if command -v apt &> /dev/null; then
                sudo apt update -y
            elif command -v yum &> /dev/null; then
                sudo yum update -y
            elif command -v pacman &> /dev/null; then
                sudo pacman -Sy
            else
                log_warning "未识别的Linux发行版，请手动安装依赖"
            fi
            ;;
    esac
}

# 安装基础依赖
install_dependencies() {
    log_info "安装基础依赖..."
    
    case $OS in
        "debian")
            sudo apt install -y curl wget git python3 python3-pip build-essential
            ;;
        "redhat")
            sudo yum install -y curl wget git python3 python3-pip gcc gcc-c++ make
            ;;
        "macos")
            brew install git python3
            ;;
        "linux")
            if command -v apt &> /dev/null; then
                sudo apt install -y curl wget git python3 python3-pip build-essential
            elif command -v yum &> /dev/null; then
                sudo yum install -y curl wget git python3 python3-pip gcc gcc-c++ make
            elif command -v pacman &> /dev/null; then
                sudo pacman -S curl wget git python3 python3-pip base-devel
            fi
            ;;
    esac
}

# 配置Docker国内镜像源
configure_docker_mirror() {
    log_info "配置Docker国内镜像源..."
    
    # 创建Docker配置目录
    sudo mkdir -p /etc/docker
    
    # 创建daemon.json配置文件，使用阿里云镜像
    sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
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
EOF

    log_success "Docker镜像源配置完成"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    case $OS in
        "debian")
            # 移除旧版本Docker
            sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            
            # 安装必要的包
            sudo apt install -y apt-transport-https ca-certificates software-properties-common
            
            # 添加Docker的官方GPG密钥
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # 设置stable存储库
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # 更新包索引
            sudo apt update
            
            # 安装Docker CE
            sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            # 重新配置镜像源
            configure_docker_mirror
            
            # 重启Docker服务
            sudo systemctl restart docker
            
            # 添加当前用户到docker组
            sudo usermod -aG docker $USER
            log_success "Docker CE 安装完成"
            ;;
        "redhat")
            # 安装Docker
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            # 重新配置镜像源
            configure_docker_mirror
            
            # 启动并启用Docker
            sudo systemctl start docker
            sudo systemctl enable docker
            
            # 添加当前用户到docker组
            sudo usermod -aG docker $USER
            log_success "Docker 安装完成"
            ;;
        "macos")
            # macOS推荐使用Docker Desktop
            if ! command -v docker &> /dev/null; then
                log_warning "请手动下载并安装Docker Desktop for Mac"
                log_info "下载地址: https://www.docker.com/products/docker-desktop"
                log_info "安装完成后，请重新运行此脚本"
                exit 0
            fi
            ;;
        "linux")
            # 尝试安装Docker
            if command -v apt &> /dev/null; then
                # Debian/Ubuntu
                sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
                sudo apt install -y apt-transport-https ca-certificates software-properties-common
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt update
                sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                configure_docker_mirror
                sudo systemctl restart docker
                sudo usermod -aG docker $USER
            elif command -v yum &> /dev/null; then
                # RedHat/CentOS
                sudo yum install -y yum-utils
                sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                configure_docker_mirror
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
            elif command -v pacman &> /dev/null; then
                # Arch Linux
                sudo pacman -S docker docker-compose
                configure_docker_mirror
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
            else
                log_error "无法在当前Linux发行版上自动安装Docker"
                exit 1
            fi
            log_success "Docker 安装完成"
            ;;
    esac
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        docker --version
        log_success "Docker 已安装"
    else
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if command -v docker compose &> /dev/null; then
        docker compose version
        log_success "Docker Compose 已安装"
    elif command -v docker-compose &> /dev/null; then
        docker-compose --version
        log_success "Docker Compose 已安装"
    else
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 测试Docker镜像拉取
    log_info "测试Docker镜像拉取..."
    if docker pull hello-world &> /dev/null; then
        log_success "Docker 镜像拉取正常"
        docker rmi hello-world &> /dev/null || true
    else
        log_warning "Docker镜像拉取可能有问题，请检查网络连接"
    fi
}

# 设置项目权限
setup_project() {
    log_info "设置项目权限..."
    
    # 确保脚本可执行
    chmod +x *.sh *.py 2>/dev/null || true
    
    # 创建必要目录
    mkdir -p data/database data/exports logs
    
    log_success "项目权限设置完成"
}

# 显示完成信息
show_completion() {
    echo
    echo "================================================"
    echo -e "${GREEN}           安装完成！${NC}"
    echo "================================================"
    echo
    echo "下一步操作："
    echo "1. 重新登录以使Docker组权限生效："
    echo "   newgrp docker"
    echo
    echo "2. 运行超级启动器："
    echo "   python3 super_launcher.py"
    echo
    echo "3. 选择部署模式并启动服务"
    echo
    echo "如果遇到权限问题，请尝试："
    echo "   sudo usermod -aG docker $USER"
    echo "   newgrp docker"
    echo
    echo "================================================"
}

# 主函数
main() {
    echo "================================================"
    echo "GoodTxt 多AI协同小说生成系统"
    echo "国内镜像安装脚本 v1.0"
    echo "================================================"
    echo
    
    # 检查参数
    if [[ "$1" == "--skip-docker" ]]; then
        log_info "跳过Docker安装..."
        install_dependencies
        setup_project
        show_completion
        exit 0
    fi
    
    # 执行安装流程
    detect_os
    check_root
    update_system
    install_dependencies
    install_docker
    verify_installation
    setup_project
    show_completion
}

# 运行主函数
main "$@"