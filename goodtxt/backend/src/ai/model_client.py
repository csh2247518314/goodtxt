"""
大模型API集成模块
支持多个国内AI服务商
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import aiohttp
import structlog

from ..config.settings import get_settings


class AIModelType(Enum):
    """AI模型类型"""
    COORDINATOR = "coordinator"
    WRITER = "writer"
    EDITOR = "researcher"
    MONITOR = "monitor"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str
    timestamp: Optional[datetime] = None


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None


class AIModelClient:
    """AI模型客户端"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = structlog.get_logger()
        
        # 创建持久化的客户端会话
        self.session = None
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1.0
        self.backoff_factor = 2.0
    
    async def _ensure_session(self):
        """确保有有效的客户端会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """关闭客户端会话"""
        if self.session and not self.session.closed:
            await self.session.close()
        
    async def chat(
        self, 
        messages: List[ChatMessage], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """发送聊天请求"""
        if not self.config.enabled:
            return ChatResponse(
                content="",
                model=self.config.name,
                tokens_used=0,
                response_time=0,
                success=False,
                error_message="模型未启用"
            )
        
        start_time = datetime.now()
        
        for attempt in range(self.max_retries + 1):
            try:
                await self._ensure_session()
                
                # 准备消息格式
                formatted_messages = []
                
                if system_prompt:
                    formatted_messages.append({
                        "role": "system",
                        "content": system_prompt
                    })
                
                for msg in messages:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                # 根据服务商准备请求
                request_data = self._prepare_request(formatted_messages, **kwargs)
                
                response = await self.session.post(
                    self.config.base_url,
                    headers=self._get_headers(),
                    json=request_data,
                    timeout=30
                )
                
                if response.status == 200:
                    result = await response.json()
                    return self._parse_response(result, start_time)
                else:
                    error_text = await response.text()
                    self.logger.warning(f"API请求失败 (尝试 {attempt + 1}): {response.status} - {error_text}")
                    
                    # 如果是最后一次尝试，返回错误
                    if attempt == self.max_retries:
                        return ChatResponse(
                            content="",
                            model=self.config.name,
                            tokens_used=0,
                            response_time=(datetime.now() - start_time).total_seconds(),
                            success=False,
                            error_message=f"API请求失败: {response.status}"
                        )
            
            except asyncio.TimeoutError:
                self.logger.warning(f"请求超时 (尝试 {attempt + 1})")
                
                if attempt == self.max_retries:
                    return ChatResponse(
                        content="",
                        model=self.config.name,
                        tokens_used=0,
                        response_time=30,
                        success=False,
                        error_message="请求超时"
                    )
            
            except Exception as e:
                self.logger.error(f"请求异常 (尝试 {attempt + 1}): {e}")
                
                if attempt == self.max_retries:
                    return ChatResponse(
                        content="",
                        model=self.config.name,
                        tokens_used=0,
                        response_time=(datetime.now() - start_time).total_seconds(),
                        success=False,
                        error_message=f"请求异常: {str(e)}"
                    )
            
            # 等待重试（除了最后一次）
            if attempt < self.max_retries:
                delay = self.retry_delay * (self.backoff_factor ** attempt)
                await asyncio.sleep(delay)
        
        # 理论上不会到达这里
        return ChatResponse(
            content="",
            model=self.config.name,
            tokens_used=0,
            response_time=0,
            success=False,
            error_message="重试机制异常"
        )
    
    def _prepare_request(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """准备请求数据"""
        if self.config.provider == "deepseek":
            return {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": False
            }
        elif self.config.provider == "qwen":
            return {
                "model": self.config.model,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature)
                }
            }
        elif self.config.provider == "minimax":
            return {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature)
            }
        elif self.config.provider == "siliconflow":
            return {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": False
            }
        else:
            raise ValueError(f"不支持的AI服务商: {self.config.provider}")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if self.config.provider in ["qwen"]:
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
    
    def _parse_response(self, result: Dict[str, Any], start_time: datetime) -> ChatResponse:
        """解析响应"""
        try:
            response_time = (datetime.now() - start_time).total_seconds()
            
            if self.config.provider == "deepseek":
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
            elif self.config.provider == "qwen":
                content = result["output"]["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
            elif self.config.provider == "minimax":
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
            elif self.config.provider == "siliconflow":
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
            else:
                content = result.get("content", "")
                tokens_used = 0
            
            return ChatResponse(
                content=content,
                model=self.config.name,
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"解析响应失败: {e}")
            return ChatResponse(
                content="",
                model=self.config.name,
                tokens_used=0,
                response_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error_message=f"解析响应失败: {str(e)}"
            )


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        self.clients: Dict[str, AIModelClient] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        
        # 初始化模型配置
        self._init_model_configs()
        
    def _init_model_configs(self):
        """初始化模型配置"""
        ai_settings = self.settings.ai
        
        # 协调者模型
        if ai_settings.deepseek_api_key:
            self.model_configs["coordinator"] = ModelConfig(
                name="DeepSeek协调者",
                provider="deepseek",
                api_key=ai_settings.deepseek_api_key,
                base_url=ai_settings.deepseek_base_url,
                model="deepseek-chat",
                max_tokens=4096,
                temperature=0.3
            )
        
        # 作者模型
        if ai_settings.qwen_api_key:
            self.model_configs["writer"] = ModelConfig(
                name="Qwen作者",
                provider="qwen",
                api_key=ai_settings.qwen_api_key,
                base_url=ai_settings.qwen_base_url,
                model="qwen-plus",
                max_tokens=4096,
                temperature=0.7
            )
        
        # 编辑模型
        if ai_settings.qwen_api_key:
            self.model_configs["editor"] = ModelConfig(
                name="Qwen编辑",
                provider="qwen",
                api_key=ai_settings.qwen_api_key,
                base_url=ai_settings.qwen_base_url,
                model="qwen-plus",
                max_tokens=4096,
                temperature=0.5
            )
        
        # 监控模型
        if ai_settings.minimax_api_key:
            self.model_configs["monitor"] = ModelConfig(
                name="MiniMax监控",
                provider="minimax",
                api_key=ai_settings.minimax_api_key,
                base_url=ai_settings.minimax_base_url,
                model="abab6.5s-chat",
                max_tokens=2048,
                temperature=0.2
            )
        
        # 创建客户端
        for name, config in self.model_configs.items():
            self.clients[name] = AIModelClient(config)
    
    async def chat_with_model(
        self, 
        model_type: AIModelType, 
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """与指定模型聊天"""
        model_name = model_type.value
        
        if model_name not in self.clients:
            return ChatResponse(
                content="",
                model=model_name,
                tokens_used=0,
                response_time=0,
                success=False,
                error_message=f"模型 {model_name} 未配置"
            )
        
        messages = [ChatMessage(role="user", content=prompt)]
        return await self.clients[model_name].chat(messages, system_prompt, **kwargs)
    
    def update_model_config(self, model_type: AIModelType, config: ModelConfig):
        """更新模型配置"""
        model_name = model_type.value
        self.model_configs[model_name] = config
        self.clients[model_name] = AIModelClient(config)
        self.logger.info(f"更新模型配置: {model_name}")
    
    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """获取模型状态"""
        status = {}
        for name, config in self.model_configs.items():
            status[name] = {
                "name": config.name,
                "provider": config.provider,
                "model": config.model,
                "enabled": config.enabled,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
        return status
    
    def test_model_connection(self, model_type: AIModelType) -> Dict[str, Any]:
        """测试模型连接"""
        model_name = model_type.value
        
        if model_name not in self.clients:
            return {
                "success": False,
                "error": f"模型 {model_name} 未配置"
            }
        
        client = self.clients[model_name]
        test_messages = [ChatMessage(role="user", content="你好，请回复一个简单的问候。")]
        
        try:
            # 使用 asyncio.run() 替代手动创建事件循环
            response = asyncio.run(
                client.chat(test_messages, "你是一个助手")
            )
            
            return {
                "success": response.success,
                "response_time": response.response_time,
                "error": response.error_message,
                "model_used": response.model
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"连接测试失败: {str(e)}"
            }
    
    async def close(self):
        """关闭客户端会话"""
        await self._close_session()


# 全局AI模型管理器实例
ai_model_manager = AIModelManager()