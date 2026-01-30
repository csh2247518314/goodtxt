#!/bin/bash

# GoodTxt Frontend 构建和部署脚本

echo "🚀 开始构建 GoodTxt 前端应用..."

# 检查Node.js版本
node_version=$(node --version 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Node.js 未安装或不可用"
    exit 1
fi

echo "✅ Node.js 版本: $node_version"

# 检查包管理器
if command -v pnpm >/dev/null 2>&1; then
    PKG_MANAGER="pnpm"
    echo "✅ 使用 pnpm 作为包管理器"
elif command -v npm >/dev/null 2>&1; then
    PKG_MANAGER="npm"
    echo "✅ 使用 npm 作为包管理器"
else
    echo "❌ 未找到包管理器"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm install --prefer-offline
else
    npm install
fi

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查类型检查
echo "🔍 进行类型检查..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm run type-check
else
    npm run type-check
fi

# 代码检查
echo "🔍 进行代码检查..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm run lint
else
    npm run lint
fi

# 构建应用
echo "🏗️  构建应用..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm run build
else
    npm run build
fi

if [ $? -ne 0 ]; then
    echo "❌ 应用构建失败"
    exit 1
fi

echo "✅ 应用构建完成"

# 检查构建结果
if [ -d "dist" ]; then
    echo "📁 构建文件已生成在 dist/ 目录"
    
    # 显示构建文件大小
    echo "📊 构建文件大小："
    du -sh dist/
    
    # 显示主要文件
    echo "📄 主要文件："
    ls -la dist/
else
    echo "❌ 未找到构建文件"
    exit 1
fi

echo ""
echo "🎉 GoodTxt 前端构建完成！"
echo ""
echo "📋 部署选项："
echo "1. 静态文件部署：将 dist/ 目录部署到任何 Web 服务器"
echo "2. Docker 部署："
echo "   docker build -t goodtxt-ui ."
echo "   docker run -p 3000:80 goodtxt-ui"
echo ""
echo "🛠️  本地预览："
if [ "$PKG_MANAGER" = "pnpm" ]; then
    echo "   pnpm run preview"
else
    echo "   npm run preview"
fi

echo ""
echo "✨ 享受 GoodTxt 多AI协同小说生成系统！"