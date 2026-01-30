"""
FastAPI应用入口

提供REST API接口给小说生成系统
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from ..engine.novel_generator import NovelGenerationEngine, NovelProject, NovelGenre, NovelLength
from ..quality.quality_monitor import QualityMonitor
from ..memory.memory_manager import MemoryManager
from ..config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Starting Multi-AI Novel Generator API")
    
    # 等待依赖服务启动
    await _wait_for_dependencies()
    
    # 初始化核心组件
    app.state.novel_engine = NovelGenerationEngine()
    app.state.quality_monitor = QualityMonitor()
    app.state.memory_manager = MemoryManager()
    
    logger.info("Multi-AI Novel Generator API started")
    
    yield
    
    # 关闭时清理
    logger.info("Shutting down Multi-AI Novel Generator API")
    
    # 清理资源（如果需要的话）
    # await app.state.novel_engine.cleanup()


async def _wait_for_dependencies():
    """等待依赖服务启动完成"""
    import asyncio
    import redis
    import aiohttp
    
    max_retries = 30  # 最多等待30秒
    retry_interval = 2  # 每2秒重试一次
    
    logger.info("Waiting for dependencies to start...")
    
    # 等待Redis
    for i in range(max_retries):
        try:
            settings = get_settings()
            r = redis.Redis(
                host=settings.db.redis_host,
                port=settings.db.redis_port,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            r.ping()
            logger.info("✓ Redis connection established")
            break
        except Exception as e:
            if i == max_retries - 1:
                logger.error(f"Redis connection failed after {max_retries} retries: {e}")
                # 不抛出异常，让应用继续启动，但记录错误
            else:
                logger.warning(f"Redis not ready, retrying... ({i+1}/{max_retries})")
                await asyncio.sleep(retry_interval)
    
    # 等待ChromaDB
    for i in range(max_retries):
        try:
            settings = get_settings()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{settings.db.chroma_host}:{settings.db.chroma_port}/v2/heartbeat") as response:
                    if response.status == 200:
                        logger.info("✓ ChromaDB connection established")
                        break
        except Exception as e:
            if i == max_retries - 1:
                logger.error(f"ChromaDB connection failed after {max_retries} retries: {e}")
                # 不抛出异常，让应用继续启动，但记录错误
            else:
                logger.warning(f"ChromaDB not ready, retrying... ({i+1}/{max_retries})")
                await asyncio.sleep(retry_interval)
    
    logger.info("Dependencies check completed")


# 创建FastAPI应用
app = FastAPI(
    title="多AI协同小说生成系统",
    description="基于多AI协同的智能小说生成系统",
    version="0.1.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局日志配置
logger = structlog.get_logger()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "多AI协同小说生成系统 API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查核心组件状态
        novel_engine = app.state.novel_engine
        quality_monitor = app.state.quality_monitor
        memory_manager = app.state.memory_manager
        
        return {
            "status": "healthy",
            "components": {
                "novel_engine": "ok",
                "quality_monitor": "ok",
                "memory_manager": "ok"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/projects")
async def create_novel_project(project_config: Dict[str, Any]):
    """创建小说项目"""
    try:
        novel_engine = app.state.novel_engine
        
        # 验证必需字段
        required_fields = ["title", "genre", "length", "theme", "target_audience"]
        for field in required_fields:
            if field not in project_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # 创建项目
        project_id = await novel_engine.create_novel_project(project_config)
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": "项目创建成功"
        }
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/generate")
async def generate_novel(
    project_id: str, 
    background_tasks: BackgroundTasks,
    chapter_count: Optional[int] = None
):
    """开始小说生成"""
    try:
        novel_engine = app.state.novel_engine
        
        # 检查项目是否存在
        if project_id not in novel_engine.active_projects:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 启动后台生成任务
        background_tasks.add_task(
            novel_engine.execute_novel_generation,
            project_id,
            chapter_count
        )
        
        return {
            "status": "started",
            "project_id": project_id,
            "message": "小说生成已开始",
            "chapter_count": chapter_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start novel generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}")
async def get_project_status(project_id: str):
    """获取项目状态"""
    try:
        novel_engine = app.state.novel_engine
        
        status = await novel_engine.get_project_status(project_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/projects/{project_id}")
async def update_project(project_id: str, project_data: Dict[str, Any]):
    """更新项目"""
    try:
        novel_engine = app.state.novel_engine
        
        if project_id not in novel_engine.active_projects:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = novel_engine.active_projects[project_id]
        
        # 更新允许的字段
        if "title" in project_data:
            project.title = project_data["title"]
        if "theme" in project_data:
            project.theme = project_data["theme"]
        if "target_audience" in project_data:
            project.target_audience = project_data["target_audience"]
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": "项目更新成功",
            "project": project.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    try:
        novel_engine = app.state.novel_engine
        
        if project_id not in novel_engine.active_projects:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 删除项目
        del novel_engine.active_projects[project_id]
        
        # 删除相关章节
        if project_id in novel_engine.novel_content:
            del novel_engine.novel_content[project_id]
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": "项目删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/status")
async def get_project_detailed_status(project_id: str):
    """获取项目详细状态"""
    try:
        novel_engine = app.state.novel_engine
        
        if project_id not in novel_engine.active_projects:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = novel_engine.active_projects[project_id]
        chapters = novel_engine.novel_content.get(project_id, [])
        
        # 计算详细统计
        total_words = sum(ch.word_count for ch in chapters)
        avg_quality = sum(ch.quality_score for ch in chapters) / len(chapters) if chapters else 0
        
        # 计算生成进度
        expected_chapters = {
            "short": 5,
            "medium": 15, 
            "long": 30,
            "epic": 50
        }.get(project.length.value, 15)
        
        progress = min(100, (len(chapters) / expected_chapters) * 100)
        
        return {
            "project_id": project_id,
            "project": {
                "project_id": project.project_id,
                "title": project.title,
                "genre": project.genre.value,
                "length": project.length.value,
                "theme": project.theme,
                "target_audience": project.target_audience,
                "language": project.language,
                "status": project.status,
                "created_at": project.created_at.isoformat()
            },
            "statistics": {
                "total_chapters": len(chapters),
                "expected_chapters": expected_chapters,
                "progress_percentage": round(progress, 2),
                "total_words": total_words,
                "average_quality": round(avg_quality, 2),
                "completed_chapters": len([ch for ch in chapters if ch.status == "completed"]),
                "draft_chapters": len([ch for ch in chapters if ch.status == "draft"])
            },
            "chapters": [chapter.to_dict() for chapter in chapters],
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project detailed status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/chapters")
async def get_project_chapters(project_id: str):
    """获取项目章节"""
    try:
        novel_engine = app.state.novel_engine
        
        if project_id not in novel_engine.novel_content:
            return {"chapters": []}
        
        chapters = novel_engine.novel_content[project_id]
        
        return {
            "project_id": project_id,
            "chapters": [chapter.to_dict() for chapter in chapters],
            "total_chapters": len(chapters)
        }
        
    except Exception as e:
        logger.error(f"Failed to get project chapters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    """获取单个章节"""
    try:
        novel_engine = app.state.novel_engine
        
        # 在所有项目中查找章节
        for project_chapters in novel_engine.novel_content.values():
            for chapter in project_chapters:
                if chapter.chapter_id == chapter_id:
                    return chapter.to_dict()
        
        raise HTTPException(status_code=404, detail="章节不存在")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chapters/{chapter_id}/quality")
async def evaluate_chapter_quality(chapter_id: str):
    """评估章节质量"""
    try:
        novel_engine = app.state.novel_engine
        quality_monitor = app.state.quality_monitor
        
        # 查找章节
        chapter = None
        for project_chapters in novel_engine.novel_content.values():
            for ch in project_chapters:
                if ch.chapter_id == chapter_id:
                    chapter = ch
                    break
            if chapter:
                break
        
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 评估质量
        quality_score = await quality_monitor.evaluate_chapter_quality(chapter)
        
        return {
            "chapter_id": chapter_id,
            "quality_score": quality_score,
            "quality_level": quality_monitor._get_quality_level(quality_score)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate chapter quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/chapters/{chapter_id}")
async def update_chapter(chapter_id: str, content: str):
    """更新章节内容"""
    try:
        novel_engine = app.state.novel_engine
        
        # 查找章节
        chapter = None
        for project_chapters in novel_engine.novel_content.values():
            for ch in project_chapters:
                if ch.chapter_id == chapter_id:
                    chapter = ch
                    break
            if chapter:
                break
        
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 更新章节内容
        chapter.content = content
        chapter.word_count = len(content)
        
        return {
            "status": "success",
            "chapter_id": chapter_id,
            "message": "章节更新成功",
            "chapter": chapter.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chapters/{chapter_id}/regenerate")
async def regenerate_chapter(chapter_id: str, instructions: Optional[str] = None):
    """重新生成章节"""
    try:
        novel_engine = app.state.novel_engine
        
        # 查找章节和所属项目
        chapter = None
        project_id = None
        for proj_id, project_chapters in novel_engine.novel_content.items():
            for ch in project_chapters:
                if ch.chapter_id == chapter_id:
                    chapter = ch
                    project_id = proj_id
                    break
            if chapter:
                break
        
        if not chapter or not project_id:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        project = novel_engine.active_projects[project_id]
        
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
        quality_monitor = app.state.quality_monitor
        new_quality_score = await quality_monitor.evaluate_chapter_quality(chapter)
        chapter.quality_score = new_quality_score
        
        return {
            "status": "success",
            "chapter_id": chapter_id,
            "message": "章节重新生成成功",
            "old_quality_score": chapter.quality_score,
            "new_quality_score": new_quality_score,
            "chapter": chapter.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/export")
async def export_novel(project_id: str, format: str = "txt"):
    """导出小说"""
    try:
        novel_engine = app.state.novel_engine
        
        # 检查项目是否存在
        if project_id not in novel_engine.active_projects:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 导出小说
        export_path = await novel_engine.export_novel(project_id, format)
        
        return {
            "status": "success",
            "project_id": project_id,
            "export_path": export_path,
            "format": format
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export novel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/search")
async def search_memory(query: str, category: Optional[str] = None):
    """搜索记忆"""
    try:
        memory_manager = app.state.memory_manager
        
        # 解析类别
        from ..memory.memory_manager import MemoryCategory
        memory_category = None
        if category:
            try:
                memory_category = MemoryCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail="无效的记忆类别")
        
        # 搜索记忆
        memories = await memory_manager.search_memories(
            query=query,
            category=memory_category
        )
        
        return {
            "query": query,
            "category": category,
            "results": memories
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    try:
        novel_engine = app.state.novel_engine
        
        # 获取系统统计
        framework_stats = novel_engine.framework.get_workflow_status("test")
        communication_stats = novel_engine.framework.communication_hub.get_communication_stats()
        scheduler_stats = novel_engine.framework.task_scheduler.get_scheduler_stats()
        
        return {
            "system": {
                "status": "running",
                "timestamp": datetime.now().isoformat()
            },
            "framework": framework_stats,
            "communication": communication_stats,
            "scheduler": scheduler_stats,
            "projects": {
                "active": len(novel_engine.active_projects),
                "completed": sum(1 for p in novel_engine.active_projects.values() if p.status == "completed")
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/metrics")
async def get_system_metrics():
    """获取系统指标"""
    try:
        import psutil
        import os
        
        novel_engine = app.state.novel_engine
        
        # 系统指标
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 应用指标
        total_projects = len(novel_engine.active_projects)
        total_chapters = sum(len(chapters) for chapters in novel_engine.novel_content.values())
        total_words = sum(
            sum(ch.word_count for ch in chapters)
            for chapters in novel_engine.novel_content.values()
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
                "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2)
            },
            "application": {
                "total_projects": total_projects,
                "total_chapters": total_chapters,
                "total_words": total_words,
                "active_projects": sum(1 for p in novel_engine.active_projects.values() if p.status == "draft"),
                "generating_projects": sum(1 for p in novel_engine.active_projects.values() if p.status == "generating"),
                "completed_projects": sum(1 for p in novel_engine.active_projects.values() if p.status == "completed")
            }
        }
        
    except ImportError:
        # 如果psutil未安装，返回基础指标
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "status": "指标监控不可用（缺少psutil依赖）"
            },
            "application": {
                "total_projects": len(novel_engine.active_projects),
                "total_chapters": sum(len(chapters) for chapters in novel_engine.novel_content.values()),
                "total_words": sum(
                    sum(ch.word_count for ch in chapters)
                    for chapters in novel_engine.novel_content.values()
                )
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/logs")
async def get_system_logs(limit: int = 100, level: Optional[str] = None):
    """获取系统日志"""
    try:
        import os
        
        # 获取最近的日志条目（简化实现）
        logs = []
        
        # 这里应该从实际日志文件中读取日志
        # 目前返回模拟日志
        sample_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "系统启动成功",
                "source": "app"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO", 
                "message": "AI模型初始化完成",
                "source": "ai"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "数据库连接正常",
                "source": "db"
            }
        ]
        
        # 按级别过滤
        if level:
            sample_logs = [log for log in sample_logs if log["level"] == level.upper()]
        
        # 限制数量
        logs = sample_logs[:limit]
        
        return {
            "logs": logs,
            "total": len(logs),
            "level_filter": level,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 认证相关API
@app.post("/auth/login")
async def login(credentials: Dict[str, Any]):
    """用户登录"""
    try:
        from ..auth.auth_manager import auth_manager
        
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="用户名和密码不能为空")
        
        user = auth_manager.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        token = auth_manager.generate_token(user.user_id)
        
        return {
            "status": "success",
            "token": token,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "settings": user.settings
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/register")
async def register(user_data: Dict[str, Any]):
    """用户注册"""
    try:
        from ..auth.auth_manager import auth_manager, UserRole
        
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="用户名、邮箱和密码不能为空")
        
        user = auth_manager.create_user(username, email, password)
        
        return {
            "status": "success",
            "message": "注册成功",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/me")
async def get_current_user(request: Request):
    """获取当前用户信息"""
    try:
        from ..auth.auth_manager import auth_manager
        
        # 从请求头获取令牌
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="未提供认证令牌")
        
        token = auth_header.split(" ")[1]
        user = auth_manager.get_user_by_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="无效或过期的令牌")
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "settings": user.settings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def get_agents():
    """获取AI代理状态"""
    try:
        from ..ai.model_client import ai_model_manager
        
        agent_status = ai_model_manager.get_model_status()
        
        return {
            "agents": agent_status,
            "total_agents": len(agent_status)
        }
        
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/models/{model_type}/test")
async def test_model_connection(model_type: str):
    """测试AI模型连接"""
    try:
        from ..ai.model_client import ai_model_manager, AIModelType
        
        # 转换模型类型
        try:
            model_enum = AIModelType(model_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"不支持的模型类型: {model_type}")
        
        result = ai_model_manager.test_model_connection(model_enum)
        
        return {
            "model_type": model_type,
            "test_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quality/history")
async def get_quality_history(limit: int = 50):
    """获取质量历史"""
    try:
        quality_monitor = app.state.quality_monitor
        
        history = quality_monitor.quality_history[-limit:]
        
        return {
            "history": [report.to_dict() for report in history],
            "total_reports": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 用户管理相关API
@app.get("/users")
async def get_users_list():
    """获取用户列表"""
    try:
        from ..auth.auth_manager import auth_manager
        
        users = auth_manager.get_all_users()
        
        return {
            "users": [
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "is_active": user.is_active
                }
                for user in users
            ],
            "total_users": len(users)
        }
        
    except Exception as e:
        logger.error(f"Failed to get users list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role_data: Dict[str, Any]):
    """更新用户角色"""
    try:
        from ..auth.auth_manager import auth_manager, UserRole
        
        new_role = role_data.get("role")
        if not new_role:
            raise HTTPException(status_code=400, detail="角色不能为空")
        
        try:
            role_enum = UserRole(new_role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的角色: {new_role}")
        
        success = auth_manager.update_user_role(user_id, role_enum)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "status": "success",
            "user_id": user_id,
            "new_role": new_role,
            "message": "用户角色更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """删除用户"""
    try:
        from ..auth.auth_manager import auth_manager
        
        success = auth_manager.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "status": "success",
            "user_id": user_id,
            "message": "用户删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """获取用户统计信息"""
    try:
        from ..auth.auth_manager import auth_manager
        
        # 验证用户是否存在
        user = auth_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        novel_engine = app.state.novel_engine
        
        # 统计用户相关的项目和章节
        user_projects = []
        user_chapters = []
        
        for project_id, project in novel_engine.active_projects.items():
            if hasattr(project, 'user_id') and project.user_id == user_id:
                user_projects.append(project_id)
                chapters = novel_engine.novel_content.get(project_id, [])
                user_chapters.extend([ch.chapter_id for ch in chapters])
        
        return {
            "user_id": user_id,
            "username": user.username,
            "statistics": {
                "total_projects": len(user_projects),
                "total_chapters": len(user_chapters),
                "completed_projects": sum(1 for p_id in user_projects 
                                        if novel_engine.active_projects[p_id].status == "completed"),
                "active_projects": sum(1 for p_id in user_projects 
                                     if novel_engine.active_projects[p_id].status == "generating"),
                "total_words": sum(
                    sum(ch.word_count for ch in novel_engine.novel_content.get(p_id, []))
                    for p_id in user_projects
                )
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 配置管理相关API
@app.get("/config")
async def get_system_config():
    """获取系统配置"""
    try:
        from ..config.settings import get_settings
        
        settings = get_settings()
        
        return {
            "config": {
                "app_name": getattr(settings, 'app_name', '多AI协同小说生成系统'),
                "debug": getattr(settings, 'debug', False),
                "max_concurrent_projects": getattr(settings, 'max_concurrent_projects', 10),
                "default_language": getattr(settings, 'default_language', 'zh-CN'),
                "quality_threshold": getattr(settings, 'quality_threshold', 0.7),
                "redis_url": getattr(settings, 'redis_url', None),
                "database_url": getattr(settings, 'database_url', None),
                "ai_model_config": getattr(settings, 'ai_model_config', {})
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/config")
async def update_system_config(config_data: Dict[str, Any]):
    """更新系统配置"""
    try:
        # 验证配置数据
        allowed_keys = {
            'max_concurrent_projects', 'default_language', 'quality_threshold',
            'debug', 'app_name'
        }
        
        invalid_keys = set(config_data.keys()) - allowed_keys
        if invalid_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"不允许的配置项: {', '.join(invalid_keys)}"
            )
        
        # 这里应该实际更新配置文件或数据库
        # 目前返回成功响应
        return {
            "status": "success",
            "updated_config": config_data,
            "message": "系统配置更新成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config/models")
async def get_ai_models_config():
    """获取AI模型配置"""
    try:
        from ..ai.model_client import ai_model_manager
        
        model_status = ai_model_manager.get_model_status()
        
        # 提取模型配置信息
        model_config = {}
        for model_type, status in model_status.items():
            model_config[model_type] = {
                "available": status.get("available", False),
                "model_name": status.get("model_name", ""),
                "temperature": status.get("temperature", 0.7),
                "max_tokens": status.get("max_tokens", 4000),
                "api_key_configured": bool(status.get("api_key"))
            }
        
        return {
            "models": model_config,
            "total_models": len(model_config),
            "available_models": sum(1 for m in model_config.values() if m["available"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI models config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/config/models")
async def update_ai_models_config(model_config: Dict[str, Any]):
    """更新AI模型配置"""
    try:
        from ..ai.model_client import ai_model_manager
        
        # 验证模型配置
        valid_models = {"writer", "editor", "planner", "reviewer"}
        invalid_models = set(model_config.keys()) - valid_models
        if invalid_models:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型类型: {', '.join(invalid_models)}"
            )
        
        # 更新模型配置
        updated_models = []
        for model_type, config in model_config.items():
            if not isinstance(config, dict):
                raise HTTPException(
                    status_code=400,
                    detail=f"模型 {model_type} 的配置必须是字典格式"
                )
            
            # 验证配置参数
            valid_params = {"temperature", "max_tokens", "api_key"}
            invalid_params = set(config.keys()) - valid_params
            if invalid_params:
                raise HTTPException(
                    status_code=400,
                    detail=f"模型 {model_type} 不支持的参数: {', '.join(invalid_params)}"
                )
            
            updated_models.append({
                "model_type": model_type,
                "config": config
            })
        
        # 这里应该实际更新模型配置
        # 目前返回成功响应
        return {
            "status": "success",
            "updated_models": updated_models,
            "message": "AI模型配置更新成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update AI models config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config/reset")
async def reset_system_config():
    """重置系统配置为默认值"""
    try:
        # 这里应该重置配置文件为默认值
        # 目前返回成功响应
        return {
            "status": "success",
            "message": "系统配置已重置为默认值",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to reset system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)