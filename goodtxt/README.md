---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5f1e69799963e773cf8621112be64830
    PropagateID: 5f1e69799963e773cf8621112be64830
    ReservedCode1: 304502202e1650e0d148dbf308afd4aa21c10251d42c2b98100ea3a9270bb7ce5b8d357a022100b5a8d5ddef001ca4fc8623563cfc8c10c6dfc1b01bffb245d9702834dadf9041
    ReservedCode2: 304502207eaaa7c41b8841bcbc79279fbc0b6e1bab09e0e163039a4481ed500b533d1556022100ca9db6fe877705b551a40658d9e5c06cb8388a13e1db1d429903350a9feb3a8e
---

# GoodTxt - 多AI协同小说生成系统

<div align="center">
  <img src="https://img.shields.io/badge/Status-活跃-green" alt="Status">
  <img src="https://img.shields.io/badge/版本-v2.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-blue" alt="Python">
  <img src="https://img.shields.io/badge/React-18+-61dafb" alt="React">
  <img src="https://img.shields.io/badge/许可证-MIT-green" alt="License">
</div>

## 📖 项目简介

GoodTxt是一个基于多AI协同的智能小说生成系统，支持用户注册登录、项目管理、智能内容生成，质量监控等核心功能。系统采用前后端分离架构，提供完整的用户界面和RESTful API接口。

本系统已经过全面修复和优化，所有核心功能都可以正常使用，支持真实的用户数据持久化和完整的项目管理功能。

## ✨ 主要功能

### 核心功能
- 🔐 **用户认证系统**：注册、登录、JWT令牌管理
- 📚 **项目管理**：创建、编辑、删除小说项目
- 🤖 **AI写作助手**：智能生成小说章节内容
- 📊 **质量监控**：实时评估生成内容的质量
- 👥 **多代理协同**：多个AI模型协同工作
- 📈 **数据统计**：项目进度、章节统计、用户活动
- 💾 **数据持久化**：SQLite数据库永久保存用户数据

### 技术特性
- 🔄 **实时更新**：WebSocket实时通信
- 💾 **数据库存储**：SQLite + Redis + ChromaDB 三层架构
- 🔒 **安全认证**：JWT令牌 + 密码哈希
- 📱 **响应式设计**：支持移动端和桌面端
- 🛠 **易于部署**：Docker + 脚本自动化
- 🎯 **容错设计**：无API密钥也能启动系统

## 🏗 技术架构

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI框架**: Tailwind CSS + shadcn/ui
- **状态管理**: React Context + Hooks
- **路由**: React Router
- **HTTP客户端**: Axios
- **实时通信**: WebSocket

### 后端技术栈
- **框架**: FastAPI (Python 3.9+)
- **数据库**: SQLite (开发) + Redis (缓存) + ChromaDB (向量存储)
- **AI集成**: 多个AI模型接口 (DeepSeek, Qwen, MiniMax, SiliconFlow等)
- **认证**: JWT + Passlib
- **日志**: Structlog
- **API文档**: 自动生成的Swagger UI

### 数据库设计
```sql
-- 核心数据表
users          -- 用户信息
projects       -- 小说项目
chapters       -- 章节内容
user_tokens    -- 用户令牌
system_logs    -- 系统日志
quality_reports -- 质量报告
memory         -- AI记忆
agent_performance -- 代理性能
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- npm/pnpm
- Git
- Docker (推荐)

### 1. 克隆项目
```bash
git clone https://github.com/csh2247518314/goodtxt.git
cd goodtxt
```

### 2. 一键安装（推荐）
```bash
# 使用一键安装脚本（包含国内镜像源优化）
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh

# 或者下载后执行
chmod +x install.sh
./install.sh
```

### 3. 智能启动
```bash
# 使用超级启动器（推荐）
python3 super_launcher.py

# 选择完整部署模式
# 系统将自动：
# ✅ 环境检查和修复
# ✅ 数据库初始化
# ✅ 服务启动和验证
# ✅ 智能地址检测
```

### 4. 访问系统
- **前端地址**: http://localhost:3002 (Docker模式) 或 http://localhost:5173 (开发模式)
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🔑 默认账户

系统启动后会自动创建管理员账户：
- **用户名**: `admin`
- **密码**: `admin123456`

## 📋 详细部署指南

### 方式一：超级启动器（最智能）
```bash
python3 super_launcher.py

# 可用选项：
# 1. 完整部署 - 运行环境检查 + 启动服务
# 2. 快速启动 - 一键启动，跳过详细检查
# 3. 环境检查 - 仅检查环境，不启动服务
# 4. 服务监控 - 实时监控服务状态
# 5. 快速检查 - 检查当前服务状态
# 6. 环境检测 - 检测网络和IP信息
```

### 方式二：Docker部署（推荐）
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：本地开发部署
```bash
# 1. 初始化数据库（重要！）
python scripts/init_database.py

# 2. 后端部署
cd backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 前端部署（新终端）
cd frontend
npm install
npm run dev
```

### 方式四：快速修复部署
```bash
# 使用快速修复脚本
./quick_fix_deploy.sh

# 该脚本将：
# ✅ 检查Python环境
# ✅ 初始化数据库
# ✅ 安装前端依赖
# ✅ 启动后端和前端服务
```

## 🔧 环境配置

### 前端环境变量
```bash
# .env.development (开发环境)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=GoodTxt
VITE_DEBUG=true

# .env.production (生产环境)
VITE_API_BASE_URL=http://your-domain.com:8000
VITE_APP_NAME=GoodTxt
VITE_DEBUG=false
```

### 后端环境变量
```bash
# .env (可选)
AI_DEEPSEEK_API_KEY=your_key
AI_QWEN_API_KEY=your_key
AI_MINIMAX_API_KEY=your_key
AI_SILICONFLOW_API_KEY=your_key
SECURITY_JWT_SECRET=your_secret_key
```

## 📱 使用指南

### 1. 用户注册登录
1. 访问 http://localhost:3002 或 http://localhost:5173
2. 点击"立即注册"创建新账户
3. 或使用默认管理员账户登录：admin / admin123456

### 2. 项目管理
1. 登录后进入项目页面
2. 点击"创建项目"新建小说项目
3. 设置项目信息：
   - 📝 标题
   - 📚 类型（科幻、言情、悬疑、奇幻等）
   - 📏 长度（短篇、中篇、长篇、长篇）
   - 🎯 主题
   - 👥 目标读者

### 3. AI写作助手
1. 进入编辑器页面
2. 选择要编辑的项目
3. 使用"生成章节"功能
4. AI会根据项目设定生成内容

### 4. 质量监控
1. 查看"系统监控"页面
2. 监控AI代理状态
3. 查看生成质量报告
4. 分析项目进度统计

### 5. AI代理配置
支持的AI服务商：
- 🤖 **DeepSeek** - 强大的逻辑推理
- 🧠 **通义千问** - 优秀的中文创作
- ⚡ **MiniMax** - 快速响应
- 🌟 **硅基流动** - 多模型支持

配置API密钥以启用AI功能：
```bash
# 编辑 docker-compose.yml
AI_DEEPSEEK_API_KEY=your_deepseek_key
AI_QWEN_API_KEY=your_qwen_key
AI_MINIMAX_API_KEY=your_minimax_key
AI_SILICONFLOW_API_KEY=your_siliconflow_key
```

## 📁 项目结构

```
goodtxt/
├── frontend/                 # 前端React应用
│   ├── src/
│   │   ├── components/      # UI组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── contexts/       # React Context
│   │   └── hooks/          # 自定义Hooks
│   ├── .env.development    # 开发环境配置
│   ├── .env.production     # 生产环境配置
│   └── package.json
├── backend/                 # 后端FastAPI应用
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── auth/          # 认证模块
│   │   ├── database/      # 数据库模块
│   │   ├── ai/           # AI模型集成
│   │   ├── engine/       # 核心引擎
│   │   └── config/       # 配置管理
│   └── database/          # 数据库相关
├── scripts/                # 部署脚本
│   ├── init_database.py   # 数据库初始化
│   ├── deploy_check.py    # 部署检查
│   └── setup-database.py  # 数据库设置
├── data/                   # 数据目录
│   ├── database/         # SQLite数据库文件
│   ├── exports/          # 导出文件
│   └── chroma/          # ChromaDB数据
├── config/                # 配置文件
│   ├── nginx/           # Nginx配置
│   └── redis.conf       # Redis配置
├── monitoring/            # 监控配置
│   ├── prometheus.yml   # Prometheus配置
│   └── grafana/         # Grafana配置
├── docker-compose.yml     # Docker配置
├── super_launcher.py     # 超级启动器
├── quick_fix_deploy.sh   # 快速部署脚本
├── install.sh           # 一键安装脚本
└── README.md           # 项目说明文档
```

## 🛠 API接口

### 认证接口
```bash
POST /auth/login     # 用户登录
POST /auth/register  # 用户注册
GET  /auth/me       # 获取当前用户
```

### 项目接口
```bash
GET    /projects        # 获取项目列表
POST   /projects        # 创建项目
GET    /projects/{id}   # 获取项目详情
PUT    /projects/{id}   # 更新项目
DELETE /projects/{id}   # 删除项目
```

### 章节接口
```bash
GET  /projects/{id}/chapters    # 获取章节列表
POST /chapters/{id}/regenerate # 重新生成章节
PUT  /chapters/{id}            # 更新章节
GET  /chapters/{id}            # 获取章节详情
POST /chapters/{id}/quality     # 评估章节质量
```

### 系统接口
```bash
GET  /system/status    # 系统状态
GET  /system/metrics  # 系统指标
GET  /system/logs     # 系统日志
GET  /health          # 健康检查
GET  /agents          # AI代理状态
```

完整API文档：http://localhost:8000/docs

## 🐛 故障排除

### 常见问题

#### 1. 数据库初始化失败
```bash
# 检查Python环境
python3 --version

# 手动初始化数据库
python scripts/init_database.py

# 检查权限
chmod +x scripts/init_database.py
```

#### 2. 前端无法连接后端
```bash
# 确认后端服务启动
curl http://localhost:8000/health

# 检查API地址配置
cat frontend/.env.development

# 端口被占用
lsof -i :8000
kill -9 $(lsof -t -i:8000)
```

#### 3. 用户注册失败
```bash
# 检查数据库文件
ls -la data/database/

# 查看后端日志
tail -f logs/backend.log

# 手动检查数据库
sqlite3 data/database/goodtxt.db ".tables"
```

#### 4. Docker部署问题
```bash
# 清理Docker资源
docker system prune -a

# 重建镜像
docker-compose build --no-cache

# 查看详细错误
docker-compose up
```

#### 5. AI模型调用失败
```bash
# 配置API密钥
echo "AI_DEEPSEEK_API_KEY=your_key" >> .env

# 重启后端服务
docker-compose restart backend
```

### 调试模式
```bash
# 启用后端调试
cd backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# 启用前端调试
cd frontend
VITE_DEBUG=true npm run dev
```

### 日志查看
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log

# Docker日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📊 监控和维护

### 系统监控
- **健康检查**: GET /health
- **系统状态**: GET /system/status
- **性能指标**: GET /system/metrics
- **实时日志**: GET /system/logs
- **AI代理状态**: GET /agents

### 数据库维护
```bash
# 数据库备份
cp data/database/goodtxt.db data/database/goodtxt_backup_$(date +%Y%m%d).db

# 数据库清理
sqlite3 data/database/goodtxt.db "DELETE FROM system_logs WHERE created_at < datetime('now', '-30 days');"

# 数据统计
sqlite3 data/database/goodtxt.db "SELECT COUNT(*) FROM users;"
```

### 性能优化
- **数据库索引**: 已为所有查询字段创建索引
- **缓存策略**: 使用Redis缓存热点数据
- **API限流**: 内置请求频率限制
- **资源监控**: 实时CPU、内存使用监控

## 🔒 安全考虑

### 认证安全
- ✅ JWT令牌认证
- ✅ 密码哈希存储
- ✅ 登录失败锁定
- ✅ API密钥管理
- ✅ 密码长度验证（最少8字符）

### 数据安全
- ✅ SQL注入防护
- ✅ XSS防护
- ✅ CORS配置
- ✅ 输入验证
- ✅ 数据库加密

### 生产环境建议
- 更改默认JWT密钥
- 启用HTTPS
- 配置防火墙
- 定期安全更新
- 数据库加密
- 配置API限流

## 🎯 系统特性

✅ **一键安装** - 自动安装所有依赖，真正零配置  
✅ **智能环境检测** - 自动识别环境并显示正确的访问地址  
✅ **数据持久化** - 用户数据永久保存，重启不丢失  
✅ **数据库初始化** - 自动创建完整的数据库结构  
✅ **真实AI集成** - 支持DeepSeek、通义千问、MiniMax、硅基流动  
✅ **完整用户认证** - JWT令牌认证、用户管理  
✅ **数据库集成** - SQLite + Redis + ChromaDB 三层架构（全部在Docker内）  
✅ **多任务隔离** - 确保同时生成多本小说不会混淆  
✅ **实时监控** - WebSocket推送生成进度  
✅ **质量评估** - 自动评估小说章节质量  
✅ **完整工作流** - 从想法到完整小说的全流程  
✅ **容错设计** - 无API密钥也能启动系统  
✅ **无需额外服务** - 不需要安装Nginx、MySQL等额外服务  
✅ **超级启动器** - 智能管理所有操作  
✅ **国内镜像支持** - 优化国内网络环境安装  

## 📞 技术支持

### 获取帮助
- 🔍 查看本README文件获取详细指导
- 🐛 运行 `python3 super_launcher.py --check` 进行环境检查
- 📋 运行 `python3 test_fixes.py` 验证系统修复
- 💬 提交 Issue 报告问题

### 常用命令
```bash
# 环境检查
python3 super_launcher.py --check

# 快速启动
python3 super_launcher.py --quick

# 服务监控
python3 super_launcher.py --monitor

# 快速检查
python3 super_launcher.py --quick-check

# 验证修复
python3 test_fixes.py

# 数据库初始化
python scripts/init_database.py
```

### 常见资源
- **API文档**: http://localhost:8000/docs
- **GitHub仓库**: https://github.com/csh2247518314/goodtxt
- **问题反馈**: https://github.com/csh2247518314/goodtxt/issues

## 📈 版本历史

### v2.0.0 (2026-01-31)
- ✅ 全面修复用户数据持久化问题
- ✅ 修复前端API配置问题
- ✅ 完善数据库初始化流程
- ✅ 增强系统启动脚本
- ✅ 添加超级启动器
- ✅ 优化国内网络安装
- ✅ 完善错误处理机制

### v1.0.0
- ✅ 基础框架搭建
- ✅ 前后端分离架构
- ✅ 基础用户认证
- ✅ AI模型集成框架

## 🤝 贡献指南

欢迎提交Issues和Pull Requests！

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/csh2247518314/goodtxt.git

# 安装依赖
pip install -r backend/requirements.txt
cd frontend && npm install

# 运行开发服务器
python3 super_launcher.py
```

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有为GoodTxt项目做出贡献的开发者！

---

<div align="center">
  <p>Built with ❤️ by GoodTxt Team</p>
  <p>版本 v2.0.0 | 最后更新 2026-01-31</p>
  <p>🎉 数据持久化问题已修复 | 🎯 完全可用</p>
  <p>🚀 智能启动器 | ⚡ 一键部署</p>
</div>
