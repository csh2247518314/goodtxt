"""
数据库初始化脚本
创建GoodTxt系统所需的数据库表结构
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime


def create_database():
    """创建数据库连接"""
    # 确保数据库目录存在
    db_dir = Path("./data/database")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = db_dir / "goodtxt.db"
    
    conn = sqlite3.connect(str(db_path))
    return conn


def create_users_table(conn):
    """创建用户表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP NOT NULL,
        last_login TIMESTAMP,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        api_key TEXT UNIQUE NOT NULL,
        settings TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)")
    
    print("✅ 用户表创建完成")


def create_projects_table(conn):
    """创建项目表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        length TEXT NOT NULL,
        theme TEXT NOT NULL,
        target_audience TEXT NOT NULL,
        language TEXT DEFAULT 'zh-CN',
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)")
    
    print("✅ 项目表创建完成")


def create_chapters_table(conn):
    """创建章节表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        chapter_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        chapter_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        word_count INTEGER NOT NULL,
        quality_score REAL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        generated_at TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_project_id ON chapters(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_created_at ON chapters(created_at)")
    
    print("✅ 章节表创建完成")


def create_tokens_table(conn):
    """创建用户令牌表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_tokens (
        token_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        token_type TEXT NOT NULL DEFAULT 'access',
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user_id ON user_tokens(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expires_at ON user_tokens(expires_at)")
    
    print("✅ 用户令牌表创建完成")


def create_system_logs_table(conn):
    """创建系统日志表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        log_id TEXT PRIMARY KEY,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        source TEXT DEFAULT 'app',
        user_id TEXT,
        project_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT DEFAULT '{}'
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system_logs(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_id ON system_logs(user_id)")
    
    print("✅ 系统日志表创建完成")


def create_quality_reports_table(conn):
    """创建质量报告表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quality_reports (
        report_id TEXT PRIMARY KEY,
        chapter_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        quality_score REAL NOT NULL,
        quality_level TEXT NOT NULL,
        report_details TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE CASCADE,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_chapter_id ON quality_reports(chapter_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_project_id ON quality_reports(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_score ON quality_reports(quality_score)")
    
    print("✅ 质量报告表创建完成")


def create_memory_table(conn):
    """创建记忆表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        memory_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        keywords TEXT DEFAULT '',
        importance_score REAL DEFAULT 0.5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT DEFAULT '{}'
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_importance ON memory(importance_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(created_at)")
    
    print("✅ 记忆表创建完成")


def create_agent_performance_table(conn):
    """创建AI代理性能表"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_performance (
        record_id TEXT PRIMARY KEY,
        agent_type TEXT NOT NULL,
        task_type TEXT NOT NULL,
        success BOOLEAN NOT NULL,
        response_time REAL,
        tokens_used INTEGER,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT DEFAULT '{}'
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_performance_type ON agent_performance(agent_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_performance_success ON agent_performance(success)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_performance_created_at ON agent_performance(created_at)")
    
    print("✅ AI代理性能表创建完成")


def init_database():
    """初始化数据库"""
    try:
        print("🚀 开始初始化GoodTxt数据库...")
        
        conn = create_database()
        
        # 创建所有表
        create_users_table(conn)
        create_projects_table(conn)
        create_chapters_table(conn)
        create_tokens_table(conn)
        create_system_logs_table(conn)
        create_quality_reports_table(conn)
        create_memory_table(conn)
        create_agent_performance_table(conn)
        
        # 提交更改
        conn.commit()
        
        print("\n🎉 数据库初始化完成！")
        print(f"数据库文件位置: {os.path.abspath('./data/database/goodtxt.db')}")
        print("\n📊 创建的表结构:")
        print("- users: 用户信息表")
        print("- projects: 项目表")
        print("- chapters: 章节表")
        print("- user_tokens: 用户令牌表")
        print("- system_logs: 系统日志表")
        print("- quality_reports: 质量报告表")
        print("- memory: 记忆表")
        print("- agent_performance: AI代理性能表")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


if __name__ == "__main__":
    init_database()
