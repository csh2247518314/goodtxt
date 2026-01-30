# GoodTxt 手动安装指南

如果一键安装脚本遇到问题，请按以下步骤手动安装：

## 1. 安装基础依赖

### Ubuntu/Debian 系统
```bash
# 更新系统
sudo apt update

# 安装Git、Python、Docker
sudo apt install -y git python3 python3-pip docker.io

# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### CentOS/RHEL 系统
```bash
# 安装Git、Python、Docker
sudo yum install -y git python3 python3-pip docker

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

## 2. 克隆项目

```bash
git clone https://github.com/csh2247518314/goodtxt.git
cd goodtxt
```

## 3. 设置权限

```bash
chmod +x *.py *.sh
```

## 4. 安装Python依赖

```bash
python3 -m pip install --user psutil requests
```

## 5. 启动系统

```bash
# 智能启动器（推荐）
python3 launcher.py

# 或者快速启动
python3 quick_start.py

# 或者直接Docker启动
docker-compose up -d
```

## 6. 访问系统

启动成功后访问：
- **前端**: http://localhost:3002
- **后端**: http://localhost:8000  
- **文档**: http://localhost:8000/docs

## 常见问题解决

### Python命令找不到
```bash
# 检查Python安装
which python3
python3 --version

# 如果没有python3
sudo apt install python3 python3-pip
```

### Docker权限问题
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker

# 或使用sudo运行
sudo docker-compose up -d
```

### Docker服务未启动
```bash
# Ubuntu/Debian
sudo systemctl start docker
sudo systemctl enable docker

# CentOS/RHEL
sudo systemctl start docker
sudo systemctl enable docker
```

### 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# 杀死占用端口的进程
sudo kill -9 <PID>
```

### Git克隆失败
```bash
# 检查网络连接
ping github.com

# 如果网络有问题，尝试使用镜像源
git clone https://ghproxy.com/https://github.com/csh2247518314/goodtxt.git
```

## 联系支持

如果仍然遇到问题，请运行诊断脚本：

```bash
python3 env_checker.py > diagnosis.log 2>&1
```

并查看生成的 `diagnosis.log` 文件。