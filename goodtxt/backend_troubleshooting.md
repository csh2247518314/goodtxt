# 后端服务故障诊断

## 🚨 后端服务无法启动诊断

从您的日志可以看到：
- ✅ 前端服务正常（3002端口可访问）
- ❌ 后端服务异常（8000端口无法连接）

## 🔍 诊断步骤

### 1. 检查Docker容器状态
```bash
# 查看所有容器状态
docker-compose ps

# 查看运行中的容器
docker ps

# 查看容器日志
docker-compose logs backend
```

### 2. 检查端口占用
```bash
# 检查8000端口占用情况
netstat -tulpn | grep :8000

# 检查所有相关端口
netstat -tulpn | grep -E ":(8000|3002|6379|8001)"
```

### 3. 检查后端容器启动日志
```bash
# 查看后端具体错误
docker-compose logs --tail=50 backend

# 如果容器没有运行，查看详细信息
docker-compose logs backend --no-color
```

### 4. 检查依赖服务
```bash
# 检查Redis是否启动
docker-compose ps redis

# 检查ChromaDB是否启动
docker-compose ps chroma

# 检查依赖服务日志
docker-compose logs redis
docker-compose logs chroma
```

### 5. 检查配置文件
```bash
# 验证docker-compose.yml语法
docker-compose config

# 检查是否有语法错误
```

### 6. 强制重建后端
```bash
# 停止服务
docker-compose down

# 重新构建后端镜像
docker-compose build backend --no-cache

# 只启动后端和依赖服务测试
docker-compose up -d redis chroma
sleep 10
docker-compose up -d backend
```

### 7. 查看详细错误信息
```bash
# 进入后端容器查看
docker-compose exec backend bash

# 或者直接运行后端命令查看错误
docker-compose run --rm backend python main.py
```

## 🔧 常见问题和解决方案

### 问题1：端口被占用
```bash
# 查找占用8000端口的进程
sudo lsof -i :8000

# 强制终止进程
sudo kill -9 <PID>
```

### 问题2：权限问题
```bash
# 检查文件权限
ls -la docker-compose.yml

# 检查用户Docker权限
groups $USER
```

### 问题3：依赖服务未启动
```bash
# 按顺序启动服务
docker-compose up -d redis
sleep 5
docker-compose up -d chroma
sleep 5
docker-compose up -d backend
```

### 问题4：配置错误
```bash
# 检查环境变量
docker-compose exec backend env | grep -E "(REDIS|CHROMA|JWT)"

# 验证数据库连接
docker-compose exec backend python -c "import sqlite3; print('SQLite OK')"
```

## 📋 请按顺序执行以下诊断命令

```bash
# 1. 查看容器状态
docker-compose ps

# 2. 查看后端日志
docker-compose logs backend --tail=30

# 3. 检查依赖服务
docker-compose ps redis chroma

# 4. 验证配置
docker-compose config

# 5. 重新启动
docker-compose down
docker-compose build backend --no-cache
docker-compose up -d redis chroma
sleep 10
docker-compose up -d backend
```

请先执行这些命令，然后将输出结果发送给我，我会根据具体的错误信息帮您解决。