"""
任务调度器

负责管理和调度AI智能体的任务执行
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from queue import PriorityQueue

import structlog

from ..core.framework import TaskStatus
from ..agents.agent_factory import AgentRole


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1  # 关键任务
    HIGH = 2      # 高优先级
    NORMAL = 3    # 普通优先级
    LOW = 4       # 低优先级


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    assigned_agent: str
    dependencies: List[str]  # 依赖的任务ID
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    estimated_duration: int = 300  # 秒
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data
    
    @property
    def duration(self) -> Optional[int]:
        """计算任务持续时间"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        elif self.started_at:
            return int((datetime.now() - self.started_at).total_seconds())
        return None
    
    @property
    def is_completed(self) -> bool:
        """检查任务是否完成"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """检查任务是否失败"""
        return self.status == TaskStatus.FAILED
    
    @property
    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return self.retry_count < self.max_retries


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        
        # 任务管理
        self.tasks: Dict[str, Task] = {}
        self.task_queue = PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        
        # 依赖管理
        self.task_dependencies: Dict[str, List[str]] = {}
        self.completed_tasks: set = set()
        
        # 智能体管理
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        self.agent_load: Dict[str, int] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # 统计信息
        self.stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "average_duration": 0
        }
        
        # 回调函数
        self.task_callbacks: Dict[str, List[Callable]] = {}
        
        # 运行状态
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        self.logger.info("Task Scheduler initialized")
    
    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """注册智能体"""
        self.agent_queues[agent_id] = asyncio.Queue()
        self.agent_load[agent_id] = 0
        self.agent_capabilities[agent_id] = capabilities
        
        self.logger.info(f"Agent registered: {agent_id} with capabilities: {capabilities}")
    
    async def create_task(
        self,
        task_type: str,
        description: str,
        assigned_agent: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: List[str] = None,
        estimated_duration: int = 300,
        metadata: Dict[str, Any] = None
    ) -> str:
        """创建任务"""
        try:
            task_id = f"task_{task_type}_{datetime.now().timestamp()}"
            
            task = Task(
                task_id=task_id,
                task_type=task_type,
                description=description,
                priority=priority,
                assigned_agent=assigned_agent,
                dependencies=dependencies or [],
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                estimated_duration=estimated_duration,
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = task
            self.task_dependencies[task_id] = task.dependencies
            
            # 添加到优先级队列
            self.task_queue.put((priority.value, task_id))
            
            self.stats["tasks_created"] += 1
            
            self.logger.info(f"Task created: {task_id} -> {assigned_agent}")
            
            # 触发回调
            await self._trigger_callbacks("task_created", task)
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            raise
    
    async def start_scheduler(self) -> None:
        """启动任务调度器"""
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Task Scheduler started")
    
    async def stop_scheduler(self) -> None:
        """停止任务调度器"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
        self.logger.info("Task Scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self.running:
            try:
                # 检查并分配任务
                await self._assign_tasks()
                
                # 检查任务超时
                await self._check_task_timeouts()
                
                # 检查依赖关系
                await self._check_dependencies()
                
                await asyncio.sleep(1)  # 每秒检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(5)
    
    async def _assign_tasks(self) -> None:
        """分配任务"""
        while not self.task_queue.empty():
            try:
                # 获取最高优先级的任务
                priority, task_id = self.task_queue.get_nowait()
                
                task = self.tasks[task_id]
                
                # 检查任务状态
                if task.status != TaskStatus.PENDING:
                    continue
                
                # 检查依赖
                if not self._check_task_dependencies(task):
                    # 重新放入队列
                    self.task_queue.put((priority, task_id))
                    continue
                
                # 检查智能体负载
                agent_id = task.assigned_agent
                if agent_id not in self.agent_queues:
                    self.logger.error(f"Agent {agent_id} not registered for task {task_id}")
                    await self._fail_task(task_id, f"Agent {agent_id} not registered")
                    continue
                
                if self.agent_load.get(agent_id, 0) >= 3:  # 最大负载3个任务
                    # 重新放入队列
                    self.task_queue.put((priority, task_id))
                    continue
                
                # 分配任务
                await self._assign_task_to_agent(task_id)
                
            except Exception as e:
                self.logger.error(f"Task assignment error: {e}")
    
    async def _assign_task_to_agent(self, task_id: str) -> None:
        """将任务分配给智能体"""
        try:
            task = self.tasks[task_id]
            agent_id = task.assigned_agent
            
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # 更新智能体负载
            self.agent_load[agent_id] = self.agent_load.get(agent_id, 0) + 1
            self.running_tasks[task_id] = task
            
            # 放入智能体队列
            await self.agent_queues[agent_id].put(task)
            
            self.logger.info(f"Task assigned: {task_id} -> {agent_id}")
            
            # 触发回调
            await self._trigger_callbacks("task_assigned", task)
            
        except Exception as e:
            self.logger.error(f"Failed to assign task {task_id}: {e}")
            await self._fail_task(task_id, str(e))
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """完成任务"""
        try:
            if task_id not in self.tasks:
                self.logger.error(f"Task {task_id} not found")
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # 更新统计
            self.stats["tasks_completed"] += 1
            if task.duration:
                self._update_average_duration(task.duration)
            
            # 清理状态
            if task_id in self.running_tasks:
                agent_id = task.assigned_agent
                self.agent_load[agent_id] = max(0, self.agent_load.get(agent_id, 0) - 1)
                del self.running_tasks[task_id]
            
            self.completed_tasks.add(task_id)
            
            self.logger.info(f"Task completed: {task_id}")
            
            # 触发回调
            await self._trigger_callbacks("task_completed", task)
            
        except Exception as e:
            self.logger.error(f"Failed to complete task {task_id}: {e}")
    
    async def fail_task(self, task_id: str, error: str) -> None:
        """标记任务失败"""
        await self._fail_task(task_id, error)
    
    async def _fail_task(self, task_id: str, error: str) -> None:
        """内部任务失败处理"""
        try:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            
            # 检查是否可以重试
            if task.can_retry:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.error = None
                
                # 重新放入队列
                self.task_queue.put((task.priority.value, task_id))
                
                self.stats["tasks_retried"] += 1
                self.logger.info(f"Task retried: {task_id} (attempt {task.retry_count + 1})")
            else:
                task.status = TaskStatus.FAILED
                task.error = error
                task.completed_at = datetime.now()
                
                self.stats["tasks_failed"] += 1
                self.logger.error(f"Task failed: {task_id} - {error}")
            
            # 清理状态
            if task_id in self.running_tasks:
                agent_id = task.assigned_agent
                self.agent_load[agent_id] = max(0, self.agent_load.get(agent_id, 0) - 1)
                del self.running_tasks[task_id]
            
            # 触发回调
            await self._trigger_callbacks("task_failed", task)
            
        except Exception as e:
            self.logger.error(f"Failed to handle task failure {task_id}: {e}")
    
    async def _check_task_timeouts(self) -> None:
        """检查任务超时"""
        current_time = datetime.now()
        
        for task_id, task in self.running_tasks.items():
            if task.started_at:
                duration = (current_time - task.started_at).total_seconds()
                if duration > task.estimated_duration * 2:  # 超时2倍估计时间
                    await self._fail_task(task_id, "Task timeout")
    
    async def _check_dependencies(self) -> None:
        """检查依赖关系"""
        for task_id, dependencies in self.task_dependencies.items():
            if task_id in self.tasks and not self._check_task_dependencies(self.tasks[task_id]):
                # 如果依赖未完成，重新检查
                self.task_queue.put((self.tasks[task_id].priority.value, task_id))
    
    def _check_task_dependencies(self, task: Task) -> bool:
        """检查任务依赖"""
        if not task.dependencies:
            return True
        
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)
    
    def _update_average_duration(self, duration: int) -> None:
        """更新平均持续时间"""
        if self.stats["tasks_completed"] == 0:
            self.stats["average_duration"] = duration
        else:
            current_avg = self.stats["average_duration"]
            completed = self.stats["tasks_completed"]
            self.stats["average_duration"] = (current_avg * (completed - 1) + duration) / completed
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """注册回调"""
        if event_type not in self.task_callbacks:
            self.task_callbacks[event_type] = []
        self.task_callbacks[event_type].append(callback)
    
    async def _trigger_callbacks(self, event_type: str, task: Task) -> None:
        """触发回调"""
        if event_type in self.task_callbacks:
            for callback in self.task_callbacks[event_type]:
                try:
                    await callback(task)
                except Exception as e:
                    self.logger.error(f"Callback error for {event_type}: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        return self.tasks[task_id].to_dict()
    
    def get_agent_queue(self, agent_id: str) -> asyncio.Queue:
        """获取智能体任务队列"""
        return self.agent_queues.get(agent_id, asyncio.Queue())
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取调度器统计"""
        return {
            **self.stats,
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agent_load": self.agent_load,
            "queue_size": self.task_queue.qsize()
        }