"""
小说生成引擎

基于多AI协同的小说内容生成引擎，
负责协调各个AI角色完成小说创作。
"""

import asyncio
import json
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

import structlog

from ..ai.model_client import ai_model_manager, AIModelType
from ..memory.memory_manager import MemoryManager, MemoryType, MemoryCategory
from ..quality.quality_monitor import QualityMonitor
from ..config.settings import get_settings


class NovelGenre(Enum):
    """小说类型枚举"""
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    HORROR = "horror"
    ADVENTURE = "adventure"
    HISTORICAL = "historical"
    CONTEMPORARY = "contemporary"


class NovelLength(Enum):
    """小说长度枚举"""
    SHORT = "short"  # 1-50页
    MEDIUM = "medium"  # 50-200页
    LONG = "long"  # 200-500页
    EPIC = "epic"  # 500页以上


@dataclass
class NovelProject:
    """小说项目"""
    project_id: str
    title: str
    genre: NovelGenre
    length: NovelLength
    theme: str
    target_audience: str
    language: str
    created_at: datetime
    status: str = "draft"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['genre'] = self.genre.value
        data['length'] = self.length.value
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class Chapter:
    """章节"""
    chapter_id: str
    chapter_number: int
    title: str
    content: str
    word_count: int
    created_at: datetime
    status: str = "draft"
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class CharacterProfile:
    """角色档案"""
    character_id: str
    name: str
    role: str
    description: str
    personality: Dict[str, Any]
    relationships: Dict[str, str]
    backstory: str
    goals: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


class NovelGenerationEngine:
    """小说生成引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.memory_manager = MemoryManager()
        self.quality_monitor = QualityMonitor()
        self.ai_manager = ai_model_manager
        
        self.logger = structlog.get_logger()
        
        # 小说项目管理
        self.active_projects: Dict[str, NovelProject] = {}
        self.novel_content: Dict[str, List[Chapter]] = {}
        self.character_profiles: Dict[str, Dict[str, CharacterProfile]] = {}
        
        self.logger.info("Novel Generation Engine initialized")
    

    
    async def create_novel_project(
        self, 
        project_config: Dict[str, Any]
    ) -> str:
        """创建小说项目"""
        try:
            # 使用 UUID 生成唯一项目 ID
            if "project_id" not in project_config:
                project_id = f"project_{uuid.uuid4().hex[:12]}"
            else:
                project_id = project_config["project_id"]
            
            # 检查项目 ID 是否已存在
            if project_id in self.active_projects:
                raise ValueError(f"项目 ID {project_id} 已存在")
            
            # 创建项目对象
            project = NovelProject(
                project_id=project_id,
                title=project_config["title"],
                genre=NovelGenre(project_config["genre"]),
                length=NovelLength(project_config["length"]),
                theme=project_config["theme"],
                target_audience=project_config["target_audience"],
                language=project_config.get("language", "中文"),
                created_at=datetime.now()
            )
            
            # 保存项目
            self.active_projects[project.project_id] = project
            
            # 存储到记忆系统
            await self.memory_manager.store_memory(
                memory_id=f"project_{project.project_id}",
                content=json.dumps(project.to_dict(), ensure_ascii=False),
                category=MemoryCategory.WORLDVIEW,
                memory_type=MemoryType.MEDIUM_TERM,
                importance_score=1.0,
                metadata={"project_id": project.project_id}
            )
            
            self.logger.info(f"Created novel project: {project.project_id}")
            return project.project_id
            
        except Exception as e:
            self.logger.error(f"Failed to create novel project: {e}")
            raise
    
    async def execute_novel_generation(
        self, 
        project_id: str, 
        chapter_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行小说生成"""
        try:
            if project_id not in self.active_projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.active_projects[project_id]
            
            # 执行项目设置
            setup_result = await self._execute_project_setup(project_id, project)
            
            # 执行世界观构建
            world_result = await self._execute_world_building(project_id, project)
            
            # 执行角色设计
            character_result = await self._execute_character_design(project_id, project)
            
            # 执行情节大纲
            plot_result = await self._execute_plot_outline(project_id, project)
            
            # 生成章节
            chapter_count = chapter_count or self._calculate_chapter_count(project.length)
            chapter_results = []
            
            for i in range(chapter_count):
                chapter_result = await self._generate_chapter(project_id, i + 1)
                chapter_results.append(chapter_result)
            
            # 质量评估
            quality_result = await self._evaluate_novel_quality(project_id, chapter_results)
            
            # 保存项目状态
            project.status = "completed" if quality_result.get("overall_quality", 0.5) > 0.7 else "draft"
            
            self.logger.info(f"Novel generation completed for project: {project_id}")
            
            return {
                "project_id": project_id,
                "status": project.status,
                "setup_result": setup_result,
                "world_result": world_result,
                "character_result": character_result,
                "plot_result": plot_result,
                "chapters": chapter_results,
                "quality_assessment": quality_result
            }
            
        except Exception as e:
            self.logger.error(f"Novel generation failed for project {project_id}: {e}")
            raise
    
    async def _execute_project_setup(self, project_id: str, project: NovelProject) -> Dict[str, Any]:
        """执行项目设置"""
        try:
            # 存储项目设置到记忆
            await self.memory_manager.store_memory(
                memory_id=f"setup_{project_id}",
                content=json.dumps(project.to_dict(), ensure_ascii=False),
                category=MemoryCategory.WORLDVIEW,
                memory_type=MemoryType.SHORT_TERM,
                metadata={"type": "project_setup", "project_id": project_id}
            )
            
            return {
                "status": "success",
                "message": "项目设置完成",
                "project_config": project.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Project setup failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_world_building(self, project_id: str, project: NovelProject) -> Dict[str, Any]:
        """执行世界观构建"""
        try:
            # 创建世界观构建任务
            world_prompt = f"""
请为以下小说项目构建一个完整的世界观：

标题：{project.title}
类型：{project.genre.value}
主题：{project.theme}
目标受众：{project.target_audience}
语言：{project.language}

请为这个{project.genre.value}类型的小说构建一个详细的世界观，包含以下要素：
1. 世界设定（地理、历史、文化）
2. 魔法/科技系统（如果适用）
3. 社会结构和政治体系
4. 重要地点和地理环境
5. 历史背景和重要事件
6. 世界观特色和创新元素

请用中文写作，内容要详细丰富，符合小说的主题和类型。
"""
            
            # 调用AI模型生成世界观
            response = await self.ai_manager.chat_with_model(
                model_type=AIModelType.COORDINATOR,
                prompt=world_prompt,
                system_prompt="你是一个专业的小说世界观构建师，擅长为不同类型的小说创造完整详细的世界观。"
            )
            
            if not response.success:
                # 检查是否是API密钥缺失导致的错误
                if "未配置" in response.error_message or "模型未启用" in response.error_message:
                    return {
                        "status": "warning",
                        "content": "世界观构建需要配置AI模型API密钥",
                        "error": response.error_message,
                        "note": "请在docker-compose.yml中配置AI_API密钥"
                    }
                else:
                    raise Exception(f"世界观构建失败: {response.error_message}")
            
            world_content = response.content
            
            # 存储世界观到记忆
            await self.memory_manager.store_memory(
                memory_id=f"worldview_{project_id}",
                content=world_content,
                category=MemoryCategory.WORLDVIEW,
                memory_type=MemoryType.LONG_TERM,
                importance_score=1.0,
                metadata={"project_id": project_id, "type": "worldview"}
            )
            
            return {
                "status": "success",
                "content": world_content,
                "elements": ["geography", "history", "culture", "social_structure", "technology"],
                "tokens_used": response.tokens_used,
                "response_time": response.response_time
            }
            
        except Exception as e:
            self.logger.error(f"World building failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_character_design(self, project_id: str, project: NovelProject) -> Dict[str, Any]:
        """执行角色设计"""
        try:
            # 获取世界观信息
            world_memories = await self.memory_manager.search_memories(
                query=f"世界观 {project_id}",
                category=MemoryCategory.WORLDVIEW
            )
            world_context = world_memories[0].content if world_memories and len(world_memories) > 0 else ""
            
            # 创建角色设计任务
            character_prompt = f"""
请为小说《{project.title}》设计主要角色：

小说信息：
- 类型：{project.genre.value}
- 主题：{project.theme}
- 目标受众：{project.target_audience}
- 语言：{project.language}

世界观背景：
{world_context}

请为这个{project.genre.value}类型的小说设计3-5个主要角色，每个角色包含：
1. 姓名、年龄、外貌特征和服装风格
2. 性格特征、行为模式和说话方式
3. 详细背景故事和成长经历
4. 主要目标、动机和内心冲突
5. 与其他角色的复杂关系网络
6. 在故事中的作用和成长弧线

请用中文写作，角色要生动立体，符合小说的主题和世界观设定。
"""
            
            # 调用AI模型生成角色
            response = await self.ai_manager.chat_with_model(
                model_type=AIModelType.COORDINATOR,
                prompt=character_prompt,
                system_prompt="你是一个专业的小说角色设计师，擅长创造立体生动的角色形象。"
            )
            
            if not response.success:
                raise Exception(f"角色设计失败: {response.error_message}")
            
            characters_content = response.content
            
            # 解析角色信息（简单解析，实际中可能需要更复杂的处理）
            characters = []
            char_sections = characters_content.split('\n\n')
            for i, section in enumerate(char_sections[:5]):  # 最多5个角色
                if section.strip():
                    characters.append({
                        "name": f"角色{i+1}",
                        "description": section.strip(),
                        "role": "main_character"
                    })
            
            # 存储角色信息
            for char in characters:
                char_id = f"char_{char['name']}_{project_id}"
                await self.memory_manager.store_memory(
                    memory_id=char_id,
                    content=json.dumps(char, ensure_ascii=False),
                    category=MemoryCategory.CHARACTER,
                    memory_type=MemoryType.LONG_TERM,
                    importance_score=0.9,
                    metadata={"project_id": project_id, "type": "character"}
                )
            
            return {
                "status": "success",
                "characters": characters,
                "character_count": len(characters),
                "full_content": characters_content,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time
            }
            
        except Exception as e:
            self.logger.error(f"Character design failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_plot_outline(self, project_id: str, project: NovelProject) -> Dict[str, Any]:
        """执行情节大纲"""
        try:
            # 获取世界观和角色信息
            world_memories = await self.memory_manager.search_memories(
                query=f"世界观 {project_id}",
                category=MemoryCategory.WORLDVIEW
            )
            world_context = world_memories[0].content if world_memories and len(world_memories) > 0 else ""
            
            char_memories = await self.memory_manager.search_memories(
                query=f"角色 {project_id}",
                category=MemoryCategory.CHARACTER
            )
            char_context = ""
            for memory in char_memories:
                char_context += f"\n{memory.content}"
            
            # 创建情节大纲
            outline_prompt = f"""
请为小说《{project.title}》制定完整的情节大纲：

小说信息：
- 类型：{project.genre.value}
- 主题：{project.theme}
- 目标受众：{project.target_audience}
- 长度：{project.length.value}
- 语言：{project.language}

世界观背景：
{world_context}

主要角色：
{char_context}

请制定完整的三幕结构情节大纲，包含：
1. 故事背景和设定
2. 主要冲突和问题
3. 三幕结构：
   - 第一幕（开端）：背景介绍，角色登场，引发事件
   - 第二幕（发展）：冲突升级，困难增加，中点转折
   - 第三幕（高潮和结局）：高潮冲突，解决问题，结局
4. 故事主题和寓意
5. 高潮点设计
6. 结局安排

请用中文写作，内容要详细合理，符合{project.genre.value}类型小说的特点。
"""
            
            # 调用AI模型生成大纲
            response = await self.ai_manager.chat_with_model(
                model_type=AIModelType.COORDINATOR,
                prompt=outline_prompt,
                system_prompt="你是一个专业的小说情节策划师，擅长制定引人入胜的故事结构和大纲。"
            )
            
            if not response.success:
                raise Exception(f"情节大纲生成失败: {response.error_message}")
            
            outline_content = response.content
            
            # 简化的结构化处理
            outline = {
                "content": outline_content,
                "acts": [
                    {"act": 1, "description": "开端阶段"},
                    {"act": 2, "description": "发展阶段"},
                    {"act": 3, "description": "高潮和结局"}
                ],
                "main_conflict": "主要冲突（见大纲内容）",
                "theme": project.theme,
                "genre": project.genre.value
            }
            
            # 存储大纲到记忆
            await self.memory_manager.store_memory(
                memory_id=f"outline_{project_id}",
                content=outline_content,
                category=MemoryCategory.PLOT,
                memory_type=MemoryType.LONG_TERM,
                importance_score=1.0,
                metadata={"project_id": project_id, "type": "outline"}
            )
            
            return {
                "status": "success",
                "outline": outline,
                "full_content": outline_content,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time
            }
            
        except Exception as e:
            self.logger.error(f"Plot outline failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _generate_chapter(self, project_id: str, chapter_number: int) -> Dict[str, Any]:
        """生成章节"""
        try:
            # 获取项目信息
            project = self.active_projects[project_id]
            
            # 获取之前生成的上下文
            world_memories = await self.memory_manager.search_memories(
                query=f"世界观 {project_id}",
                category=MemoryCategory.WORLDVIEW
            )
            world_context = world_memories[0].content if world_memories else ""
            
            char_memories = await self.memory_manager.search_memories(
                query=f"角色 {project_id}",
                category=MemoryCategory.CHARACTER
            )
            char_context = ""
            for memory in char_memories[:3]:  # 获取前3个角色
                char_context += f"\n{memory.content}"
            
            outline_memories = await self.memory_manager.search_memories(
                query=f"大纲 {project_id}",
                category=MemoryCategory.PLOT
            )
            outline_context = outline_memories[0].content if outline_memories else ""
            
            # 创建章节生成提示词
            chapter_prompt = f"""
请为小说《{project.title}》撰写第{chapter_number}章。

小说基本信息：
- 类型：{project.genre.value}
- 主题：{project.theme}
- 长度：{project.length.value}
- 语言：{project.language}

世界观背景：
{world_context}

主要角色：
{char_context}

故事大纲：
{outline_context}

请撰写第{chapter_number}章，要求：
1. 内容连贯，符合前文设定
2. 包含适当的对话、动作和心理描写
3. 推进主要情节发展
4. 字数控制在3000-5000字
5. 用中文写作，语言生动自然

请直接开始写章节内容，不需要章节标题。
"""
            
            # 调用AI模型生成章节
            response = await self.ai_manager.chat_with_model(
                model_type=AIModelType.WRITER,
                prompt=chapter_prompt,
                system_prompt=f"你是一个专业的小说作者，擅长写作{project.genre.value}类型的小说。请创作高质量的小说章节。",
                max_tokens=8000,
                temperature=0.7
            )
            
            if not response.success:
                raise Exception(f"章节生成失败: {response.error_message}")
            
            chapter_content = response.content
            
            # 创建章节对象
            chapter = Chapter(
                chapter_id=f"ch_{chapter_number}_{project_id}",
                chapter_number=chapter_number,
                title=f"第{chapter_number}章",
                content=chapter_content,
                word_count=len(chapter_content),
                created_at=datetime.now()
            )
            
            # 保存章节
            if project_id not in self.novel_content:
                self.novel_content[project_id] = []
            self.novel_content[project_id].append(chapter)
            
            # 存储章节到记忆
            await self.memory_manager.store_memory(
                memory_id=f"chapter_{chapter_number}_{project_id}",
                content=chapter_content,
                category=MemoryCategory.PLOT,
                memory_type=MemoryType.SHORT_TERM,
                importance_score=0.8,
                metadata={
                    "project_id": project_id,
                    "type": "chapter",
                    "chapter_number": chapter_number,
                    "word_count": chapter.word_count
                }
            )
            
            # 质量评估
            quality_score = await self.quality_monitor.evaluate_chapter_quality(chapter)
            chapter.quality_score = quality_score
            
            return {
                "status": "success",
                "chapter": chapter.to_dict(),
                "quality_score": quality_score,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time
            }
            
        except Exception as e:
            self.logger.error(f"Chapter generation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _evaluate_novel_quality(self, project_id: str, chapters: List[Dict]) -> Dict[str, Any]:
        """评估小说质量"""
        try:
            # 获取所有章节
            chapter_objects = []
            for chapter_data in chapters:
                if "chapter" in chapter_data:
                    # 从字典创建Chapter对象
                    chapter_dict = chapter_data["chapter"]
                    chapter = Chapter(
                        chapter_id=chapter_dict["chapter_id"],
                        chapter_number=chapter_dict["chapter_number"],
                        title=chapter_dict["title"],
                        content=chapter_dict["content"],
                        word_count=chapter_dict["word_count"],
                        created_at=datetime.fromisoformat(chapter_dict["created_at"]),
                        quality_score=chapter_dict["quality_score"]
                    )
                    chapter_objects.append(chapter)
            
            # 质量评估
            quality_assessment = await self.quality_monitor.evaluate_novel_quality(
                project_id, chapter_objects
            )
            
            return quality_assessment
            
        except Exception as e:
            self.logger.error(f"Novel quality evaluation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_chapter_count(self, length: NovelLength) -> int:
        """计算章节数量"""
        chapter_counts = {
            NovelLength.SHORT: 5,
            NovelLength.MEDIUM: 15,
            NovelLength.LONG: 30,
            NovelLength.EPIC: 50
        }
        return chapter_counts.get(length, 15)
    

    
    async def export_novel(self, project_id: str, format: str = "txt") -> str:
        """导出小说"""
        try:
            # 确保导出目录存在
            os.makedirs("./exports", exist_ok=True)
            
            chapters = self.novel_content.get(project_id, [])
            if not chapters:
                raise ValueError("No chapters to export")
            
            project = self.active_projects[project_id]
            
            if format.lower() == "txt":
                content = f"《{project.title}》\n\n"
                for chapter in sorted(chapters, key=lambda x: x.chapter_number):
                    content += f"{chapter.title}\n\n{chapter.content}\n\n"
                
                export_path = f"./exports/{project_id}.txt"
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return export_path
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Novel export failed: {e}")
            raise

    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """更新项目信息"""
        try:
            if project_id not in self.active_projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.active_projects[project_id]
            
            # 更新允许的字段
            if "title" in updates:
                project.title = updates["title"]
            if "theme" in updates:
                project.theme = updates["theme"]
            if "target_audience" in updates:
                project.target_audience = updates["target_audience"]
            
            # 更新记忆中的项目信息
            await self.memory_manager.store_memory(
                memory_id=f"project_{project.project_id}",
                content=json.dumps(project.to_dict(), ensure_ascii=False),
                category=MemoryCategory.WORLDVIEW,
                memory_type=MemoryType.MEDIUM_TERM,
                importance_score=1.0,
                metadata={"project_id": project.project_id}
            )
            
            self.logger.info(f"Updated project: {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update project {project_id}: {e}")
            raise

    async def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            if project_id not in self.active_projects:
                raise ValueError(f"Project {project_id} not found")
            
            # 删除项目
            del self.active_projects[project_id]
            
            # 删除相关章节
            if project_id in self.novel_content:
                del self.novel_content[project_id]
            
            # 删除相关角色档案
            if project_id in self.character_profiles:
                del self.character_profiles[project_id]
            
            # 清理相关记忆
            # 这里应该删除所有与项目相关的记忆
            # 简化实现：记录删除操作
            self.logger.info(f"Deleted project: {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete project {project_id}: {e}")
            raise

    async def update_chapter(self, chapter_id: str, content: str) -> bool:
        """更新章节内容"""
        try:
            # 查找章节
            chapter = None
            for project_chapters in self.novel_content.values():
                for ch in project_chapters:
                    if ch.chapter_id == chapter_id:
                        chapter = ch
                        break
                if chapter:
                    break
            
            if not chapter:
                raise ValueError(f"Chapter {chapter_id} not found")
            
            # 更新内容
            chapter.content = content
            chapter.word_count = len(content)
            
            # 存储到记忆
            await self.memory_manager.store_memory(
                memory_id=f"chapter_{chapter.chapter_number}_{chapter.chapter_id}",
                content=content,
                category=MemoryCategory.PLOT,
                memory_type=MemoryType.SHORT_TERM,
                importance_score=0.8,
                metadata={
                    "project_id": chapter.chapter_id.split('_')[-1],
                    "type": "chapter",
                    "chapter_number": chapter.chapter_number,
                    "word_count": chapter.word_count
                }
            )
            
            self.logger.info(f"Updated chapter: {chapter_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update chapter {chapter_id}: {e}")
            raise

    async def regenerate_chapter(self, chapter_id: str, instructions: Optional[str] = None) -> str:
        """重新生成章节"""
        try:
            # 查找章节和项目
            chapter = None
            project_id = None
            for proj_id, project_chapters in self.novel_content.items():
                for ch in project_chapters:
                    if ch.chapter_id == chapter_id:
                        chapter = ch
                        project_id = proj_id
                        break
                if chapter:
                    break
            
            if not chapter or not project_id:
                raise ValueError(f"Chapter {chapter_id} not found")
            
            project = self.active_projects[project_id]
            
            # 构建重新生成的提示词
            regenerate_prompt = f"""
请重新生成小说《{project.title}》的第{chapter.chapter_number}章。

小说信息：
- 类型：{project.genre.value}
- 主题：{project.theme}
- 目标受众：{project.target_audience}

原有章节内容：
{chapter.content}

重新生成要求：
1. 保持原有的章节标题和基本情节
2. 改进文笔和叙述技巧
3. 增强人物刻画和对话
4. 提升整体可读性

{f'特殊要求：{instructions}' if instructions else ''}

请直接开始写章节内容，不需要章节标题。
"""
            
            # 调用AI模型重新生成
            from ..ai.model_client import ai_model_manager, AIModelType
            
            response = await ai_model_manager.chat_with_model(
                model_type=AIModelType.WRITER,
                prompt=regenerate_prompt,
                system_prompt=f"你是一个专业的小说作者，擅长写作{project.genre.value}类型的小说。请重新生成高质量的小说章节。",
                max_tokens=8000,
                temperature=0.7
            )
            
            if not response.success:
                raise Exception(f"章节重新生成失败: {response.error_message}")
            
            new_content = response.content
            
            # 更新章节内容
            chapter.content = new_content
            chapter.word_count = len(new_content)
            
            # 重新评估质量
            new_quality_score = await self.quality_monitor.evaluate_chapter_quality(chapter)
            chapter.quality_score = new_quality_score
            
            self.logger.info(f"Regenerated chapter: {chapter_id}")
            return new_content
            
        except Exception as e:
            self.logger.error(f"Failed to regenerate chapter {chapter_id}: {e}")
            raise

    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """获取项目状态"""
        try:
            if project_id not in self.active_projects:
                return {"error": "项目不存在"}
            
            project = self.active_projects[project_id]
            chapters = self.novel_content.get(project_id, [])
            
            # 计算进度
            expected_chapters = {
                "short": 5,
                "medium": 15, 
                "long": 30,
                "epic": 50
            }.get(project.length.value, 15)
            
            progress = min(100, (len(chapters) / expected_chapters) * 100)
            
            return {
                "project_id": project_id,
                "project": project.to_dict(),
                "statistics": {
                    "total_chapters": len(chapters),
                    "expected_chapters": expected_chapters,
                    "progress_percentage": round(progress, 2),
                    "total_words": sum(ch.word_count for ch in chapters),
                    "completed_chapters": len([ch for ch in chapters if ch.status == "completed"]),
                    "draft_chapters": len([ch for ch in chapters if ch.status == "draft"])
                },
                "status": project.status,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project status: {e}")
            raise

    async def export_novel(self, project_id: str, format: str = "txt") -> str:
        """导出小说"""
        try:
            if project_id not in self.active_projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.active_projects[project_id]
            chapters = self.novel_content.get(project_id, [])
            
            if not chapters:
                raise ValueError("没有章节内容可导出")
            
            # 创建导出目录
            os.makedirs("./exports", exist_ok=True)
            
            # 生成导出文件
            export_filename = f"{project.title}_{project_id}.{format}"
            export_path = f"./exports/{export_filename}"
            
            if format.lower() == "txt":
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write(f"《{project.title}》\n")
                    f.write(f"作者：多AI协同小说生成系统\n")
                    f.write(f"类型：{project.genre.value}\n")
                    f.write(f"主题：{project.theme}\n")
                    f.write(f"目标受众：{project.target_audience}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for chapter in chapters:
                        f.write(f"第{chapter.chapter_number}章 {chapter.title}\n")
                        f.write("-" * 30 + "\n")
                        f.write(chapter.content)
                        f.write("\n\n")
            
            self.logger.info(f"Exported novel {project_id} to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Failed to export novel {project_id}: {e}")
            raise

    # 用户管理相关方法
    async def get_user_projects(self, user_id: str) -> List[NovelProject]:
        """获取用户的所有项目"""
        try:
            user_projects = []
            for project in self.active_projects.values():
                if hasattr(project, 'user_id') and project.user_id == user_id:
                    user_projects.append(project)
            return user_projects
        except Exception as e:
            self.logger.error(f"Failed to get user projects: {e}")
            raise

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            user_projects = await self.get_user_projects(user_id)
            
            total_projects = len(user_projects)
            completed_projects = sum(1 for p in user_projects if p.status == "completed")
            active_projects = sum(1 for p in user_projects if p.status == "generating")
            
            total_chapters = 0
            total_words = 0
            
            for project in user_projects:
                chapters = self.novel_content.get(project.project_id, [])
                total_chapters += len(chapters)
                total_words += sum(ch.word_count for ch in chapters)
            
            return {
                "total_projects": total_projects,
                "completed_projects": completed_projects,
                "active_projects": active_projects,
                "total_chapters": total_chapters,
                "total_words": total_words
            }
        except Exception as e:
            self.logger.error(f"Failed to get user statistics: {e}")
            raise

    # 配置管理相关方法
    async def get_system_configuration(self) -> Dict[str, Any]:
        """获取系统配置"""
        try:
            config = {
                "app_name": getattr(self.settings, 'app_name', '多AI协同小说生成系统'),
                "debug": getattr(self.settings, 'debug', False),
                "max_concurrent_projects": getattr(self.settings, 'max_concurrent_projects', 10),
                "default_language": getattr(self.settings, 'default_language', 'zh-CN'),
                "quality_threshold": getattr(self.settings, 'quality_threshold', 0.7),
                "redis_url": getattr(self.settings, 'redis_url', None),
                "database_url": getattr(self.settings, 'database_url', None),
                "ai_model_config": getattr(self.settings, 'ai_model_config', {}),
                "engine_version": "0.1.0",
                "supported_genres": [genre.value for genre in NovelGenre],
                "supported_lengths": [length.value for length in NovelLength]
            }
            return config
        except Exception as e:
            self.logger.error(f"Failed to get system configuration: {e}")
            raise

    async def update_system_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """更新系统配置"""
        try:
            # 验证配置更新
            allowed_keys = {
                'max_concurrent_projects', 'default_language', 'quality_threshold',
                'debug', 'app_name'
            }
            
            invalid_keys = set(config_updates.keys()) - allowed_keys
            if invalid_keys:
                raise ValueError(f"不允许的配置项: {', '.join(invalid_keys)}")
            
            # 这里应该实际更新配置文件或数据库
            # 目前只记录更新操作
            self.logger.info(f"Updated system configuration: {config_updates}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update system configuration: {e}")
            raise

    async def get_ai_model_configuration(self) -> Dict[str, Any]:
        """获取AI模型配置"""
        try:
            model_config = {}
            
            # 获取AI模型状态
            for model_type in AIModelType:
                status = self.ai_manager.get_model_status().get(model_type.value, {})
                model_config[model_type.value] = {
                    "available": status.get("available", False),
                    "model_name": status.get("model_name", ""),
                    "temperature": status.get("temperature", 0.7),
                    "max_tokens": status.get("max_tokens", 4000),
                    "api_key_configured": bool(status.get("api_key"))
                }
            
            return model_config
            
        except Exception as e:
            self.logger.error(f"Failed to get AI model configuration: {e}")
            raise

    async def update_ai_model_configuration(self, model_updates: Dict[str, Any]) -> bool:
        """更新AI模型配置"""
        try:
            # 验证模型配置更新
            valid_models = {model_type.value for model_type in AIModelType}
            invalid_models = set(model_updates.keys()) - valid_models
            if invalid_models:
                raise ValueError(f"不支持的模型类型: {', '.join(invalid_models)}")
            
            # 验证配置参数
            for model_type, config in model_updates.items():
                if not isinstance(config, dict):
                    raise ValueError(f"模型 {model_type} 的配置必须是字典格式")
                
                valid_params = {"temperature", "max_tokens", "api_key"}
                invalid_params = set(config.keys()) - valid_params
                if invalid_params:
                    raise ValueError(f"模型 {model_type} 不支持的参数: {', '.join(invalid_params)}")
            
            # 这里应该实际更新模型配置
            self.logger.info(f"Updated AI model configuration: {model_updates}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update AI model configuration: {e}")
            raise