#!/bin/bash

# GoodTxt 多AI协同小说生成系统 - 自动部署脚本

set -e

echo "🚀 开始部署 GoodTxt 系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录结构..."
    
    mkdir -p data/database
    mkdir -p data/chroma
    mkdir -p data/exports
    mkdir -p logs
    mkdir -p config/nginx
    mkdir -p config/redis
    mkdir -p scripts
    
    log_success "目录结构创建完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    cat > config/redis/redis.conf << EOF
# Redis配置文件
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename goodtxt.rdb
dir /data
maxmemory 512mb
maxmemory-policy allkeys-lru
EOF
    
    log_success "Redis配置完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    cat > config/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # 前端静态文件
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # 后端API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # WebSocket连接
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # 导出文件下载
        location /exports/ {
            alias /var/www/exports/;
            expires 1d;
        }
    }
}
EOF
    
    log_success "Nginx配置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    if command -v python3 &> /dev/null; then
        python3 scripts/setup-database.py
        log_success "数据库初始化完成"
    else
        log_warning "Python3未找到，跳过数据库初始化"
    fi
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建后端镜像
    docker-compose build backend
    
    # 构建前端镜像
    docker-compose build frontend
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动核心服务
    docker-compose up -d redis chroma
    
    # 等待服务就绪
    log_info "等待数据库服务就绪..."
    sleep 10
    
    # 初始化数据库
    docker-compose run --rm db-init
    
    # 启动完整服务
    docker-compose up -d backend frontend
    
    log_success "服务启动完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    echo ""
    log_success "部署完成！"
    echo ""
    echo "📱 访问地址:"
    echo "   前端界面: http://localhost:3002"
    echo "   后端API:  http://localhost:8000"
    echo "   API文档:  http://localhost:8000/docs"
    echo ""
    echo "🔧 常用命令:"
    echo "   查看日志: docker-compose logs -f"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart"
    echo ""
}

# 主函数
main() {
    echo "GoodTxt 多AI协同小说生成系统 - 自动部署脚本"
    echo "================================================"
    
    # 检查依赖
    log_info "检查系统依赖..."
    check_command docker
    check_command docker-compose
    
    # 检查.env文件
    if [ ! -f .env ]; then
        log_warning ".env文件不存在，正在复制示例文件..."
        cp .env.example .env
        log_warning "请编辑.env文件并配置AI API密钥"
    fi
    
    # 创建目录和配置
    create_directories
    setup_redis
    setup_nginx
    
    # 询问是否需要初始化数据库
    read -p "是否初始化数据库? (y/N): " init_db
    if [[ $init_db =~ ^[Yy]$ ]]; then
        init_database
    fi
    
    # 询问是否构建镜像
    read -p "是否构建Docker镜像? (y/N): " build
    if [[ $build =~ ^[Yy]$ ]]; then
        build_images
    fi
    
    # 启动服务
    start_services
    
    # 显示状态
    show_status
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"