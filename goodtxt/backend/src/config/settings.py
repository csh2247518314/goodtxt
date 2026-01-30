"""
多AI协同小说生成系统配置管理

处理所有配置相关的功能，包括环境变量加载、
配置验证和动态配置管理。
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecurityConfig(BaseSettings):
    """安全配置"""
    jwt_secret: str = Field(default="your-super-secret-jwt-key-change-in-production")
    jwt_secret_key: str = Field(default="your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    token_expire_hours: int = Field(default=24)
    bcrypt_rounds: int = Field(default=12)
    
    def __init__(self, **data):
        super().__init__(**data)
        # 检查生产环境安全性
        if self.jwt_secret == "your-super-secret-jwt-key-change-in-production":
            import warnings
            warnings.warn("警告：使用默认JWT密钥，存在安全风险！", UserWarning)
        
        # 环境变量检查
        if os.getenv('ENVIRONMENT') == 'production' and self.jwt_secret == "your-super-secret-jwt-key-change-in-production":
            raise ValueError("生产环境必须设置强JWT密钥！")
    
    # API密钥管理
    api_key_header: str = Field(default="X-API-Key")
    
    # CORS设置
    cors_origins: list = Field(default=["http://localhost:3002", "http://localhost:5173"])
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_")


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    redis_url: str = Field(default="redis://redis:6379/0")
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    
    sqlite_path: str = Field(default="./data/database/goodtxt.db")
    
    chroma_persist_directory: str = Field(default="./data/chroma")
    chroma_host: str = Field(default="chroma")
    chroma_port: int = Field(default=8000)
    
    model_config = SettingsConfigDict(env_prefix="DB_")


class AIModelConfig(BaseSettings):
    """AI模型API配置"""
    # 硅基流动
    siliconflow_api_key: Optional[str] = Field(default=None)
    siliconflow_base_url: str = Field(default="https://api.siliconflow.cn")
    
    # DeepSeek
    deepseek_api_key: Optional[str] = Field(default=None)
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    
    # 通义千问
    qwen_api_key: Optional[str] = Field(default=None)
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    
    # MiniMax
    minimax_api_key: Optional[str] = Field(default=None)
    minimax_base_url: str = Field(default="https://api.minimax.chat")
    
    # 默认模型分配
    default_coordinator_model: str = Field(default="deepseek")
    default_writer_model: str = Field(default="qwen")
    default_editor_model: str = Field(default="qwen")
    default_monitor_model: str = Field(default="minimax")
    
    # 请求限制
    max_requests_per_minute: int = Field(default=100)
    max_tokens_per_request: int = Field(default=4096)
    
    model_config = SettingsConfigDict(env_prefix="AI_")


class AppConfig(BaseSettings):
    """应用配置"""
    app_name: str = Field(default="Multi-AI Novel Generator")
    app_version: str = Field(default="0.1.0")
    app_debug: bool = Field(default=False)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    
    # 前端URL
    frontend_url: str = Field(default="http://localhost:3002")
    
    # 日志配置
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_file: Optional[str] = Field(default=None)
    
    # 监控配置
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    
    # 限流配置
    rate_limit_requests_per_minute: int = Field(default=60)
    rate_limit_tokens_per_minute: int = Field(default=10000)
    
    # 缓存配置
    cache_ttl: int = Field(default=3600)
    cache_max_size: int = Field(default=1000)
    
    # 文件配置
    upload_max_size: int = Field(default=50)  # MB
    export_formats: list = Field(default=["txt", "pdf", "docx"])
    
    model_config = SettingsConfigDict(env_prefix="APP_")


class Settings:
    """应用设置管理"""
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.ai = AIModelConfig()
        self.app = AppConfig()
        self.security = SecurityConfig()
        
    def validate_config(self) -> Dict[str, Any]:
        """验证配置完整性"""
        issues = []
        
        # 检查必要的API密钥
        api_keys = [
            ("siliconflow_api_key", self.ai.siliconflow_api_key),
            ("deepseek_api_key", self.ai.deepseek_api_key),
            ("qwen_api_key", self.ai.qwen_api_key),
            ("minimax_api_key", self.ai.minimax_api_key)
        ]
        
        configured_keys = []
        for name, key in api_keys:
            if key:
                configured_keys.append(name)
        
        if not configured_keys:
            issues.append("至少需要配置一个AI模型API密钥")
        
        # 检查JWT密钥
        if (self.security.jwt_secret == "your-super-secret-jwt-key-change-in-production" or 
            self.security.jwt_secret_key == "your-super-secret-jwt-key-change-in-production"):
            issues.append("JWT密钥未更改，存在严重安全风险！生产环境必须更改此密钥")
        
        # 检查数据库连接配置
        if self.db.redis_url.startswith("redis://redis"):
            # 在开发环境中这是正常的
            pass
        elif not self.db.redis_url.startswith("redis://"):
            issues.append("Redis URL格式不正确")
        
        # 检查目录权限
        data_dir = Path(self.ai.chroma_persist_directory).parent
        if not data_dir.exists():
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"无法创建数据目录: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config_summary": {
                "ai_models_configured": len(configured_keys),
                "database_type": "redis + sqlite + chroma",
                "monitoring_enabled": self.app.metrics_enabled,
                "security_level": "high" if self.security.jwt_secret != "your-super-secret-jwt-key-change-in-production" else "low"
            }
        }
    
    def get_ai_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取特定AI模型配置"""
        configs = {
            "siliconflow": {
                "api_key": self.ai.siliconflow_api_key,
                "base_url": self.ai.siliconflow_base_url,
                "model_type": "siliconflow"
            },
            "deepseek": {
                "api_key": self.ai.deepseek_api_key,
                "base_url": self.ai.deepseek_base_url,
                "model_type": "openai_compatible"
            },
            "qwen": {
                "api_key": self.ai.qwen_api_key,
                "base_url": self.ai.qwen_base_url,
                "model_type": "qwen"
            },
            "minimax": {
                "api_key": self.ai.minimax_api_key,
                "base_url": self.ai.minimax_base_url,
                "model_type": "minimax"
            }
        }
        return configs.get(model_name)
    
    def get_environment_info(self) -> Dict[str, str]:
        """获取环境信息"""
        return {
            "app_name": self.app.app_name,
            "app_version": self.app.app_version,
            "debug": self.app.app_debug,
            "log_level": self.app.log_level,
            "ai_models_configured": str(len([
                k for k in [
                    self.ai.siliconflow_api_key,
                    self.ai.deepseek_api_key,
                    self.ai.qwen_api_key,
                    self.ai.minimax_api_key
                ] if k
            ]))
        }


# 全局设置实例
settings = Settings()


def load_settings_from_file(env_file: str = ".env") -> None:
    """从文件加载环境变量"""
    try:
        from dotenv import load_dotenv
        
        if Path(env_file).exists():
            load_dotenv(env_file)
            # 重新初始化设置以加载新的环境变量
            global settings
            settings = Settings()
    except ImportError:
        # 如果没有安装python-dotenv，则跳过
        pass


def get_settings() -> Settings:
    """获取应用设置"""
    return settings


def create_env_template():
    """创建环境变量模板文件"""
    template = """# GoodTxt 多AI协同小说生成系统环境配置

# ===========================================
# AI模型API配置
# ===========================================

# 硅基流动 API (推荐用于DeepSeek)
AI_SILICONFLOW_API_KEY=your_siliconflow_api_key_here

# DeepSeek API
AI_DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 通义千问 API
AI_QWEN_API_KEY=your_qwen_api_key_here

# MiniMax API
AI_MINIMAX_API_KEY=your_minimax_api_key_here

# ===========================================
# 数据库配置
# ===========================================

# Redis配置
DB_REDIS_HOST=localhost
DB_REDIS_PORT=6379
DB_REDIS_DB=0

# SQLite数据库文件
DB_SQLITE_PATH=../data/database/goodtxt.db

# ChromaDB配置
DB_CHROMA_PERSIST_DIRECTORY=../data/chroma

# ===========================================
# 安全配置
# ===========================================

# JWT密钥 (生产环境必须更改)
SECURITY_JWT_SECRET=your-super-secret-jwt-key-change-in-production

# CORS允许的源 (多个用逗号分隔)
SECURITY_CORS_ORIGINS=http://localhost:3002,http://localhost:5173

# ===========================================
# 应用配置
# ===========================================

# 应用设置
APP_APP_DEBUG=false
APP_APP_HOST=0.0.0.0
APP_APP_PORT=8000

# 前端URL
APP_FRONTEND_URL=http://localhost:3002

# 日志设置
APP_LOG_LEVEL=INFO

# 监控设置
APP_METRICS_ENABLED=true

# 限流设置
APP_RATE_LIMIT_REQUESTS_PER_MINUTE=60
APP_RATE_LIMIT_TOKENS_PER_MINUTE=10000
"""
    
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(template)
    
    print("环境变量模板文件已创建: .env.template")
    print("请复制此文件为 .env 并填入您的API密钥")