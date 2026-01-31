FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级pip并安装Python依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p data/database data/exports logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["sh", "-c", "python scripts/init_database.py && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]