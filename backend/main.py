"""
多AI协同小说生成系统 - 后端服务启动
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    import uvicorn
    from src.api.main import app
    
    # 启动FastAPI应用
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False  # 在Docker环境中禁用reload
    )