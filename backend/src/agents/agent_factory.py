"""
AI角色定义模块

定义7个核心AI角色及其职责分工
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from crewai import Agent, Task
from crewai_tools import BaseTool, SerperDevTool, FileReadTool, FileWriteTool

from ..config.settings import get_settings


class AgentRole(Enum):
    """AI角色枚举"""
    COORDINATOR = "coordinator"
    WORLD_ARCHITECT = "world_architect"
    PLOT_BUILDER = "plot_builder"
    SCRIPTWRITER = "scriptwriter"
    WRITING_AGENT = "writing_agent"
    QUALITY_AUDITOR = "quality_auditor"
    MEMORY_MANAGER = "memory_manager"


@dataclass
class RoleConfig:
    """角色配置"""
    name: str
    description: str
    goal: str
    backstory: str
    llm_model: str
    tools: List[str]
    max_iter: int = 3
    verbose: bool = True
    allow_delegation: bool = False


class AIAgentFactory:
    """AI智能体工厂"""
    
    def __init__(self):
        self.settings = get_settings()
        self.role_configs = self._init_role_configs()
    
    def _init_role_configs(self) -> Dict[str, RoleConfig]:
        """初始化角色配置"""
        return {
            AgentRole.COORDINATOR.value: RoleConfig(
                name="协调者",
                description="系统协调者，负责任务调度、冲突解决和全局决策",
                goal="确保多AI协同工作高效进行，解决冲突，优化整体流程",
                backstory="你是一个经验丰富的高级AI协调者，具有强大的逻辑思维和问题解决能力。你负责协调多个AI智能体的工作，确保小说生成过程的高质量和高效率。",
                llm_model="deepseek",
                tools=["file_read", "file_write"],
                max_iter=3,
                verbose=True,
                allow_delegation=True
            ),
            
            AgentRole.WORLD_ARCHITECT.value: RoleConfig(
                name="世界观架构师",
                description="负责创建和维护小说的世界观设定",
                goal="构建完整、一致的小说世界，包括历史、地理、文化、魔法系统等",
                backstory="你是一个富有创造力的世界观构建专家，擅长设计复杂而有趣的世界设定。你能够创造独特的文明、地理环境、社会结构和文化传统。",
                llm_model="qwen",
                tools=["file_read", "file_write"],
                max_iter=2,
                verbose=True,
                allow_delegation=False
            ),
            
            AgentRole.PLOT_BUILDER.value: RoleConfig(
                name="情节构建者",
                description="负责设计小说的整体结构和情节发展",
                goal="创建引人入胜的情节线，管理伏笔和高潮，确保逻辑连贯",
                backstory="你是一个精于编织故事的大师，能够设计复杂而富有层次的情节。你擅长创造紧张感、设置悬念、处理因果关系。",
                llm_model="deepseek",
                tools=["file_read", "file_write"],
                max_iter=2,
                verbose=True,
                allow_delegation=False
            ),
            
            AgentRole.SCRIPTWRITER.value: RoleConfig(
                name="编剧",
                description="负责创作对话和场景描述",
                goal="创作生动自然的对话，描写引人入胜的场景",
                backstory="你是一个才华横溢的编剧和对话专家，能够为每个角色创造独特的声音。你擅长刻画人物性格，营造氛围。",
                llm_model="minimax",
                tools=["file_read", "file_write"],
                max_iter=2,
                verbose=True,
                allow_delegation=False
            ),
            
            AgentRole.WRITING_AGENT.value: RoleConfig(
                name="写作智能体",
                description="负责章节内容的具体写作",
                goal="根据大纲和要求，高质量地完成章节写作",
                backstory="你是一个专业的写作者，擅长将抽象的想法转化为具体的文字。你注重文笔优美、情节生动、人物鲜活。",
                llm_model="qwen",
                tools=["file_read", "file_write"],
                max_iter=3,
                verbose=True,
                allow_delegation=False
            ),
            
            AgentRole.QUALITY_AUDITOR.value: RoleConfig(
                name="质量审核员",
                description="负责质量检查和一致性验证",
                goal="确保小说质量达标，检查逻辑一致性和风格统一性",
                backstory="你是一个严格的质量控制专家，具有敏锐的洞察力和判断力。你能够发现细节问题，确保作品的品质。",
                llm_model="qwen",
                tools=["file_read", "file_write"],
                max_iter=2,
                verbose=True,
                allow_delegation=False
            ),
            
            AgentRole.MEMORY_MANAGER.value: RoleConfig(
                name="记忆管理员",
                description="负责管理和维护系统记忆",
                goal="确保信息准确存储，便于检索和关联",
                backstory="你是一个细心的信息管理员，负责维护系统的记忆系统。你能够组织和索引各种信息，确保知识的完整性和可访问性。",
                llm_model="qwen",
                tools=["file_read", "file_write"],
                max_iter=1,
                verbose=True,
                allow_delegation=False
            )
        }
    
    def create_agent(self, role: AgentRole, model_config: Dict[str, Any]) -> Agent:
        """创建AI智能体"""
        config = self.role_configs[role.value]
        
        # 根据角色获取模型配置
        model_config_map = {
            "deepseek": {
                "model": "deepseek-chat",
                "api_base": self.settings.ai.deepseek_base_url,
                "api_key": self.settings.ai.deepseek_api_key
            },
            "qwen": {
                "model": "qwen-plus",
                "api_base": self.settings.ai.qwen_base_url,
                "api_key": self.settings.ai.qwen_api_key
            },
            "minimax": {
                "model": "abab6.5s-chat",
                "api_base": self.settings.ai.minimax_base_url,
                "api_key": self.settings.ai.minimax_api_key
            },
            "siliconflow": {
                "model": "deepseek-chat",
                "api_base": self.settings.ai.siliconflow_base_url,
                "api_key": self.settings.ai.siliconflow_api_key
            }
        }
        
        model_config = model_config_map.get(config.llm_model, model_config_map["deepseek"])
        
        # 创建工具列表
        tools = []
        if "file_read" in config.tools:
            tools.append(FileReadTool())
        if "file_write" in config.tools:
            tools.append(FileWriteTool())
        
        # 创建智能体
        agent = Agent(
            role=config.name,
            goal=config.goal,
            backstory=config.backstory,
            tools=tools,
            verbose=config.verbose,
            allow_delegation=config.allow_delegation,
            max_iter=config.max_iter,
            llm=model_config  # CrewAI需要传递模型配置
        )
        
        return agent
    
    def get_role_description(self, role: AgentRole) -> str:
        """获取角色描述"""
        config = self.role_configs[role.value]
        return f"""
角色：{config.name}
职责：{config.description}
目标：{config.goal}
模型：{config.llm_model}
"""
    
    def get_coordination_instructions(self) -> Dict[str, str]:
        """获取协调指令"""
        return {
            "task_distribution": "根据任务复杂度和AI能力进行智能分配",
            "conflict_resolution": "优先级协议 → 协商解决 → 人工仲裁",
            "quality_control": "多层检查：输入 → 过程 → 输出 → 反馈",
            "memory_sharing": "实时同步记忆，确保上下文一致",
            "progress_tracking": "实时监控任务进度，及时调整策略"
        }


class AgentCoordinator:
    """AI角色协调器"""
    
    def __init__(self):
        self.factory = AIAgentFactory()
        self.agents: Dict[str, Agent] = {}
        self.role_assignments: Dict[str, AgentRole] = {}
        self.task_queues: Dict[str, List[Task]] = {}
        self.logger = structlog.get_logger()
    
    def initialize_agents(self, model_configs: Dict[str, Dict]) -> None:
        """初始化所有智能体"""
        for role in AgentRole:
            agent = self.factory.create_agent(role, model_configs)
            agent_id = role.value
            self.agents[agent_id] = agent
            self.role_assignments[agent_id] = role
            
            self.logger.info(f"Initialized agent: {agent_id}")
    
    def assign_task(self, task: Task, agent_role: AgentRole) -> bool:
        """分配任务给特定角色"""
        try:
            agent_id = agent_role.value
            if agent_id not in self.agents:
                self.logger.error(f"Agent {agent_id} not found")
                return False
            
            task.agent = self.agents[agent_id]
            
            if agent_id not in self.task_queues:
                self.task_queues[agent_id] = []
            
            self.task_queues[agent_id].append(task)
            
            self.logger.info(f"Task assigned to {agent_id}: {task.description[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}")
            return False
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """获取协调状态"""
        return {
            "agents_active": len(self.agents),
            "task_queues": {
                role: len(queue) for role, queue in self.task_queues.items()
            },
            "role_assignments": {
                agent_id: role.value for agent_id, role in self.role_assignments.items()
            }
        }