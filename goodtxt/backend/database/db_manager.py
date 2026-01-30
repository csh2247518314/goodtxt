"""
数据库连接管理器
负责GoodTxt系统的所有数据库操作
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..config.settings import get_settings


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self._get_db_path()
        self._ensure_db_directory()
    
    def _get_db_path(self) -> Path:
        """获取数据库文件路径"""
        return Path(self.settings.db.sqlite_path)
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 返回字典格式的行
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询SQL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新SQL，返回影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> str:
        """执行插入SQL，返回插入的记录ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid


class UserDatabaseManager(DatabaseManager):
    """用户数据库操作管理器"""
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """创建用户"""
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        query = """
        INSERT INTO users (
            user_id, username, email, password_hash, role,
            created_at, last_login, is_active, api_key, settings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user_id,
            user_data['username'],
            user_data['email'],
            user_data['password_hash'],
            user_data.get('role', 'user'),
            datetime.now(),
            None,
            True,
            user_data['api_key'],
            json.dumps(user_data.get('settings', {}))
        )
        
        self.execute_insert(query, params)
        return user_id
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        results = self.execute_query(query, (username,))
        return results[0] if results else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        query = "SELECT * FROM users WHERE email = ? AND is_active = 1"
        results = self.execute_query(query, (email,))
        return results[0] if results else None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE user_id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """根据API密钥获取用户"""
        query = "SELECT * FROM users WHERE api_key = ? AND is_active = 1"
        results = self.execute_query(query, (api_key,))
        return results[0] if results else None
    
    def update_user_login_time(self, user_id: str):
        """更新用户最后登录时间"""
        query = "UPDATE users SET last_login = ? WHERE user_id = ?"
        self.execute_update(query, (datetime.now(), user_id))
    
    def update_user_settings(self, user_id: str, settings: Dict[str, Any]):
        """更新用户设置"""
        query = "UPDATE users SET settings = ?, updated_at = ? WHERE user_id = ?"
        self.execute_update(query, (json.dumps(settings), datetime.now(), user_id))
    
    def update_user_role(self, user_id: str, role: str):
        """更新用户角色"""
        query = "UPDATE users SET role = ?, updated_at = ? WHERE user_id = ?"
        self.execute_update(query, (role, datetime.now(), user_id))
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户（软删除）"""
        query = "UPDATE users SET is_active = 0, updated_at = ? WHERE user_id = ?"
        return self.execute_update(query, (datetime.now(), user_id)) > 0
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        query = "SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC"
        return self.execute_query(query)
    
    def check_username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        query = "SELECT 1 FROM users WHERE username = ? AND is_active = 1"
        results = self.execute_query(query, (username,))
        return len(results) > 0
    
    def check_email_exists(self, email: str) -> bool:
        """检查邮箱是否存在"""
        query = "SELECT 1 FROM users WHERE email = ? AND is_active = 1"
        results = self.execute_query(query, (email,))
        return len(results) > 0


class ProjectDatabaseManager(DatabaseManager):
    """项目数据库操作管理器"""
    
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """创建项目"""
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        
        query = """
        INSERT INTO projects (
            project_id, user_id, title, genre, length, theme,
            target_audience, language, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            project_id,
            project_data['user_id'],
            project_data['title'],
            project_data['genre'],
            project_data['length'],
            project_data['theme'],
            project_data['target_audience'],
            project_data.get('language', 'zh-CN'),
            'draft',
            datetime.now()
        )
        
        self.execute_insert(query, params)
        return project_id
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """根据ID获取项目"""
        query = "SELECT * FROM projects WHERE project_id = ?"
        results = self.execute_query(query, (project_id,))
        return results[0] if results else None
    
    def get_user_projects(self, user_id: str, limit: int = 50) -> List[Dict]:
        """获取用户的所有项目"""
        query = """
        SELECT p.*, 
               COUNT(c.chapter_id) as chapters_count,
               COALESCE(SUM(c.word_count), 0) as total_words
        FROM projects p
        LEFT JOIN chapters c ON p.project_id = c.project_id
        WHERE p.user_id = ?
        GROUP BY p.project_id
        ORDER BY p.updated_at DESC
        LIMIT ?
        """
        return self.execute_query(query, (user_id, limit))
    
    def update_project_status(self, project_id: str, status: str):
        """更新项目状态"""
        query = "UPDATE projects SET status = ?, updated_at = ? WHERE project_id = ?"
        self.execute_update(query, (status, datetime.now(), project_id))
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        query = "DELETE FROM projects WHERE project_id = ?"
        return self.execute_update(query, (project_id,)) > 0


class ChapterDatabaseManager(DatabaseManager):
    """章节数据库操作管理器"""
    
    def create_chapter(self, chapter_data: Dict[str, Any]) -> str:
        """创建章节"""
        chapter_id = f"ch_{uuid.uuid4().hex[:12]}"
        
        query = """
        INSERT INTO chapters (
            chapter_id, project_id, chapter_number, title, content,
            word_count, quality_score, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            chapter_id,
            chapter_data['project_id'],
            chapter_data['chapter_number'],
            chapter_data['title'],
            chapter_data['content'],
            chapter_data['word_count'],
            chapter_data.get('quality_score', 0.0),
            chapter_data.get('status', 'draft'),
            datetime.now()
        )
        
        self.execute_insert(query, params)
        return chapter_id
    
    def get_chapters_by_project(self, project_id: str) -> List[Dict]:
        """获取项目的所有章节"""
        query = """
        SELECT * FROM chapters 
        WHERE project_id = ?
        ORDER BY chapter_number ASC
        """
        return self.execute_query(query, (project_id,))
    
    def get_chapter_by_id(self, chapter_id: str) -> Optional[Dict]:
        """根据ID获取章节"""
        query = "SELECT * FROM chapters WHERE chapter_id = ?"
        results = self.execute_query(query, (chapter_id,))
        return results[0] if results else None
    
    def update_chapter_content(self, chapter_id: str, content: str, word_count: int):
        """更新章节内容"""
        query = """
        UPDATE chapters 
        SET content = ?, word_count = ?, updated_at = ?
        WHERE chapter_id = ?
        """
        self.execute_update(query, (content, word_count, datetime.now(), chapter_id))
    
    def update_chapter_quality(self, chapter_id: str, quality_score: float):
        """更新章节质量分数"""
        query = """
        UPDATE chapters 
        SET quality_score = ?, updated_at = ?
        WHERE chapter_id = ?
        """
        self.execute_update(query, (quality_score, datetime.now(), chapter_id))


# 全局数据库管理器实例
db_manager = DatabaseManager()
user_db = UserDatabaseManager()
project_db = ProjectDatabaseManager()
chapter_db = ChapterDatabaseManager()
