# GoodTxt 多AI协同小说生成系统

一个真正可用的多AI协同小说生成系统，支持多AI协作、完整工作流程和实时监控。

## 🎉 **最新更新 (v0.1.2)**

### 🔧 **重要修复**
- ✅ **后端启动问题已修复** - 不再出现语法错误
- ✅ **演示登录已移除** - 界面更简洁专业
- ✅ **注册功能已修复** - 前后端完美配合
- ✅ **数据库代码已优化** - 支持完整用户管理

### 📋 **修复文件**
- `backend/src/auth/auth_manager.py` - 修复重复代码
- `frontend/src/pages/LoginPage.tsx` - 移除演示登录
- `frontend/src/services/api.ts` - 修复API路由
- `backend/requirements.txt` - 添加必要依赖

**🌟 系统现在完全可用，无需任何额外配置！**

## ⚡ 一键安装

### 最简单的安装方式

**适用于任何全新服务器或本地环境：**

#### 方式1：直接执行（推荐）

```bash
# 下载并运行安装脚本
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
```

#### 方式2：手动下载

```bash
# 1. 下载安装脚本
wget https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh

# 2. 给执行权限并运行
chmod +x install.sh
./install.sh
```

这个脚本将自动：
- ✅ 检测操作系统并安装必要的依赖（Git、Python、Docker）
- ✅ 克隆项目到本地
- ✅ 设置权限
- ✅ 启动系统
- ✅ **智能检测环境，自动显示正确的访问地址（公网IP或localhost）**

## 📋 系统要求

### 最低要求
- **操作系统**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+), macOS, Windows 10+
- **内存**: 4GB RAM (推荐 8GB+)
- **磁盘空间**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **内存**: 8GB+ RAM
- **磁盘空间**: 20GB+ SSD
- **CPU**: 4核心以上

## 🏗️ 系统架构说明

### 核心组件（Docker容器）

系统采用Docker容器化部署，包含以下组件：

1. **前端服务** (React)
   - 端口：3000
   - 功能：用户界面和交互

2. **后端服务** (Python FastAPI)
   - 端口：8000
   - 功能：API接口、逻辑处理

3. **数据库服务**
   - **SQLite**: 本地数据库（容器内）
   - **Redis**: 缓存和会话存储（容器内）
   - **ChromaDB**: 向量数据库（容器内）

4. **API文档服务**
   - 端口：8000/docs
   - 功能：自动生成的API文档

### 无需额外安装的组件

**以下组件完全由Docker容器管理，无需手动安装：**

- ❌ **Nginx**: 不需要，系统使用内置的路由机制
- ❌ **MySQL/PostgreSQL**: 不需要，使用SQLite作为主要数据库
- ❌ **独立的Redis服务**: 不需要，Redis在Docker容器内运行
- ❌ **独立的数据库服务**: 不需要，所有数据库都在容器内

**唯一需要的是：**
- ✅ **Docker**: 容器运行时环境
- ✅ **Docker Compose**: 容器编排工具

## 🔧 安装和部署

### 方式一：一键安装脚本（推荐）

一键安装脚本支持以下操作系统：
- Ubuntu/Debian
- CentOS/RHEL
- Fedora
- macOS

#### Ubuntu/Debian 系统
```bash
# 运行安装脚本（会自动安装Git、Python、Docker）
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
```

#### CentOS/RHEL 系统
```bash
# 同样的命令，脚本会自动检测系统类型
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
```

#### macOS 系统
```bash
# 在macOS上运行（需要先安装Homebrew）
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
```

### 方式二：手动安装

如果一键脚本无法运行，请按以下步骤手动安装：

#### 1. 安装依赖

**Ubuntu/Debian:**
```bash
# 更新系统
sudo apt update

# 安装必要软件
sudo apt install -y git curl wget python3 python3-pip

# 安装Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
# 安装必要软件
sudo yum install -y git curl wget python3 python3-pip

# 安装Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# 安装Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install git python3 docker
```

#### 2. 克隆项目
```bash
git clone https://github.com/csh2247518314/goodtxt.git
cd goodtxt
```

#### 3. 设置权限
```bash
chmod +x *.py *.sh
```

## 🚀 启动系统

### 方式一：智能启动器（推荐）

**自动引导式启动：**
```bash
python3 super_launcher.py
```

提供交互式界面，引导您完成整个部署过程：
- 自动环境检查和修复
- 服务启动和状态监控
- 配置指导和问题排查

### 方式二：快速启动

**一键快速启动：**
```bash
python3 super_launcher.py --quick
```

自动启动系统并验证所有服务是否正常运行。

### 方式三：手动启动

**传统Docker启动：**
```bash
# 1. 环境检查
python3 super_launcher.py --check

# 2. 启动服务
docker-compose up -d

# 3. 验证服务
python3 super_launcher.py --quick-check
```

### 方式四：自动部署

**适用于CI/CD或自动化环境：**
```bash
python3 super_launcher.py --auto
```

全自动部署模式，无交互运行。

## 🌐 访问系统

### 智能地址检测

系统具备智能环境检测功能，会自动判断运行环境并显示正确的访问地址：

**在本地开发环境：**
- 前端界面: http://localhost:3002
- 后端API: http://localhost:8000  
- API文档: http://localhost:8000/docs

**在服务器/云环境：**
- 前端界面: http://[您的公网IP]:3000
- 后端API: http://[您的公网IP]:8000
- API文档: http://[您的公网IP]:8000/docs

### 🔍 如何判断环境

系统启动后会显示：
```
🔍 检测访问环境...
✅ 检测到公网IP: 123.456.789.123

🌐 访问地址:
   前端: http://123.456.789.123:3000
   后端API: http://123.456.789.123:8000
   API文档: http://123.456.789.123:8000/docs
```

如果显示"localhost"，说明检测到本地环境。

## 🛠️ 工具使用指南

### 核心工具

| 工具 | 用途 | 使用场景 |
|------|------|----------|
| `install.sh` | 一键安装脚本 | 安装Docker和依赖（国内镜像源） |
| `super_launcher.py` | 超级启动器 | 整合所有功能的统一工具 |

### 超级启动器 (super_launcher.py)

```bash
# 交互式模式（推荐）
python3 super_launcher.py

# 自动模式
python3 super_launcher.py --auto
```

**功能特性:**
- 交互式界面：图形化引导，步骤清晰
- 环境自动检查：验证Docker、端口、文件等
- 自动修复：自动创建缺失的配置和目录
- 服务管理：启动、停止、重启服务
- 状态监控：实时显示服务健康状态

### 超级启动器功能 (super_launcher.py)

```bash
python3 super_launcher.py --check
```

**检查项目:**
- Docker环境验证
- 系统资源检查（内存、磁盘）
- 端口可用性（8000, 3000, 6379, 8001）
- 项目文件完整性
- 目录结构创建
- 配置文件生成

### 超级启动器监控功能 (super_launcher.py)

```bash
# 快速检查
python3 super_launcher.py --quick-check

# 交互式监控
python3 super_launcher.py --monitor

# 默认模式
python3 super_launcher.py --monitor
```

**监控功能:**
- 实时监控服务状态
- 响应时间监控
- Docker容器状态
- 交互式操作（重启、查看日志等）

## 🔧 配置管理

### 基础配置

系统默认配置支持无API密钥启动，AI功能将显示为不可用状态。

### AI功能配置（可选）

要启用AI功能，请编辑 `docker-compose.yml` 文件：

```bash
nano docker-compose.yml
```

在backend服务的environment部分添加API密钥：

```yaml
environment:
  # ... 其他环境变量 ...
  # AI API密钥 (至少配置一个)
  - SILICONFLOW_API_KEY=你的硅基流动API密钥
  - DEEPSEEK_API_KEY=你的DeepSeek API密钥
  - QWEN_API_KEY=你的通义千问API密钥
  - MINIMAX_API_KEY=你的MiniMax API密钥
```

然后重启服务：
```bash
docker-compose restart backend
```

### 环境变量配置

#### 必需配置（系统启动）
```yaml
# docker-compose.yml 中的 environment 部分
environment:
  # 应用配置
  - APP_NAME=GoodTxt
  - APP_VERSION=1.0.0
  - DEBUG=true
  - ENVIRONMENT=production
  
  # 数据库配置
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - SQLITE_DATABASE_URL=sqlite:///./data/database/goodtxt.db
  - CHROMA_HOST=chroma
  - CHROMA_PORT=8000
  
  # 安全配置
  - JWT_SECRET_KEY=your-super-secret-jwt-key
  - JWT_ALGORITHM=HS256
  - JWT_EXPIRE_HOURS=24
  
  # CORS配置
  - ALLOWED_ORIGINS=http://localhost:3002,http://127.0.0.1:3000
```

#### 可选配置（AI功能）
```yaml
environment:
  # AI API密钥 (至少配置一个)
  - SILICONFLOW_API_KEY=your_siliconflow_api_key
  - DEEPSEEK_API_KEY=your_deepseek_api_key
  - QWEN_API_KEY=your_qwen_api_key
  - MINIMAX_API_KEY=your_minimax_api_key
  
  # AI配置
  - AI_DEFAULT_COORDINATOR_MODEL=deepseek
  - AI_DEFAULT_WRITER_MODEL=qwen
  - AI_MAX_REQUESTS_PER_MINUTE=100
```

## 🔧 故障排除

### 🚨 常见问题及解决方案 (v0.1.2更新)

#### ✅ **已修复的问题**
如果您遇到以下问题，请使用最新版本（v0.1.2）：

1. **后端启动失败**
   - **问题**: 认证管理器重复代码定义
   - **解决**: ✅ 已在v0.1.2中修复

2. **前端演示登录**
   - **问题**: 不需要的演示登录功能
   - **解决**: ✅ 已在v0.1.2中移除

3. **注册功能失败**
   - **问题**: 前后端API路由不匹配
   - **解决**: ✅ 已在v0.1.2中修复

4. **JWT认证错误**
   - **问题**: 缺少必要的认证依赖
   - **解决**: ✅ 已在v0.1.2中添加

### 通用故障排除

#### 1. 权限问题

**问题**: `Permission denied` 错误

**解决方案**:
```bash
# 给脚本执行权限
chmod +x *.py *.sh

# 或者直接用Python运行
python3 super_launcher.py
```

#### 2. Python命令找不到

**问题**: `bash: python: command not found`

**解决方案**:
```bash
# 尝试不同命令
python3 --version
python --version

# 如果都失败，重新安装Python
# Ubuntu/Debian: sudo apt install python3 python3-pip
# macOS: brew install python3
```

#### 3. Docker权限问题

**问题**: `Got permission denied while trying to connect to the Docker daemon`

**解决方案**:
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录
newgrp docker

# 或者使用sudo运行
sudo docker-compose up -d
```

#### 4. 端口被占用

**问题**: `Port already in use` 错误

**解决方案**:
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# 关闭占用端口的进程
sudo kill -9 <PID>
```

#### 5. 服务启动失败

**问题**: `docker-compose up -d` 失败

**解决方案**:
```bash
# 1. 清理Docker资源
docker system prune -a

# 2. 检查配置文件语法
docker-compose config

# 3. 查看详细错误信息
docker-compose up

# 4. 重建镜像
docker-compose build --no-cache
```

#### 6. AI功能不可用

**问题**: AI代理数量为0，API调用失败

**解决方案**:
```bash
# 验证API密钥格式
echo $SILICONFLOW_API_KEY | wc -c  # 应该大于10

# 重启后端服务
docker-compose restart backend

# 检查网络连接
docker-compose exec backend ping api.deepseek.com
```

#### 7. Docker构建失败 - pnpm锁定文件不匹配

**问题**: `ERR_PNPM_OUTDATED_LOCKFILE` 错误

**解决方案**:

#### 方案1：简单Docker修复（推荐）
```bash
# 使用简单Docker构建修复脚本
bash simple_build_fix.sh
```

#### 方案2：前端依赖修复
```bash
# 使用前端依赖修复脚本（需要Node.js环境）
bash fix_frontend_deps.sh

# 或者手动修复
cd frontend
rm pnpm-lock.yaml node_modules
pnpm install
pnpm install --frozen-lockfile

# 重新构建
docker-compose build frontend
docker-compose up -d --build
```

### 诊断工具

运行诊断脚本获取详细信息：

```bash
# 生成诊断报告
python3 super_launcher.py --check > diagnosis.log 2>&1
docker-compose ps > status.log
docker-compose logs > logs.log
```

### 修复脚本

如果遇到安装问题，可以使用以下修复脚本：

#### 简单修复脚本
```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/simple_fix.sh -o simple_fix.sh && bash simple_fix.sh
```

#### 增强修复脚本
```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/quick_fix.sh -o quick_fix.sh && bash quick_fix.sh
```

#### Docker修复脚本
```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/docker_fix.sh -o docker_fix.sh && bash docker_fix.sh
```

#### 前端依赖修复脚本
```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/fix_frontend_deps.sh -o fix_frontend_deps.sh && bash fix_frontend_deps.sh
```

#### 简单Docker构建修复（推荐）
```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/simple_build_fix.sh -o simple_build_fix.sh && bash simple_build_fix.sh
```

## 📊 运维管理

### 日常监控

#### 1. 服务状态监控
```bash
# 实时监控
python3 super_launcher.py --monitor

# 快速检查
python3 super_launcher.py --quick-check

# 后台监控脚本
while true; do
    python3 super_launcher.py --quick-check
    sleep 30
done
```

#### 2. 日志管理
```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs --tail=100 backend

# 导出日志
docker-compose logs > system.log

# 日志轮转
docker-compose logs --since=24h > daily.log
```

#### 3. 性能监控
```bash
# Docker 资源使用
docker stats

# 系统资源监控
htop
df -h
free -h

# 网络监控
netstat -tulpn | grep -E ":(8000|3000|6379|8001)"
```

### 备份与恢复

#### 1. 数据备份
```bash
# 创建备份目录
mkdir -p backups/$(date +%Y%m%d)

# 备份数据库
docker-compose exec backend sqlite3 data/database/goodtxt.db ".backup backups/$(date +%Y%m%d)/goodtxt.db"

# 备份配置文件
cp docker-compose.yml backups/$(date +%Y%m%d)/

# 备份用户数据
tar -czf backups/$(date +%Y%m%d)/user_data.tar.gz data/
```

#### 2. 配置备份
```bash
# 备份所有配置
tar -czf goodtxt-config-$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    .env \
    config/ \
    scripts/
```

#### 3. 恢复数据
```bash
# 停止服务
docker-compose down

# 恢复数据库
docker-compose exec backend sqlite3 data/database/goodtxt.db ".restore backups/$(date +%Y%m%d)/goodtxt.db"

# 恢复配置
tar -xzf goodtxt-config-20240130.tar.gz

# 重启服务
docker-compose up -d
```

### 升级与维护

#### 1. 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 更新服务
docker-compose up -d

# 清理旧镜像
docker image prune -a
```

#### 2. 安全更新
```bash
# 更新 Docker 镜像
docker-compose pull

# 更新系统包（谨慎操作）
sudo apt update && sudo apt upgrade

# 检查安全漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image goodtxt-backend:latest
```

#### 3. 性能优化
```bash
# 清理 Docker 资源
docker system prune -a

# 优化数据库
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('data/database/goodtxt.db')
conn.execute('VACUUM')
conn.close()
"

# 重启所有服务
docker-compose restart
```

## 🚨 紧急恢复流程

### 服务完全崩溃
```bash
# 1. 停止所有服务
docker-compose down

# 2. 清理Docker资源
docker system prune -a

# 3. 备份现有数据
cp -r data/ data.backup.$(date +%Y%m%d)/

# 4. 重新初始化
python setup.py

# 5. 恢复配置
cp docker-compose.yml.backup docker-compose.yml

# 6. 重新启动
docker-compose up -d

# 7. 验证恢复
python3 super_launcher.py --quick
```

## 🔒 安全配置

### 网络安全

#### 1. 防火墙配置
```bash
# 仅开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw enable
```

#### 2. JWT密钥管理
```bash
# 生成强随机JWT密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 在生产环境中使用环境变量
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

#### 3. API密钥安全
```bash
# 使用密钥管理服务
# 或环境变量文件
echo "AI_DEEPSEEK_API_KEY=your_key_here" > .env.production
```

## 📈 性能优化

### 系统级优化

#### 1. Docker优化
```bash
# 创建Docker配置
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
EOF

# 重启Docker服务
sudo systemctl restart docker
```

#### 2. 系统参数优化
```bash
# 优化内核参数
echo 'net.core.somaxconn = 65535' | sudo tee -a /etc/sysctl.conf
echo 'vm.swappiness = 10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 增加文件描述符限制
echo '* soft nofile 65535' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65535' | sudo tee -a /etc/security/limits.conf
```

## 🎯 使用流程

### **快速开始**
1. **一键安装**: 
   ```bash
   curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
   ```

2. **智能启动**: 
   ```bash
   python3 super_launcher.py
   ```

3. **验证修复**: 
   ```bash
   python3 test_fixes.py
   ```

4. **访问系统**: 
   - 前端: http://localhost:3002
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

5. **登录系统**: 
   - 默认用户: admin / admin123456
   - 或注册新用户

### **系统验证**
运行修复验证脚本确认一切正常：
```bash
cd /workspace/goodtxt
python3 test_fixes.py
```

**期望结果**: 
- ✅ 后端语法测试通过
- ✅ 前端构建测试通过  
- ✅ Docker配置测试通过

## 📁 项目结构

```
goodtxt/
├── 🚀 super_launcher.py    # 超级启动器（整合所有功能）
├── 📖 README.md           # 项目说明（本文件）
├── 🐳 docker-compose.yml   # Docker配置
├── 📂 backend/            # 后端代码
├── 📂 frontend/           # 前端代码
├── 📂 config/             # 配置文件
├── 📂 data/               # 数据目录
└── 📂 logs/               # 日志目录
```

## 🎉 系统特性

✅ **一键安装** - 自动安装所有依赖，真正零配置  
✅ **智能环境检测** - 自动识别环境并显示正确的访问地址  
✅ **真实AI集成** - 支持DeepSeek、通义千问、MiniMax、硅基流动  
✅ **完整用户认证** - JWT令牌认证、用户管理  
✅ **数据库集成** - SQLite + Redis + ChromaDB 三层架构（全部在Docker内）  
✅ **多任务隔离** - 确保同时生成多本小说不会混淆  
✅ **实时监控** - WebSocket推送生成进度  
✅ **质量评估** - 自动评估小说章节质量  
✅ **完整工作流** - 从想法到完整小说的全流程  
✅ **容错设计** - 无API密钥也能启动系统  
✅ **无需额外服务** - 不需要安装Nginx、MySQL等额外服务  

## 📞 支持与帮助

### 获取帮助的渠道

1. **文档资源**:
   - 本文件 (README.md) - 完整使用指南

2. **诊断工具**:
   ```bash
   # 生成诊断报告
   python3 super_launcher.py --check > diagnosis.log 2>&1
   docker-compose ps > status.log
   docker-compose logs > logs.log
   ```

3. **社区支持**:
   - 项目 Issues
   - 技术讨论
   - 用户社区

### 反馈问题

当遇到问题时，请提供以下信息：

1. **系统环境**:
   ```bash
   uname -a
   docker --version
   python --version
   ```

2. **错误日志**:
   ```bash
   python3 super_launcher.py --check
   docker-compose logs > error.log
   ```

3. **配置信息**:
   ```bash
   docker-compose config
   ```

---

**一个真正能工作的一键安装小说生成系统！**

现在您可以通过以下命令在任何服务器上一键安装和启动GoodTxt系统：

```bash
curl -sSL https://raw.githubusercontent.com/csh2247518314/goodtxt/main/install.sh -o install.sh && bash install.sh
```

## 最新修复 (v0.1.1)

### 🔧 高优先级API修复
- ✅ 实现了完整的用户管理API（列表、角色更新、删除、统计）
- ✅ 实现了完整的配置管理API（系统配置、AI模型配置）
- ✅ 修复了前后端API不一致问题
- ✅ 完善了业务逻辑闭环
- ✅ 增强了错误处理和数据验证

### 📊 修复统计
- 新增API端点: 9个
- 新增支持方法: 11个
- 修改文件: 3个
- 逻辑闭环: 3个主要业务流程

### 🛡️ 安全性增强
- 严格的数据验证机制
- 管理员权限验证
- 参数白名单验证
- 完整的错误处理

## API文档更新

### 用户管理相关
- `GET /users` - 获取用户列表
- `PUT /users/{user_id}/role` - 更新用户角色
- `DELETE /users/{user_id}` - 删除用户
- `GET /users/{user_id}/stats` - 获取用户统计

### 配置管理相关
- `GET /config` - 获取系统配置
- `PUT /config` - 更新系统配置
- `GET /config/models` - 获取AI模型配置
- `PUT /config/models` - 更新AI模型配置
- `POST /config/reset` - 重置系统配置

### 版本历史更新

### v0.1.2 (当前版本)
- 🔧 修复后端启动失败问题
- 🗑️ 移除前端演示登录功能
- 🔗 统一前后端API路由
- 📦 添加JWT认证依赖包
- 💾 完善数据库初始化脚本
- 🧪 新增修复验证脚本
- 📖 创建详细使用指南文档

### v0.1.1
- 🔧 修复高优先级API缺失问题
- 👥 完善用户管理功能
- ⚙️ 实现配置管理系统
- 📊 增强系统监控功能
- 🛡️ 提升安全性和稳定性

## 🚀 **服务器快速更新指南**

### **已有GoodTxt系统快速更新到v0.1.2**

如果您已经安装了GoodTxt系统，可以快速更新到最新版本：

```bash
# 1. 进入项目目录
cd /path/to/your/goodtxt

# 2. 拉取最新代码
git pull origin main

# 3. 安装/更新依赖
uv pip install PyJWT python-jose[cryptography] passlib[bcrypt] fastapi uvicorn pydantic-settings

# 4. 验证修复
python3 test_fixes.py

# 5. 重启系统
python3 super_launcher.py --quick
```

### **一键更新脚本**

创建更新脚本：

```bash
cat > quick_update.sh << 'EOF'
#!/bin/bash
echo "🚀 GoodTxt v0.1.2 快速更新"

# 进入项目目录
cd /path/to/your/goodtxt || exit 1

echo "📥 拉取最新代码..."
git pull origin main

echo "📦 更新Python依赖..."
uv pip install PyJWT python-jose[cryptography] passlib[bcrypt] fastapi uvicorn pydantic-settings

echo "🧪 验证修复..."
python3 test_fixes.py

echo "🔄 重启系统..."
python3 super_launcher.py --quick

echo "✅ 更新完成！访问: http://localhost:3002"
EOF

chmod +x quick_update.sh
```

然后运行：
```bash
./quick_update.sh
```