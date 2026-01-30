#!/bin/bash

# GoodTxt 系统快速修复部署脚本
# 用于快速修复并部署系统

set -e

echo "🚀 GoodTxt 系统快速修复部署"
echo "=================================="

# 1. 检查Python环境
echo "🔍 检查Python环境..."
python3 --version

# 2. 初始化数据库
echo "🗄️ 初始化数据库..."
cd backend
python3 ../scripts/init_database.py

# 3. 安装前端依赖
echo "📦 安装前端依赖..."
cd ../frontend
npm install

# 4. 启动服务
echo "🚀 启动服务..."

# 创建日志目录
mkdir -p ../logs

# 启动后端（后台运行）
echo "启动后端服务..."
cd ../backend
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
echo "等待后端服务启动..."
sleep 5

# 检查后端服务
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 启动前端（后台运行）
echo "启动前端服务..."
cd ../frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
echo "等待前端服务启动..."
sleep 10

echo ""
echo "🎉 服务启动完成！"
echo "=================================="
echo "🌐 前端地址: http://localhost:5173"
echo "🔗 后端API: http://localhost:8000"
echo "📊 API文档: http://localhost:8000/docs"
echo ""
echo "📝 默认管理员账户:"
echo "   用户名: admin"
echo "   密码: admin123456"
echo ""
echo "📄 日志文件:"
echo "   后端日志: logs/backend.log"
echo "   前端日志: logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🔍 检查服务状态:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:5173"
echo ""

# 等待用户中断
echo "按 Ctrl+C 停止所有服务"
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo "✅ 服务已停止"; exit 0' INT

# 保持脚本运行
while true; do
    sleep 1
done
