"""
GoodTxt 数据库初始化脚本
创建和初始化所有必需的数据库
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.db_dir = self.data_dir / "database"
        self.chroma_dir = self.data_dir / "chroma"
        self.exports_dir = self.data_dir / "exports"
        
        # 创建数据目录
        self.data_dir.mkdir(exist_ok=True)
        self.db_dir.mkdir(exist_ok=True)
        self.chroma_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        
        self.sqlite_path = self.db_dir / "goodtxt.db"
        
    def create_sqlite_tables(self):
        """创建SQLite数据库表"""
        print("📦 创建SQLite数据库表...")
        
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1,
                api_key TEXT,
                settings TEXT
            )
        ''')
        
        # 项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                genre TEXT NOT NULL,
                length TEXT NOT NULL,
                theme TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                language TEXT DEFAULT '中文',
                status TEXT DEFAULT 'draft',
                progress REAL DEFAULT 0.0,
                word_count INTEGER DEFAULT 0,
                target_words INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 章节表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                chapter_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                word_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'draft',
                quality_score REAL DEFAULT 0.0,
                ai_agent TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # 角色档案表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                character_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                description TEXT,
                personality TEXT,
                relationships TEXT,
                backstory TEXT,
                goals TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # 记忆表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                project_id TEXT,
                category TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score REAL DEFAULT 0.5,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # 质量评估表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_reports (
                report_id TEXT PRIMARY KEY,
                project_id TEXT,
                chapter_id TEXT,
                overall_score REAL NOT NULL,
                readability_score REAL,
                coherence_score REAL,
                creativity_score REAL,
                grammar_score REAL,
                consistency_score REAL,
                engagement_score REAL,
                feedback TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id),
                FOREIGN KEY (chapter_id) REFERENCES chapters (chapter_id)
            )
        ''')
        
        # AI代理状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'idle',
                current_task TEXT,
                model TEXT NOT NULL,
                specialty TEXT,
                performance TEXT,
                last_active TEXT,
                uptime TEXT,
                memory_usage REAL,
                cpu_usage REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 项目设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_settings (
                setting_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
            "CREATE INDEX IF NOT EXISTS idx_projects_user ON projects (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status)",
            "CREATE INDEX IF NOT EXISTS idx_chapters_project ON chapters (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters (chapter_number)",
            "CREATE INDEX IF NOT EXISTS idx_characters_project ON characters (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_project ON memories (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_category ON memories (category)",
            "CREATE INDEX IF NOT EXISTS idx_quality_project ON quality_reports (project_id)",
            "CREATE INDEX IF NOT EXISTS idx_quality_chapter ON quality_reports (chapter_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        print("✅ SQLite数据库表创建完成")
        
    def initialize_redis_data(self):
        """初始化Redis数据"""
        print("🔴 初始化Redis数据...")
        try:
            import redis
            
            # 连接Redis (使用环境变量或默认配置)
            redis_host = os.getenv('REDIS_HOST', 'redis')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            
            # 测试连接
            r.ping()
            
            # 设置默认配置
            r.hset('config:default', mapping={
                'max_concurrent_projects': '5',
                'default_chapter_length': '2000',
                'auto_save_interval': '30',
                'quality_threshold': '0.8'
            })
            
            # 初始化用户会话模板
            r.setex('session:template', 3600, json.dumps({
                'theme': 'light',
                'language': 'zh-CN',
                'notifications': True,
                'auto_refresh': True
            }))
            
            print("✅ Redis数据初始化完成")
            
        except redis.ConnectionError:
            print("⚠️  Redis未启动，跳过Redis初始化")
        except ImportError:
            print("⚠️  Redis模块未安装，跳过Redis初始化")
    
    def initialize_chroma_db(self):
        """初始化ChromaDB向量数据库"""
        print("🧠 初始化ChromaDB向量数据库...")
        try:
            import chromadb
            from chromadb.config import Settings
            
            # 创建ChromaDB客户端
            client = chromadb.PersistentClient(
                path=str(self.chroma_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 创建集合
            collections = {
                'novel_content': '小说内容向量存储',
                'characters': '角色信息向量存储',
                'worldview': '世界观设定向量存储',
                'plot_outlines': '情节大纲向量存储'
            }
            
            for collection_name, description in collections.items():
                try:
                    collection = client.get_collection(collection_name)
                    print(f"✅ 集合 {collection_name} 已存在")
                except:
                    collection = client.create_collection(
                        name=collection_name,
                        metadata={"description": description}
                    )
                    print(f"✅ 创建集合 {collection_name}")
            
            print("✅ ChromaDB初始化完成")
            
        except ImportError:
            print("⚠️  ChromaDB未安装，跳过向量数据库初始化")
        except Exception as e:
            print(f"⚠️  ChromaDB初始化失败: {e}")
    
    def create_default_admin(self):
        """创建默认管理员账户"""
        print("👤 创建默认管理员账户...")
        
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()
        
        # 检查是否已有管理员
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # 导入密码哈希函数
            import bcrypt
            
            # 创建管理员账户
            admin_id = "admin_001"
            username = "admin"
            email = "admin@goodtxt.com"
            password = "admin123456"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            api_key = f"gk_{os.urandom(16).hex()}"
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (
                    user_id, username, email, password_hash, role, created_at, is_active, api_key, settings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_id, username, email, password_hash, 'admin', 
                created_at, True, api_key, 
                json.dumps({"theme": "light", "language": "zh-CN"})
            ))
            
            conn.commit()
            print(f"✅ 创建默认管理员账户:")
            print(f"   用户名: {username}")
            print(f"   密码: {password}")
            print(f"   邮箱: {email}")
            
        else:
            print("✅ 管理员账户已存在")
        
        conn.close()
    
    def create_sample_data(self):
        """创建示例数据"""
        print("📝 创建示例数据...")
        
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()
        
        # 创建示例用户
        cursor.execute("SELECT user_id FROM users WHERE username = 'admin'")
        admin_result = cursor.fetchone()
        if admin_result:
            admin_id = admin_result[0]
            
            # 创建示例项目
            sample_projects = [
                {
                    'project_id': 'project_001',
                    'user_id': admin_id,
                    'title': '星际征途',
                    'description': '探索未知星系的科幻冒险小说',
                    'genre': 'science_fiction',
                    'length': 'medium',
                    'theme': '探索与成长',
                    'target_audience': '青年读者',
                    'status': 'active',
                    'progress': 0.0,
                    'word_count': 0,
                    'target_words': 30000
                },
                {
                    'project_id': 'project_002',
                    'user_id': admin_id,
                    'title': '古风情缘',
                    'description': '古代背景的浪漫爱情故事',
                    'genre': 'romance',
                    'length': 'short',
                    'theme': '爱情与忠诚',
                    'target_audience': '女性读者',
                    'status': 'draft',
                    'progress': 0.0,
                    'word_count': 0,
                    'target_words': 15000
                }
            ]
            
            for project in sample_projects:
                try:
                    cursor.execute('''
                        INSERT INTO projects (
                            project_id, user_id, title, description, genre, length,
                            theme, target_audience, status, progress, word_count, 
                            target_words, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        project['project_id'], project['user_id'], project['title'],
                        project['description'], project['genre'], project['length'],
                        project['theme'], project['target_audience'], project['status'],
                        project['progress'], project['word_count'], project['target_words'],
                        datetime.now().isoformat(), datetime.now().isoformat()
                    ))
                    print(f"✅ 创建示例项目: {project['title']}")
                except sqlite3.IntegrityError:
                    print(f"⚠️  项目已存在: {project['title']}")
            
            conn.commit()
        
        conn.close()
        print("✅ 示例数据创建完成")
    
    def setup_directory_permissions(self):
        """设置目录权限"""
        print("🔒 设置目录权限...")
        
        # 确保所有目录都有读写权限
        for directory in [self.data_dir, self.db_dir, self.chroma_dir, self.exports_dir]:
            try:
                directory.chmod(0o755)
                print(f"✅ 设置权限: {directory}")
            except Exception as e:
                print(f"⚠️  设置权限失败: {directory} - {e}")
    
    def verify_installation(self):
        """验证安装"""
        print("🔍 验证安装...")
        
        # 检查SQLite
        if self.sqlite_path.exists():
            conn = sqlite3.connect(str(self.sqlite_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ SQLite: {len(tables)} 个表")
            conn.close()
        else:
            print("❌ SQLite数据库未创建")
        
        # 检查目录
        dirs = {
            '数据目录': self.data_dir,
            '数据库目录': self.db_dir,
            '向量数据库目录': self.chroma_dir,
            '导出目录': self.exports_dir
        }
        
        for name, path in dirs.items():
            if path.exists():
                print(f"✅ {name}: {path}")
            else:
                print(f"❌ {name}: 不存在")
    
    def run(self):
        """运行完整初始化"""
        print("🚀 开始数据库初始化...")
        print("=" * 50)
        
        try:
            self.setup_directory_permissions()
            self.create_sqlite_tables()
            self.initialize_redis_data()
            self.initialize_chroma_db()
            self.create_default_admin()
            self.create_sample_data()
            self.verify_installation()
            
            print("=" * 50)
            print("🎉 数据库初始化完成!")
            print("\n📋 快速开始:")
            print("1. 配置AI API密钥 (.env文件)")
            print("2. 启动系统: python main.py")
            print("3. 访问前端: http://localhost:3002")
            print("4. 登录: admin / admin123456")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise

if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.run()