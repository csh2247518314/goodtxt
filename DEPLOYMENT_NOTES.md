# GoodTxt 项目部署说明

## 修复摘要

我们对 GoodTxt 多AI协同小说生成系统进行了以下关键修复和改进：

### 1. 安全性修复
- **JWT密钥安全**：在 `backend/src/config/settings.py` 中添加了密钥长度验证（至少32字符）
- **默认管理员账户**：移除了自动创建默认管理员账户的功能，改为通过环境变量控制
- **密码哈希**：使用内置PBKDF2算法替代外部依赖，提高安全性

### 2. 部署改进
- **Docker Compose**：创建了完整的 `docker-compose.yml` 文件，支持一键部署
- **Dockerfiles**：为前后端分别创建了Dockerfile
- **环境配置**：更新了 `.env` 文件模板，包含安全配置建议

### 3. 依赖优化
- **requirements.txt**：更新了依赖版本，提高稳定性
- **认证模块**：重构了认证管理器，减少对外部库的依赖

## 部署步骤

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd goodtxt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置安全密钥和其他配置
```

### 2. Docker部署（推荐）
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 3. 手动部署
```bash
# 启动后端
cd backend
pip install -r requirements.txt
python scripts/init_database.py
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 启动前端
cd frontend
npm install
npm run dev
```

## 安全建议

1. **生产环境必须**：
   - 更改默认JWT密钥（至少32字符随机字符串）
   - 不要使用默认管理员账户
   - 配置HTTPS
   - 设置防火墙规则

2. **AI API密钥**：
   - 至少配置一个AI服务提供商的API密钥
   - 定期轮换API密钥
   - 限制API调用频率

## 文件变更清单

- `backend/src/config/settings.py` - 添加JWT密钥长度验证
- `backend/src/auth/auth_manager.py` - 重构认证模块，移除默认管理员创建
- `docker-compose.yml` - 新增Docker Compose配置
- `backend/Dockerfile` - 新增后端Dockerfile
- `frontend/Dockerfile` - 新增前端Dockerfile
- `backend/requirements.txt` - 更新依赖版本
- `.env` - 新增安全环境配置模板
- `README.md` - 更新部署说明和安全建议