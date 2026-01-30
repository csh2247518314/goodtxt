"""
多AI协同框架 - 核心协调器

基于LangGraph和CrewAI的多AI协同框架，
负责协调各个AI智能体的工作流程。
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import structlog

# 可选依赖，使用try-catch处理
try:
    from langgraph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # 创建占位符类以避免导入错误
    class StateGraph:
        def __init__(self, state_class): pass
        def add_node(self, name, handler): pass
        def add_edge(self, source, target, condition=None): pass
        def set_entry_point(self, name): pass
        def compile(self): return self
    
    END = "END"

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # 创建占位符类
    class Agent:
        def __init__(self, **kwargs): pass
        def kickoff(self, task): return ""
    
    class Task:
        def __init__(self, **kwargs): pass
    
    class Crew:
        def __init__(self, **kwargs): pass

try:
    from crewai_tools import BaseTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False
    # 创建占位符类
    class BaseTool:
        def __init__(self, **kwargs): pass

from ..config.settings import get_settings
from .communication_hub import CommunicationHub
from .task_scheduler import TaskScheduler
from ..memory.memory_manager import MemoryManager


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentMessage:
    """智能体消息"""
    sender_id: str
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1-5, 5为最高优先级


@dataclass
class WorkflowState:
    """工作流状态"""
    current_task: Optional[str]
    task_status: TaskStatus
    agent_states: Dict[str, Dict[str, Any]]
    shared_context: Dict[str, Any]
    messages: List[AgentMessage]
    error_log: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]


class MultiAIFramework:
    """多AI协同框架主类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        
        # 核心组件
        self.communication_hub = CommunicationHub()
        self.task_scheduler = TaskScheduler()
        self.memory_manager = MemoryManager()
        
        # 智能体管理
        self.agents: Dict[str, Agent] = {}
        self.agent_roles: Dict[str, str] = {}
        
        # 工作流管理
        self.workflow_graph: Optional[StateGraph] = None
        self.active_workflows: Dict[str, Dict] = {}
        
        # 状态管理
        self.workflow_states: Dict[str, WorkflowState] = {}
        
        # 回调函数
        self.task_callbacks: Dict[str, Callable] = {}
        self.quality_callbacks: List[Callable] = []
        
        self.logger.info("MultiAI Framework initialized")
    
    def register_agent(self, agent_id: str, agent: Agent, role: str) -> None:
        """注册智能体"""
        self.agents[agent_id] = agent
        self.agent_roles[agent_id] = role
        
        # 注册到通信中心
        self.communication_hub.register_agent(agent_id, agent)
        
        self.logger.info(f"Agent registered: {agent_id} as {role}")
    
    def create_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]) -> None:
        """创建工作流"""
        try:
            # 构建工作流图
            graph = StateGraph(WorkflowState)
            
            # 添加节点
            for node_name, node_config in workflow_config.get("nodes", {}).items():
                graph.add_node(
                    node_name,
                    self._create_node_handler(node_name, node_config)
                )
            
            # 添加边
            for edge in workflow_config.get("edges", []):
                graph.add_edge(
                    edge["source"], 
                    edge["target"], 
                    self._create_edge_condition(edge.get("condition"))
                )
            
            # 设置开始和结束节点
            start_node = workflow_config.get("start_node")
            end_nodes = workflow_config.get("end_nodes", [])
            
            if start_node:
                graph.set_entry_point(start_node)
            
            for end_node in end_nodes:
                graph.add_edge(end_node, END)
            
            # 编译工作流
            self.workflow_graph = graph.compile()
            
            # 初始化工作流状态
            self.workflow_states[workflow_id] = WorkflowState(
                current_task=None,
                task_status=TaskStatus.PENDING,
                agent_states={},
                shared_context={},
                messages=[],
                error_log=[],
                quality_metrics={}
            )
            
            self.logger.info(f"Workflow created: {workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow {workflow_id}: {e}")
            raise
    
    def execute_workflow(
        self, 
        workflow_id: str, 
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行工作流"""
        if workflow_id not in self.workflow_states:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        state = self.workflow_states[workflow_id]
        
        try:
            # 更新工作流状态
            state.task_status = TaskStatus.RUNNING
            state.shared_context.update(input_data or {})
            if context:
                state.shared_context.update(context)
            
            self.logger.info(f"Starting workflow execution: {workflow_id}")
            
            # 执行工作流
            result = self.workflow_graph.invoke(
                state,
                config={"thread_id": workflow_id}
            )
            
            # 更新状态
            state.task_status = TaskStatus.COMPLETED
            state.shared_context.update(result.get("shared_context", {}))
            
            self.logger.info(f"Workflow completed: {workflow_id}")
            
            return {
                "status": "success",
                "result": result.get("shared_context", {}),
                "quality_metrics": result.get("quality_metrics", {})
            }
            
        except Exception as e:
            state.task_status = TaskStatus.FAILED
            state.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "workflow_id": workflow_id
            })
            
            self.logger.error(f"Workflow failed: {workflow_id} - {e}")
            return {
                "status": "error",
                "error": str(e),
                "error_log": state.error_log
            }
    
    def _create_node_handler(self, node_name: str, node_config: Dict[str, Any]) -> Callable:
        """创建节点处理器"""
        def node_handler(state: WorkflowState) -> WorkflowState:
            agent_id = node_config.get("agent_id")
            task_type = node_config.get("task_type")
            
            if not agent_id or agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found for node {node_name}")
            
            # 获取智能体
            agent = self.agents[agent_id]
            
            # 创建任务
            task = Task(
                description=node_config.get("description", f"Execute {task_type}"),
                agent=agent,
                context=str(state.shared_context),
                expected_output=node_config.get("expected_output", "")
            )
            
            try:
                # 执行任务
                result = agent.kickoff(task)
                
                # 确保结果安全处理
                if result is None:
                    result = ""
                elif hasattr(result, 'raw'):
                    result = result.raw
                elif hasattr(result, 'pydantic'):
                    result = result.pydantic
                
                # 更新状态
                if agent_id not in state.agent_states:
                    state.agent_states[agent_id] = {}
                
                state.agent_states[agent_id].update({
                    "last_task": task_type,
                    "last_result": str(result),
                    "last_execution": datetime.now().isoformat()
                })
                
                # 更新共享上下文
                state.shared_context.update(node_config.get("output_mapping", {}))
                
                self.logger.info(f"Node {node_name} completed by agent {agent_id}")
                
            except Exception as e:
                error_info = {
                    "node": node_name,
                    "agent": agent_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                state.error_log.append(error_info)
                raise
            
            return state
        
        return node_handler
    
    def _create_edge_condition(self, condition: Optional[str]) -> Callable:
        """创建边条件处理器"""
        if not condition:
            return lambda state: True
        
        def condition_handler(state: WorkflowState) -> bool:
            try:
                # 安全的条件评估 - 仅支持有限的预定义操作符
                allowed_operations = {
                    "==": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                    ">=": lambda a, b: a >= b,
                    "<=": lambda a, b: a <= b,
                    "and": lambda a, b: a and b,
                    "or": lambda a, b: a or b,
                    "not": lambda a: not a,
                    "len": lambda x: len(x) if hasattr(x, '__len__') else 0,
                    "getattr": getattr,
                    "hasattr": hasattr
                }
                
                # 简单的条件解析器（避免使用 eval）
                if "==" in condition:
                    parts = condition.split("==")
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip().strip('"').strip("'")
                        if left.startswith("state."):
                            attr_path = left[6:]  # 移除 "state."
                            try:
                                # 安全地获取嵌套属性
                                value = state
                                for attr in attr_path.split('.'):
                                    if hasattr(value, attr):
                                        value = getattr(value, attr)
                                    elif isinstance(value, dict) and attr in value:
                                        value = value[attr]
                                    else:
                                        value = None
                                        break
                                return str(value) == right
                            except (AttributeError, TypeError):
                                return False
                
                # 默认情况下允许通过（避免阻塞工作流）
                return True
                
            except Exception as e:
                self.logger.error(f"Edge condition evaluation failed: {e}")
                return False
        
        return condition_handler
    
    async def broadcast_message(self, message: AgentMessage) -> None:
        """广播消息到所有智能体"""
        await self.communication_hub.broadcast_message(message)
    
    def register_quality_callback(self, callback: Callable) -> None:
        """注册质量监控回调"""
        self.quality_callbacks.append(callback)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        if workflow_id not in self.workflow_states:
            return {"error": "Workflow not found"}
        
        state = self.workflow_states[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": state.task_status.value,
            "current_task": state.current_task,
            "agent_states": state.agent_states,
            "shared_context": state.shared_context,
            "error_count": len(state.error_log),
            "quality_metrics": state.quality_metrics
        }