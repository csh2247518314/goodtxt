"""
GoodTxt 数据库模块
提供数据库连接和管理功能
"""

from .db_manager import (
    DatabaseManager,
    UserDatabaseManager,
    ProjectDatabaseManager,
    ChapterDatabaseManager,
    db_manager,
    user_db,
    project_db,
    chapter_db
)

__all__ = [
    'DatabaseManager',
    'UserDatabaseManager', 
    'ProjectDatabaseManager',
    'ChapterDatabaseManager',
    'db_manager',
    'user_db',
    'project_db',
    'chapter_db'
]
