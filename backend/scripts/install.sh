#!/bin/bash

# 多AI协同小说生成系统 - 一键安装脚本
# 作者: MiniMax Agent
# 版本: 0.1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_step "检查系统要求..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python 3.9+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    log_info "检测到 Python 版本: $python_version"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查内存
    total_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_memory" -lt 4096 ]; then
        log_warn "建议内存至少4GB，当前: ${total_memory}MB"
    fi
    
    # 检查磁盘空间
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 10 ]; then
        log_error "磁盘空间不足，至少需要10GB可用空间"
        exit 1
    fi
    
    log_info "系统要求检查通过"
}

# 创建目录结构
create_directories() {
    log_step "创建目录结构..."
    
    directories=(
        "data"
        "logs" 
        "exports"
        "config"
        "scripts"
        "monitoring"
        "monitoring/grafana"
        "monitoring/dashboards"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "创建目录: $dir"
    done
}

# 创建配置文件
create_config_files() {
    log_step "创建配置文件..."
    
    # Redis配置文件
    cat > config/redis.conf << 'EOF'
# Redis配置文件
port 6379
bind 0.0.0.0
timeout 0
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
maxmemory 512mb
maxmemory-policy allkeys-lru
EOF

    # Prometheus配置文件
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'novel-generator'
    static_configs:
      - targets: ['app:9090']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6380']
    scrape_interval: 30s

  - job_name: 'chroma'
    static_configs:
      - targets: ['chroma:8000']
    scrape_interval: 30s
    metrics_path: /api/v1/metrics
EOF

    # Loki配置文件
    cat > monitoring/loki.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093
EOF

    # Promtail配置文件
    cat > monitoring/promtail.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/log/app/*.log

  - job_name: novel-generator
    static_configs:
      - targets:
          - localhost
        labels:
          job: novel-generator
          __path__: /var/log/app/*.log
EOF

    # Grafana配置
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
EOF

    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/provisioning/dashboards
    cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

    log_info "配置文件创建完成"
}

# 创建环境变量文件
create_env_file() {
    log_step "创建环境变量文件..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        log_info "已创建 .env 文件，请编辑该文件填入API密钥"
        
        # 提示用户配置API密钥
        echo ""
        echo -e "${YELLOW}重要提醒：${NC}"
        echo "请编辑 .env 文件，配置以下API密钥："
        echo "  - SILICONFLOW_API_KEY (硅基流动)"
        echo "  - DEEPSEEK_API_KEY (深度求索)"
        echo "  - QWEN_API_KEY (通义千问)"
        echo "  - MINIMAX_API_KEY (MiniMax)"
        echo ""
        read -p "配置完成后按Enter键继续..." -r
    else
        log_info ".env 文件已存在，跳过创建"
    fi
}

# 安装Docker依赖
install_docker_dependencies() {
    log_step "安装Docker依赖..."
    
    # 复制Docker相关文件
    if [ -f "Dockerfile" ]; then
        log_info "Dockerfile已存在"
    else
        log_error "Dockerfile不存在，请检查项目文件"
        exit 1
    fi
    
    if [ -f "docker-compose.yml" ]; then
        log_info "docker-compose.yml已存在"
    else
        log_error "docker-compose.yml不存在，请检查项目文件"
        exit 1
    fi
    
    # 构建Docker镜像
    log_info "构建Docker镜像..."
    docker build -t multi-ai-novel-generator:latest .
    
    log_info "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    # 启动服务
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    log_info "服务启动中，请稍候..."
    
    # 等待服务启动
    sleep 30
    
    # 检查服务状态
    log_info "检查服务状态..."
    
    services=("redis" "chroma" "app" "prometheus" "grafana")
    
    for service in "${services[@]}"; do
        if docker ps | grep -q "$service"; then
            log_info "$service 服务运行正常"
        else
            log_error "$service 服务启动失败"
        fi
    done
}

# 运行健康检查
health_check() {
    log_step "运行健康检查..."
    
    # 检查API服务
    if curl -s http://localhost:8000/health > /dev/null; then
        log_info "API服务健康检查通过"
    else
        log_warn "API服务可能尚未完全启动，请稍后重试"
    fi
    
    # 检查Redis
    if docker exec novel-generator-redis redis-cli ping | grep -q PONG; then
        log_info "Redis服务健康检查通过"
    else
        log_error "Redis服务健康检查失败"
    fi
    
    # 检查ChromaDB
    if curl -s http://localhost:8002/api/v1/heartbeat > /dev/null; then
        log_info "ChromaDB服务健康检查通过"
    else
        log_warn "ChromaDB服务可能尚未完全启动"
    fi
}

# 显示访问信息
show_access_info() {
    log_step "显示访问信息..."
    
    echo ""
    echo -e "${GREEN}=== 安装完成 ===${NC}"
    echo ""
    echo "🌐 服务访问地址："
    echo "  📊 API文档:    http://localhost:8000/docs"
    echo "  📈 监控面板:   http://localhost:3002"
    echo "  🔍 Prometheus: http://localhost:9091"
    echo "  📋 日志查看:   http://localhost:3100"
    echo ""
    echo "🔧 管理命令："
    echo "  启动服务: docker-compose up -d"
    echo "  停止服务: docker-compose down"
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo ""
    echo "📖 使用说明："
    echo "  1. 访问 http://localhost:8000/docs 查看API文档"
    echo "  2. 使用POST /projects接口创建小说项目"
    echo "  3. 使用POST /projects/{id}/generate开始生成"
    echo "  4. 使用GET /projects/{id}查看进度"
    echo ""
    echo -e "${YELLOW}注意事项：${NC}"
    echo "  - 确保 .env 文件中的API密钥配置正确"
    echo "  - 首次运行可能需要下载模型，请耐心等待"
    echo "  - 如遇问题请查看日志：docker-compose logs -f app"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════╗"
    echo "║     多AI协同小说生成系统 - 一键安装脚本      ║"
    echo "║              版本: 0.1.0                   ║"
    echo "║              作者: MiniMax Agent            ║"
    echo "╚══════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # 执行安装步骤
    check_requirements
    create_directories
    create_config_files
    create_env_file
    install_docker_dependencies
    start_services
    health_check
    show_access_info
    
    log_info "安装完成！"
}

# 错误处理
trap 'log_error "安装过程中出现错误，退出安装"; exit 1' ERR

# 运行主函数
main "$@"