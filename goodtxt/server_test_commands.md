# GoodTxt 服务器测试指令

## 🚀 服务器操作指南

### 1. 进入项目目录
```bash
cd /path/to/your/goodtxt
# 或者如果您在根目录克隆的：
cd goodtxt
```

### 2. 更新仓库到最新版本
```bash
# 拉取最新代码
git pull origin main

# 检查是否有更新
git status
```

### 3. 环境检查和验证
```bash
# 检查Docker是否安装
docker --version

# 检查Docker Compose是否安装
docker-compose --version

# 运行系统修复验证
python3 test_fixes.py
```

### 4. 启动系统（方式一：超级启动器）
```bash
# 交互式启动（推荐）
python3 super_launcher.py

# 选择选项：
# 1 - 完整部署（推荐）
# 2 - 快速启动
```

### 5. 启动系统（方式二：Docker Compose）
```bash
# 直接启动Docker服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 6. 系统验证
```bash
# 等待服务启动（约30秒）
sleep 30

# 检查后端API
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3002

# 检查数据库服务
docker-compose exec redis redis-cli ping
docker-compose exec chroma curl http://localhost:8000/api/v1/heartbeat
```

### 7. 访问系统
```bash
# 打开浏览器访问：
# 前端界面: http://localhost:3002
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs

# 默认登录信息：
# 用户名: admin
# 密码: admin123456
```

### 8. 常用管理命令
```bash
# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 重建并启动（用于修改配置后）
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 查看实时日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 清理Docker资源（谨慎使用）
docker system prune -a

# 备份数据库
docker-compose exec backend sqlite3 data/database/goodtxt.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"
```

### 9. 配置AI API密钥（可选）
```bash
# 编辑docker-compose.yml文件
nano docker-compose.yml

# 在backend服务的environment部分添加至少一个API密钥：
# - SILICONFLOW_API_KEY=your_api_key_here
# - DEEPSEEK_API_KEY=your_api_key_here
# - QWEN_API_KEY=your_api_key_here
# - MINIMAX_API_KEY=your_api_key_here

# 重启服务应用配置
docker-compose restart backend
```

### 10. 故障排除
```bash
# 检查端口占用
netstat -tulpn | grep -E ":(8000|3002|6379|8001)"

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 查看Docker容器资源使用
docker stats

# 生成诊断报告
python3 super_launcher.py --check > diagnosis.log 2>&1
```

### 11. 性能监控
```bash
# 监控服务状态（实时）
python3 super_launcher.py --monitor

# 快速检查
python3 super_launcher.py --quick-check

# 检查所有服务健康状态
curl -s http://localhost:8000/health | jq .
```

## 🔧 快速测试脚本

创建快速测试脚本：
```bash
cat > quick_test.sh << 'EOF'
#!/bin/bash
echo "🚀 GoodTxt 快速测试开始..."

# 更新代码
echo "1. 更新代码..."
git pull origin main

# 检查Docker
echo "2. 检查Docker..."
docker --version || exit 1
docker-compose --version || exit 1

# 启动服务
echo "3. 启动服务..."
docker-compose up -d

# 等待启动
echo "4. 等待服务启动..."
sleep 30

# 验证服务
echo "5. 验证服务..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

echo "6. 访问地址："
echo "   前端: http://localhost:3002"
echo "   后端: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"

echo "🎉 测试完成！"
EOF

chmod +x quick_test.sh
```

执行快速测试：
```bash
./quick_test.sh
```

## 📝 注意事项

1. **确保端口可用**：8000、3002、6379、8001端口不能被其他服务占用
2. **权限问题**：确保当前用户有Docker权限（`sudo usermod -aG docker $USER`）
3. **资源要求**：至少4GB内存，10GB磁盘空间
4. **网络连接**：确保服务器能访问互联网以下载Docker镜像
5. **API密钥**：如果不配置AI密钥，系统仍可启动但AI功能不可用

## 🆘 紧急恢复

如果系统完全崩溃：
```bash
# 1. 停止所有服务
docker-compose down

# 2. 清理Docker资源
docker system prune -a

# 3. 重新拉取代码
git reset --hard HEAD
git pull origin main

# 4. 重新启动
python3 super_launcher.py --quick
```