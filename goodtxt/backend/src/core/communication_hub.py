"""
通信中心模块

负责AI智能体之间的消息传递和通信协调
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

import structlog

from ..core.framework import AgentMessage


class MessageType(Enum):
    """消息类型枚举"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    QUALITY_ALERT = "quality_alert"
    MEMORY_UPDATE = "memory_update"
    COORDINATION_REQUEST = "coordination_request"
    HEARTBEAT = "heartbeat"


class CommunicationHub:
    """通信中心"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        
        # 注册的智能体
        self.agents: Dict[str, Any] = {}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        
        # 消息队列
        self.message_queue: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self.message_history: deque = deque(maxlen=1000)
        
        # 订阅机制
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)  # event_type -> agent_ids
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # 统计信息
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0
        }
        
        # 启动消息处理任务
        self.running = False
        
        self.logger.info("Communication Hub initialized")
    
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """注册智能体"""
        self.agents[agent_id] = agent
        self.agent_status[agent_id] = {
            "status": "registered",
            "last_seen": datetime.now(),
            "message_count": 0,
            "error_count": 0
        }
        
        self.logger.info(f"Agent registered: {agent_id}")
    
    def subscribe(self, agent_id: str, event_type: str) -> None:
        """订阅事件"""
        self.subscribers[event_type].add(agent_id)
        self.logger.debug(f"Agent {agent_id} subscribed to {event_type}")
    
    def unsubscribe(self, agent_id: str, event_type: str) -> None:
        """取消订阅"""
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(agent_id)
            self.logger.debug(f"Agent {agent_id} unsubscribed from {event_type}")
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """注册消息处理器"""
        self.message_handlers[message_type].append(handler)
        self.logger.debug(f"Message handler registered for {message_type}")
    
    async def start(self) -> None:
        """启动通信中心"""
        self.running = True
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._heartbeat_monitor())
        self.logger.info("Communication Hub started")
    
    async def stop(self) -> None:
        """停止通信中心"""
        self.running = False
        self.logger.info("Communication Hub stopped")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""
        try:
            # 验证消息
            if not self._validate_message(message):
                self.logger.error(f"Invalid message from {message.sender_id}")
                return False
            
            # 更新统计
            self.stats["messages_sent"] += 1
            
            # 添加到历史记录
            self.message_history.append({
                "timestamp": datetime.now().isoformat(),
                "sender": message.sender_id,
                "receiver": message.receiver_id,
                "type": message.message_type,
                "priority": message.priority
            })
            
            # 放入队列
            await self.message_queue.put(message)
            
            # 更新发送者状态
            if message.sender_id in self.agent_status:
                self.agent_status[message.sender_id]["message_count"] += 1
                self.agent_status[message.sender_id]["last_seen"] = datetime.now()
            
            self.logger.debug(f"Message sent: {message.sender_id} -> {message.receiver_id}")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def broadcast_message(self, message: AgentMessage) -> None:
        """广播消息"""
        # 发送消息给所有注册的智能体
        for agent_id in self.agents.keys():
            if agent_id != message.sender_id:
                broadcast_message = AgentMessage(
                    sender_id=message.sender_id,
                    receiver_id=agent_id,
                    message_type=message.message_type,
                    content=message.content,
                    timestamp=message.timestamp,
                    priority=message.priority
                )
                await self.send_message(broadcast_message)
    
    async def _message_processor(self) -> None:
        """消息处理器"""
        while self.running:
            try:
                # 从队列获取消息
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # 处理消息
                await self._process_message(message)
                
                # 标记任务完成
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.stats["errors"] += 1
                self.logger.error(f"Message processing error: {e}")
    
    async def _process_message(self, message: AgentMessage) -> None:
        """处理单个消息"""
        try:
            self.stats["messages_received"] += 1
            
            # 更新接收者状态
            if message.receiver_id in self.agent_status:
                self.agent_status[message.receiver_id]["last_seen"] = datetime.now()
            
            # 处理消息类型
            await self._handle_message_by_type(message)
            
            # 调用注册的处理器
            if message.message_type in self.message_handlers:
                for handler in self.message_handlers[message.message_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.logger.error(f"Message handler error: {e}")
            
            self.logger.debug(f"Message processed: {message.sender_id} -> {message.receiver_id}")
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Message processing failed: {e}")
    
    async def _handle_message_by_type(self, message: AgentMessage) -> None:
        """根据消息类型处理"""
        try:
            message_type = MessageType(message.message_type)
            
            if message_type == MessageType.TASK_REQUEST:
                await self._handle_task_request(message)
            elif message_type == MessageType.TASK_RESPONSE:
                await self._handle_task_response(message)
            elif message_type == MessageType.STATUS_UPDATE:
                await self._handle_status_update(message)
            elif message_type == MessageType.QUALITY_ALERT:
                await self._handle_quality_alert(message)
            elif message_type == MessageType.MEMORY_UPDATE:
                await self._handle_memory_update(message)
            elif message_type == MessageType.COORDINATION_REQUEST:
                await self._handle_coordination_request(message)
            elif message_type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(message)
                
        except ValueError:
            # 未知的消息类型
            self.logger.warning(f"Unknown message type: {message.message_type}")
    
    async def _handle_task_request(self, message: AgentMessage) -> None:
        """处理任务请求"""
        # 这里可以实现任务分配逻辑
        pass
    
    async def _handle_task_response(self, message: AgentMessage) -> None:
        """处理任务响应"""
        # 这里可以实现任务结果处理逻辑
        pass
    
    async def _handle_status_update(self, message: AgentMessage) -> None:
        """处理状态更新"""
        if message.receiver_id in self.agent_status:
            self.agent_status[message.receiver_id].update(message.content)
    
    async def _handle_quality_alert(self, message: AgentMessage) -> None:
        """处理质量告警"""
        # 广播质量告警给所有订阅者
        alert_message = AgentMessage(
            sender_id="communication_hub",
            receiver_id="",
            message_type="quality_alert_broadcast",
            content=message.content,
            timestamp=datetime.now(),
            priority=5
        )
        await self.broadcast_message(alert_message)
    
    async def _handle_memory_update(self, message: AgentMessage) -> None:
        """处理记忆更新"""
        # 广播记忆更新给相关订阅者
        pass
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """处理协调请求"""
        # 处理系统协调相关的消息
        pass
    
    async def _handle_heartbeat(self, message: AgentMessage) -> None:
        """处理心跳"""
        if message.sender_id in self.agent_status:
            self.agent_status[message.sender_id]["last_seen"] = datetime.now()
    
    async def _heartbeat_monitor(self) -> None:
        """心跳监控"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for agent_id, status in self.agent_status.items():
                    last_seen = status["last_seen"]
                    if (current_time - last_seen).seconds > 30:  # 30秒无心跳
                        status["status"] = "offline"
                    else:
                        status["status"] = "online"
                
                await asyncio.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                self.logger.error(f"Heartbeat monitor error: {e}")
    
    def _validate_message(self, message: AgentMessage) -> bool:
        """验证消息"""
        required_fields = ["sender_id", "receiver_id", "message_type", "content"]
        
        for field in required_fields:
            if not hasattr(message, field) or getattr(message, field) is None:
                return False
        
        # 验证发送者和接收者是否已注册
        if message.receiver_id and message.receiver_id not in self.agents:
            return False
        
        return True
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """获取通信统计"""
        return {
            **self.stats,
            "agents_registered": len(self.agents),
            "agents_online": sum(1 for status in self.agent_status.values() if status["status"] == "online"),
            "message_history_size": len(self.message_history),
            "subscribers": {event_type: len(subscribers) for event_type, subscribers in self.subscribers.items()}
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体状态"""
        return self.agent_status.get(agent_id)
    
    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取消息历史"""
        return list(self.message_history)[-limit:]