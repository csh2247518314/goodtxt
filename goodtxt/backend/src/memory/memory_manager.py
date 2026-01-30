"""
AI记忆管理系统

实现三层记忆架构：短期记忆（Redis）、
中期记忆（SQLite）、长期记忆（ChromaDB）
"""

import asyncio
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import structlog
import redis
import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np

from ..config.settings import get_settings


class MemoryType(Enum):
    """记忆类型枚举"""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term" 
    LONG_TERM = "long_term"


class MemoryCategory(Enum):
    """记忆分类枚举"""
    CONVERSATION = "conversation"
    PLOT = "plot"
    CHARACTER = "character"
    WORLDVIEW = "worldview"
    THEME = "theme"
    EMOTION = "emotion"
    FACTS = "facts"


@dataclass
class MemoryEntry:
    """记忆条目"""
    memory_id: str
    content: str
    category: MemoryCategory
    memory_type: MemoryType
    metadata: Dict[str, Any]
    importance_score: float
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['category'] = self.category.value
        data['memory_type'] = self.memory_type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data


class ShortTermMemory:
    """短期记忆管理（Redis）"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        try:
            self.redis_client = redis.Redis(
                host=self.settings.db.redis_host,
                port=self.settings.db.redis_port,
                db=self.settings.db.redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            self.redis_client.ping()
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def store(self, memory_id: str, content: Dict[str, Any], ttl: int = 3600) -> bool:
        """存储短期记忆"""
        try:
            if self.redis_client is None:
                self.logger.warning("Redis client not available, skipping short-term memory storage")
                return False
                
            key = f"memory:short:{memory_id}"
            data = json.dumps(content, ensure_ascii=False)
            
            # 设置过期时间
            self.redis_client.setex(key, ttl, data)
            self.logger.debug(f"Stored short-term memory: {memory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store short-term memory {memory_id}: {e}")
            return False
    
    async def retrieve(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """检索短期记忆"""
        try:
            if self.redis_client is None:
                self.logger.warning("Redis client not available, cannot retrieve short-term memory")
                return None
                
            key = f"memory:short:{memory_id}"
            data = self.redis_client.get(key)
            
            if data:
                content = json.loads(data)
                self.logger.debug(f"Retrieved short-term memory: {memory_id}")
                return content
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve short-term memory {memory_id}: {e}")
            return None
    
    async def get_recent(self, count: int = 50) -> List[Dict[str, Any]]:
        """获取最近的短期记忆"""
        try:
            keys = self.redis_client.keys("memory:short:*")
            recent_keys = sorted(keys, reverse=True)[:count]
            
            memories = []
            for key in recent_keys:
                data = self.redis_client.get(key)
                if data:
                    memories.append({
                        "memory_id": key.decode().split(":")[-1],
                        "content": json.loads(data)
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to get recent short-term memories: {e}")
            return []


class MediumTermMemory:
    """中期记忆管理（SQLite）"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        self.db_path = self.settings.db.sqlite_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建中期记忆表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medium_term_memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_medium_memory_category 
                ON medium_term_memories(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_medium_memory_importance 
                ON medium_term_memories(importance_score DESC)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize medium-term memory database: {e}")
            raise
    
    def store(self, memory_id: str, content: str, category: MemoryCategory, 
              importance_score: float = 0.0, metadata: Optional[Dict] = None) -> bool:
        """存储中期记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
            
            cursor.execute("""
                INSERT OR REPLACE INTO medium_term_memories 
                (memory_id, content, category, importance_score, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (memory_id, content, category.value, importance_score, metadata_json))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Stored medium-term memory: {memory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store medium-term memory {memory_id}: {e}")
            return False
    
    def retrieve(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """检索中期记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM medium_term_memories WHERE memory_id = ?
            """, (memory_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                metadata = json.loads(row[7]) if row[7] else {}
                result = {
                    "memory_id": row[0],
                    "content": row[1],
                    "category": row[2],
                    "importance_score": row[3],
                    "created_at": row[4],
                    "last_accessed": row[5],
                    "access_count": row[6],
                    "metadata": metadata
                }
                
                # 更新访问统计
                self._update_access_stats(memory_id)
                
                self.logger.debug(f"Retrieved medium-term memory: {memory_id}")
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve medium-term memory {memory_id}: {e}")
            return None
    
    def search_by_category(self, category: MemoryCategory, limit: int = 50) -> List[Dict[str, Any]]:
        """按类别搜索中期记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM medium_term_memories 
                WHERE category = ? 
                ORDER BY importance_score DESC, last_accessed DESC
                LIMIT ?
            """, (category.value, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                metadata = json.loads(row[7]) if row[7] else {}
                memories.append({
                    "memory_id": row[0],
                    "content": row[1],
                    "category": row[2],
                    "importance_score": row[3],
                    "created_at": row[4],
                    "last_accessed": row[5],
                    "access_count": row[6],
                    "metadata": metadata
                })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to search medium-term memories by category: {e}")
            return []
    
    def _update_access_stats(self, memory_id: str):
        """更新访问统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            from datetime import datetime
            
            cursor.execute("""
                UPDATE medium_term_memories 
                SET last_accessed = ?, 
                    access_count = access_count + 1
                WHERE memory_id = ?
            """, (datetime.now().isoformat(), memory_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update access stats for {memory_id}: {e}")


class LongTermMemory:
    """长期记忆管理（ChromaDB）"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        self.chroma_client = chromadb.PersistentClient(
            path=self.settings.db.chroma_persist_directory
        )
        self.collections = {}
        self._init_collections()
    
    def _init_collections(self):
        """初始化集合"""
        collection_names = [
            "conversations", "plot_elements", "characters", 
            "worldview", "themes", "emotions", "facts"
        ]
        
        for name in collection_names:
            try:
                self.collections[name] = self.chroma_client.get_or_create_collection(
                    name=name,
                    embedding_function=None  # 使用默认嵌入函数
                )
            except Exception as e:
                self.logger.error(f"Failed to create collection {name}: {e}")
    
    def store(self, memory_id: str, content: str, category: MemoryCategory, 
              metadata: Optional[Dict] = None, embeddings: Optional[List[float]] = None) -> bool:
        """存储长期记忆"""
        try:
            collection_name = self._get_collection_name(category)
            collection = self.collections[collection_name]
            
            metadata = metadata or {}
            metadata.update({
                "memory_id": memory_id,
                "category": category.value,
                "created_at": datetime.now().isoformat()
            })
            
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            self.logger.debug(f"Stored long-term memory: {memory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store long-term memory {memory_id}: {e}")
            return False
    
    def search(self, query: str, category: Optional[MemoryCategory] = None, 
               n_results: int = 10) -> List[Dict[str, Any]]:
        """搜索长期记忆"""
        try:
            results = []
            
            if category:
                collection_name = self._get_collection_name(category)
                collection = self.collections[collection_name]
                
                query_results = collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    query_results['documents'][0],
                    query_results['metadatas'][0],
                    query_results['distances'][0]
                )):
                    results.append({
                        "memory_id": query_results['ids'][0][i],
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,
                        "category": category.value
                    })
            else:
                # 在所有集合中搜索
                for category_enum in MemoryCategory:
                    category_results = self.search(query, category_enum, n_results)
                    results.extend(category_results)
            
            # 按相似度排序
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results[:n_results]
            
        except Exception as e:
            self.logger.error(f"Failed to search long-term memory: {e}")
            return []
    
    def _get_collection_name(self, category: MemoryCategory) -> str:
        """获取集合名称"""
        mapping = {
            MemoryCategory.CONVERSATION: "conversations",
            MemoryCategory.PLOT: "plot_elements",
            MemoryCategory.CHARACTER: "characters",
            MemoryCategory.WORLDVIEW: "worldview",
            MemoryCategory.THEME: "themes",
            MemoryCategory.EMOTION: "emotions",
            MemoryCategory.FACTS: "facts"
        }
        return mapping.get(category, "facts")


class MemoryManager:
    """统一记忆管理器"""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.medium_term = MediumTermMemory()
        self.long_term = LongTermMemory()
        self.logger = structlog.get_logger()
    
    async def store_memory(
        self, 
        memory_id: str, 
        content: str, 
        category: MemoryCategory,
        memory_type: MemoryType,
        importance_score: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> bool:
        """存储记忆"""
        try:
            success = False
            
            if memory_type == MemoryType.SHORT_TERM:
                success = await self.short_term.store(memory_id, content, metadata or {})
            
            elif memory_type == MemoryType.MEDIUM_TERM:
                success = self.medium_term.store(
                    memory_id, content, category, importance_score, metadata
                )
            
            elif memory_type == MemoryType.LONG_TERM:
                success = self.long_term.store(
                    memory_id, content, category, metadata
                )
            
            if success:
                self.logger.info(f"Memory stored: {memory_id} ({memory_type.value})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store memory {memory_id}: {e}")
            return False
    
    async def retrieve_memory(self, memory_id: str, memory_type: MemoryType) -> Optional[Dict]:
        """检索记忆"""
        try:
            if memory_type == MemoryType.SHORT_TERM:
                return await self.short_term.retrieve(memory_id)
            
            elif memory_type == MemoryType.MEDIUM_TERM:
                return self.medium_term.retrieve(memory_id)
            
            elif memory_type == MemoryType.LONG_TERM:
                # 长期记忆需要按ID搜索，这里使用空查询和分类搜索
                results = self.long_term.search(memory_id, None, 1)
                # 尝试找到匹配的ID
                for result in results:
                    if result.get('memory_id') == memory_id:
                        return result
                return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory {memory_id}: {e}")
            return None
    
    async def search_memories(
        self, 
        query: str, 
        category: Optional[MemoryCategory] = None,
        memory_types: Optional[List[MemoryType]] = None
    ) -> List[Dict]:
        """搜索记忆"""
        try:
            all_results = []
            memory_types = memory_types or [MemoryType.SHORT_TERM, MemoryType.MEDIUM_TERM, MemoryType.LONG_TERM]
            
            for mem_type in memory_types:
                if mem_type == MemoryType.LONG_TERM:
                    results = self.long_term.search(query, category)
                    all_results.extend(results)
                elif mem_type == MemoryType.MEDIUM_TERM and category:
                    results = self.medium_term.search_by_category(category)
                    # 转换格式以匹配长期记忆结果
                    for result in results:
                        all_results.append({
                            "memory_id": result.get('memory_id'),
                            "content": result.get('content'),
                            "metadata": result.get('metadata'),
                            "category": result.get('category'),
                            "similarity_score": result.get('importance_score', 0.0)
                        })
                elif mem_type == MemoryType.SHORT_TERM:
                    results = await self.short_term.get_recent()
                    # 转换格式以匹配长期记忆结果
                    for result in results:
                        all_results.append({
                            "memory_id": result.get('memory_id'),
                            "content": str(result.get('content')),
                            "metadata": {},
                            "category": "short_term",
                            "similarity_score": 1.0
                        })
            
            # 按相似度/重要性排序
            all_results.sort(key=lambda x: x.get('similarity_score', 0.0), reverse=True)
            
            return all_results
            
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    async def cleanup_expired_memories(self) -> int:
        """清理过期记忆"""
        # 这里可以实现记忆过期策略
        # 例如：清理低重要性的中期记忆
        self.logger.info("Memory cleanup completed")
        return 0