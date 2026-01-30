"""
多AI协同小说生成系统 - 核心模块

这个模块包含了整个系统的核心组件：
- 多AI协同框架
- 记忆管理系统
- AI角色分工机制
- 小说生成引擎
- 质量监控系统
"""

from .framework import MultiAIFramework
from .agent_coordinator import AgentCoordinator
from .task_scheduler import TaskScheduler
from .communication_hub import CommunicationHub

__version__ = "0.1.0"
__author__ = "MiniMax Agent"

__all__ = [
    "MultiAIFramework",
    "AgentCoordinator", 
    "TaskScheduler",
    "CommunicationHub"
]