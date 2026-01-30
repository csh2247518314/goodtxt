#!/bin/bash

# GoodTxt 快速部署测试脚本
# 使用方法：chmod +x quick_deploy.sh && ./quick_deploy.sh

set -e

echo "🚀 GoodTxt 快速部署测试脚本"
echo "================================"

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到docker-compose.yml文件"
    echo "请确保在GoodTxt项目根目录下运行此脚本"
    exit 1
fi

# 1. 更新仓库
echo "📥 1. 更新仓库到最新版本..."
git pull origin main
echo "✅ 仓库更新完成"

# 2. 环境检查
echo "🔍 2. 检查环境..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境正常"

# 3. 运行系统验证
echo "🧪 3. 运行系统验证..."
if [ -f "test_fixes.py" ]; then
    python3 test_fixes.py
else
    echo "⚠️  测试脚本不存在，跳过验证"
fi

# 4. 启动服务
echo "🚀 4. 启动Docker服务..."
docker-compose up -d

# 5. 等待服务启动
echo "⏳ 5. 等待服务启动（30秒）..."
sleep 30

# 6. 验证服务
echo "🔍 6. 验证服务状态..."

# 检查后端
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务异常，检查日志："
    docker-compose logs backend --tail=20
fi

# 检查前端
if curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常"
else
    echo "❌ 前端服务异常，检查日志："
    docker-compose logs frontend --tail=20
fi

# 检查Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis服务运行正常"
else
    echo "❌ Redis服务异常"
fi

# 检查ChromaDB
if curl -s http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB服务运行正常"
else
    echo "❌ ChromaDB服务异常"
fi

# 7. 显示访问信息
echo ""
echo "🎉 部署完成！"
echo "================================"
echo "📱 访问地址："
echo "   🌐 前端界面: http://localhost:3002"
echo "   🔧 后端API: http://localhost:8000"
echo "   📚 API文档: http://localhost:8000/docs"
echo ""
echo "👤 默认登录信息："
echo "   用户名: admin"
echo "   密码: admin123456"
echo ""
echo "🔧 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo "   监控状态: python3 super_launcher.py --monitor"
echo ""

# 8. 提供后续配置提示
echo "💡 后续配置提示："
if grep -q "SILICONFLOW_API_KEY=" docker-compose.yml; then
    echo "   要启用AI功能，请编辑 docker-compose.yml 添加API密钥："
    echo "   - SILICONFLOW_API_KEY=your_api_key"
    echo "   - DEEPSEEK_API_KEY=your_api_key"
    echo "   然后运行: docker-compose restart backend"
fi

echo ""
echo "🚀 享受您的AI小说创作之旅！"