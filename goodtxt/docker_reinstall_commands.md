# Docker 镜像重新安装指令

## 🔄 重新安装Docker镜像服务

### 1. 清理现有Docker容器和镜像
```bash
# 停止所有容器
docker-compose down

# 强制停止所有运行中的容器
docker stop $(docker ps -aq)

# 删除所有容器
docker rm $(docker ps -aq)

# 删除未使用的镜像
docker image prune -a -f

# 删除未使用的卷
docker volume prune -f

# 清理Docker系统
docker system prune -a -f
```

### 2. 重新构建镜像
```bash
# 重新构建所有镜像
docker-compose build --no-cache

# 或者分别构建各个服务
docker-compose build backend --no-cache
docker-compose build frontend --no-cache
docker-compose build redis --no-cache
docker-compose build chroma --no-cache
```

### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看启动日志
docker-compose logs
```

### 4. 验证服务状态
```bash
# 检查容器状态
docker ps

# 查看容器资源使用
docker stats

# 检查特定服务
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis
docker-compose logs chroma
```

### 5. 手动启动单个服务验证
```bash
# 启动Redis验证
docker run -d --name test-redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes

# 测试Redis连接
docker exec test-redis redis-cli ping

# 清理测试容器
docker stop test-redis && docker rm test-redis

# 启动ChromaDB验证
docker run -d --name test-chroma \
  -p 8001:8000 \
  -e CHROMA_SERVER_HOST=0.0.0.0 \
  chromadb/chroma:latest

# 测试ChromaDB连接
curl http://localhost:8001/api/v1/heartbeat

# 清理测试容器
docker stop test-chroma && docker rm test-chroma
```

### 6. 端口占用检查和清理
```bash
# 检查端口占用
netstat -tulpn | grep -E ":(8000|3002|6379|8001)"

# 如果端口被占用，强制清理
sudo fuser -k 8000/tcp
sudo fuser -k 3002/tcp
sudo fuser -k 6379/tcp
sudo fuser -k 8001/tcp
```

### 7. 磁盘空间检查
```bash
# 检查Docker磁盘使用
docker system df

# 清理Docker磁盘空间
docker system prune -a --volumes -f

# 检查磁盘空间
df -h
```

### 8. 强制重建流程（完整）
```bash
# 完整重新安装流程
docker-compose down --volumes --remove-orphans
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d

# 等待服务启动
sleep 30

# 验证启动
curl -s http://localhost:8000/health
curl -s http://localhost:3002
```

### 9. 故障排查
```bash
# 查看具体容器日志
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend

# 进入容器调试
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec redis redis-cli

# 检查容器网络
docker network ls
docker network inspect goodtxt_goodtxt-network
```

### 10. 强制重置Docker环境
```bash
# 仅在完全重置时使用（会删除所有Docker数据）
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network prune -f
systemctl restart docker
```

## 🎯 推荐的重新安装步骤

**标准重新安装：**
```bash
# 1. 停止并清理
docker-compose down
docker system prune -a -f

# 2. 重新构建
docker-compose build --no-cache

# 3. 启动服务
docker-compose up -d

# 4. 验证
docker-compose ps
curl http://localhost:8000/health
```