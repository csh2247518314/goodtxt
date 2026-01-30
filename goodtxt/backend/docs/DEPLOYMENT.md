# 多AI协同小说生成系统 - 部署指南

本文档详细说明如何在Linux服务器上部署多AI协同小说生成系统。

## 目录

- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [安装方式](#安装方式)
- [配置说明](#配置说明)
- [启动服务](#启动服务)
- [验证部署](#验证部署)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [监控运维](#监控运维)

## 系统要求

### 最低要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / RHEL 7+
- **CPU**: 4核心 2.0GHz+
- **内存**: 8GB RAM
- **存储**: 50GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **CPU**: 8核心 3.0GHz+
- **内存**: 16GB+ RAM
- **存储**: 100GB+ SSD
- **网络**: 千兆以太网

### 端口要求
| 端口 | 服务 | 说明 |
|------|------|------|
| 8000 | API服务 | 主要API接口 |
| 3000 | Grafana | 监控面板 |
| 9090 | Prometheus | 指标收集 |
| 9091 | Prometheus Web | 指标查看 |
| 3100 | Loki | 日志服务 |
| 6379 | Redis | 缓存服务 |
| 8001 | ChromaDB | 向量数据库 |

## 环境准备

### 1. 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. 安装基础依赖
```bash
# Ubuntu/Debian
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# CentOS/RHEL
sudo yum install -y curl wget git unzip wget curl gnupg2 software-properties-common
```

### 3. 安装Docker
```bash
# 添加Docker官方仓库
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

### 4. 安装Docker Compose
```bash
# 下载最新版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 5. 安装Python和pip
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y python3 python3-pip
```

## 安装方式

### 方式一：一键自动安装（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/csh2247518314/goodtxt.git
cd multi-ai-novel-generator

# 2. 运行安装脚本
chmod +x scripts/install.sh
./scripts/install.sh
```

安装脚本将自动完成：
- 系统环境检查
- 目录结构创建
- 配置文件生成
- Docker镜像构建
- 服务启动
- 健康检查

### 方式二：手动安装

```bash
# 1. 创建目录结构
mkdir -p data logs exports config scripts monitoring/grafana/dashboards

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑配置文件
vim .env

# 4. 构建镜像
docker build -t multi-ai-novel-generator:latest .

# 5. 启动服务
docker-compose up -d

# 6. 检查服务状态
docker-compose ps
```

## 配置说明

### 环境变量配置

编辑 `.env` 文件：

```bash
# AI模型API配置
SILICONFLOW_API_KEY=your_siliconflow_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
MINIMAX_API_KEY=your_minimax_api_key

# 数据库配置
REDIS_HOST=redis
REDIS_PORT=6379
CHROMA_HOST=chroma
CHROMA_PORT=8000
SQLITE_PATH=./data/novel.db

# 应用配置
APP_DEBUG=false
LOG_LEVEL=INFO
METRICS_ENABLED=true

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### API密钥获取

#### 1. 硅基流动 (SiliconFlow)
- 注册：https://siliconflow.cn
- 获取API密钥：控制台 → API密钥
- 充值账户余额

#### 2. 深度求索 (DeepSeek)
- 注册：https://platform.deepseek.com
- 获取API密钥：个人中心 → API管理
- 设置使用限制

#### 3. 通义千问 (Qwen)
- 注册：https://dashscope.console.aliyun.com
- 创建应用 → 获取API Key
- 配置调用白名单

#### 4. MiniMax
- 注册：https://api.minimax.chat
- 获取API密钥：开发者控制台
- 设置API调用配额

## 启动服务

### 启动所有服务
```bash
cd multi-ai-novel-generator
docker-compose up -d
```

### 启动特定服务
```bash
# 只启动核心服务
docker-compose up -d redis chroma app

# 启动监控服务
docker-compose up -d prometheus grafana loki promtail
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart app
```

## 验证部署

### 1. 检查服务状态
```bash
docker-compose ps
```

期望输出：
```
NAME                           COMMAND                  SERVICE             STATUS              PORTS
novel-generator-app            "python main.py"         app                 running             0.0.0.0:8000->8000/tcp, 0.0.0.0:9090->9090/tcp
novel-generator-chroma         "/bin/bash -c 'chroma…"   chroma              running             0.0.0.0:8002->8000/tcp
novel-generator-grafana        "/run.sh"                grafana             running             0.0.0.0:3000->3000/tcp
novel-generator-loki           "/usr/bin/loki -confi…"   loki                running             0.0.0.0:3100->3100/tcp
novel-generator-prometheus      "/bin/prometheus --co…"   prometheus          running             0.0.0.0:9091->9090/tcp
novel-generator-promtail       "/usr/bin/promtail -c…"   promtail            running             
novel-generator-redis         "docker-entrypoint.s…"   redis               running             0.0.0.0:6380->6379/tcp
```

### 2. 健康检查
```bash
# 检查API健康状态
curl http://localhost:8000/health

# 检查Redis
docker exec novel-generator-redis redis-cli ping

# 检查ChromaDB
curl http://localhost:8002/api/v1/heartbeat
```

### 3. 功能测试
```bash
# 运行API示例
python examples/api_examples.py
```

### 4. 访问监控面板
- **API文档**: http://localhost:8000/docs
- **监控面板**: http://localhost:3002 (admin/admin123)
- **Prometheus**: http://localhost:9091
- **日志查看**: http://localhost:3100

## 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看服务日志
docker-compose logs app
docker-compose logs redis
docker-compose logs chroma

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查磁盘空间
df -h
```

#### 2. API调用失败
```bash
# 检查API服务日志
docker-compose logs -f app

# 验证配置
docker-compose exec app python -c "from src.config.settings import get_settings; print(get_settings().validate_config())"
```

#### 3. 数据库连接问题
```bash
# 检查Redis连接
docker-compose exec app redis-cli -h redis ping

# 检查ChromaDB连接
curl http://chroma:8000/api/v1/heartbeat
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h
docker stats

# 清理Docker缓存
docker system prune -a
```

### 日志查看

```bash
# 实时查看应用日志
docker-compose logs -f app

# 查看所有服务日志
docker-compose logs

# 查看特定时间范围日志
docker-compose logs --since="2023-01-01T00:00:00" app
```

### 重置系统

```bash
# 停止所有服务
docker-compose down

# 清理所有数据
docker-compose down -v
sudo rm -rf data/ logs/ exports/

# 重新启动
./scripts/install.sh
```

## 性能优化

### 1. 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化网络参数
echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. Docker优化

创建 `docker-compose.override.yml`：

```yaml
version: '3.8'
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    environment:
      - PYTHONUNBUFFERED=1
      - WORKERS=4

  redis:
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  chroma:
    environment:
      - ANONYMIZED_TELEMETRY=false
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 3. 数据库优化

```bash
# 优化Redis配置
echo 'maxmemory 4gb' >> config/redis.conf
echo 'maxmemory-policy allkeys-lru' >> config/redis.conf

# 定期清理日志
echo '0 2 * * * docker system prune -f' | crontab -
```

## 监控运维

### 1. 自动化备份

创建备份脚本 `scripts/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/backup/novel-generator"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据
docker exec novel-generator-redis redis-cli BGSAVE
docker cp novel-generator-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# 备份配置文件
cp .env $BACKUP_DIR/env_$DATE
cp docker-compose.yml $BACKUP_DIR/compose_$DATE

# 压缩备份
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR redis_$DATE.rdb env_$DATE compose_$DATE

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

设置定时任务：
```bash
chmod +x scripts/backup.sh
echo '0 3 * * * /path/to/scripts/backup.sh' | crontab -
```

### 2. 监控脚本

创建监控脚本 `scripts/monitor.sh`：

```bash
#!/bin/bash

# 检查服务状态
services=("app" "redis" "chroma")
for service in "${services[@]}"; do
    if ! docker-compose ps | grep -q "$service.*Up"; then
        echo "ALERT: Service $service is down"
        # 发送告警邮件或执行重启
        docker-compose restart $service
    fi
done

# 检查磁盘空间
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "ALERT: Disk usage is ${disk_usage}%"
    # 清理日志文件
    docker system prune -f
fi

# 检查内存使用
mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $mem_usage -gt 90 ]; then
    echo "ALERT: Memory usage is ${mem_usage}%"
fi

echo "Monitoring check completed at $(date)"
```

设置监控任务：
```bash
chmod +x scripts/monitor.sh
echo '*/5 * * * * /path/to/scripts/monitor.sh' | crontab -
```

### 3. 日志轮转

创建 `logrotate.conf`：

```
/var/log/novel-generator/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart app
    endscript
}
```

## 更新升级

### 1. 代码更新
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 2. 数据迁移
```bash
# 备份当前数据
./scripts/backup.sh

# 更新代码
git pull

# 运行数据库迁移（如果有）
docker-compose exec app python -m src.migrations.migrate

# 重启服务
docker-compose up -d
```

## 安全建议

### 1. 网络安全
- 使用防火墙限制端口访问
- 配置SSL证书启用HTTPS
- 设置API访问频率限制

### 2. 数据安全
- 定期备份数据库
- 加密敏感配置信息
- 使用强密码和API密钥

### 3. 系统安全
- 定期更新系统和Docker
- 监控系统访问日志
- 限制Docker容器权限

---

如需技术支持，请参考项目的GitHub仓库或提交Issue。