"""
用户认证管理系统
实现JWT认证、用户管理和权限控制
"""

import hashlib
import secrets
import uuid
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
import bcrypt

from ..config.settings import get_settings
from ..database.db_manager import user_db
import json


class UserRole(Enum):
    """用户角色"""
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"


@dataclass
class User:
    """用户数据模型"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    api_key: str
    settings: Dict[str, str]


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        # 修复bcrypt版本兼容性问题
        try:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception as e:
            # 如果bcrypt有问题，使用pbkdf2_sha256作为备用
            import logging
            logging.warning(f"bcrypt初始化失败，使用备用方案: {e}")
            self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        
        self.jwt_secret = self.settings.security.jwt_secret_key
        self.jwt_algorithm = "HS256"
        self.token_expire_hours = 24
        
        # 登录失败跟踪
        self.login_attempts: Dict[str, Dict[str, int]] = {}  # username -> {attempts, locked_until}
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def hash_password(self, password: str) -> str:
        """密码哈希 - 修复bcrypt版本兼容性"""
        # bcrypt有72字节长度限制，处理超长密码
        if len(password.encode('utf-8')) > 72:
            # 如果密码超过72字节，使用哈希值作为实际密码
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()[:72]
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(password, password_hash)
    
    def _validate_password_strength(self, password: str) -> bool:
        """验证密码强度"""
        if len(password) < 8:
            return False
        
        # 开发环境要求8位密码，生产环境可以增强验证
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        
        # 开发环境：8位密码，必须包含字母和数字
        if len(password) >= 8 and has_letter and has_digit:
            return True
        
        return False
    
    def generate_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload.get("user_id")
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None
    
    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        if user_db.check_username_exists(username):
            raise ValueError("用户名已存在")
        if user_db.check_email_exists(email):
            raise ValueError("邮箱已存在")
        
        # 验证密码强度
        if len(password) < 8:
            raise ValueError("密码至少需要8位")
        
        # 生成用户数据
        password_hash = self.hash_password(password)
        api_key = self._generate_api_key()
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role.value,
            'api_key': api_key,
            'settings': {"theme": "light", "language": "zh-CN"}
        }
        
        # 保存到数据库
        user_id = user_db.create_user(user_data)
        
        # 返回用户对象
        db_user = user_db.get_user_by_id(user_id)
        if not db_user:
            raise ValueError("创建用户失败")
        
        return self._db_user_to_user_obj(db_user)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 检查是否被锁定
        if self._is_user_locked(username):
            return None
        
        # 从数据库获取用户
        db_user = user_db.get_user_by_username(username)
        if not db_user or not db_user['is_active']:
            self._record_login_attempt(username)
            return None
        
        # 验证密码
        if self.verify_password(password, db_user['password_hash']):
            # 登录成功，清除失败记录
            if username in self.login_attempts:
                del self.login_attempts[username]
            
            # 更新登录时间
            user_db.update_user_login_time(db_user['user_id'])
            
            # 返回用户对象
            return self._db_user_to_user_obj(db_user)
        
        # 登录失败，记录失败次数
        self._record_login_attempt(username)
        return None
    
    def _is_user_locked(self, username: str) -> bool:
        """检查用户是否被锁定"""
        if username not in self.login_attempts:
            return False
        
        attempts_data = self.login_attempts[username]
        locked_until = attempts_data.get('locked_until')
        
        if locked_until and datetime.now() < locked_until:
            return True
        elif locked_until and datetime.now() >= locked_until:
            # 锁定时间已过，清除记录
            del self.login_attempts[username]
            return False
        
        return False
    
    def _record_login_attempt(self, username: str) -> None:
        """记录登录失败次数"""
        now = datetime.now()
        
        if username not in self.login_attempts:
            self.login_attempts[username] = {'attempts': 1, 'locked_until': None}
        else:
            attempts_data = self.login_attempts[username]
            attempts_data['attempts'] += 1
            
            # 如果达到最大失败次数，锁定账户
            if attempts_data['attempts'] >= self.max_login_attempts:
                attempts_data['locked_until'] = now + self.lockout_duration
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """通过令牌获取用户"""
        user_id = self.verify_token(token)
        if not user_id:
            return None
        
        # 从数据库获取用户
        db_user = user_db.get_user_by_id(user_id)
        if not db_user or not db_user['is_active']:
            return None
        
        return self._db_user_to_user_obj(db_user)
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """通过API密钥获取用户"""
        db_user = user_db.get_user_by_api_key(api_key)
        if not db_user or not db_user['is_active']:
            return None
        return self._db_user_to_user_obj(db_user)
    
    def update_user_settings(self, user_id: str, settings: Dict[str, str]) -> bool:
        """更新用户设置"""
        return user_db.update_user_settings(user_id, settings)
    
    def _generate_api_key(self) -> str:
        """生成API密钥"""
        return f"gk_{secrets.token_urlsafe(32)}"
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        db_users = user_db.get_all_users()
        return [self._db_user_to_user_obj(db_user) for db_user in db_users]
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        db_user = user_db.get_user_by_id(user_id)
        if not db_user:
            return None
        return self._db_user_to_user_obj(db_user)
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """更新用户角色"""
        return user_db.update_user_role(user_id, new_role.value)
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        return user_db.delete_user(user_id)
    
    def _db_user_to_user_obj(self, db_user: Dict) -> User:
        """将数据库用户数据转换为User对象"""
        # 处理日期时间字段
        created_at = db_user['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        last_login = db_user['last_login']
        if last_login and isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
        
        # 处理设置字段
        settings = {}
        if db_user['settings']:
            try:
                settings = json.loads(db_user['settings'])
            except (json.JSONDecodeError, TypeError):
                settings = {}
        
        return User(
            user_id=db_user['user_id'],
            username=db_user['username'],
            email=db_user['email'],
            password_hash=db_user['password_hash'],
            role=UserRole(db_user['role']),
            created_at=created_at,
            last_login=last_login,
            is_active=bool(db_user['is_active']),
            api_key=db_user['api_key'],
            settings=settings
        )


# 全局认证管理器实例
auth_manager = AuthManager()

# 创建默认管理员用户
try:
    admin_user = auth_manager.create_user(
        username="admin",
        email="admin@goodtxt.com",
        password="admin123456",
        role=UserRole.ADMIN
    )
except ValueError:
    pass  # 用户已存在


def require_auth(func):
    """认证装饰器 - 修复版本"""
    async def wrapper(*args, **kwargs):
        from fastapi import Request, HTTPException, status
        
        # 尝试从参数中获取Request对象
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            # 从kwargs中查找Request对象
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取请求对象",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌格式",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.split(" ")[1]
        user = auth_manager.get_user_by_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或过期的令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 将当前用户添加到参数中
        kwargs['current_user'] = user
        return await func(*args, **kwargs)
    
    return wrapper


def require_admin(func):
    """管理员权限装饰器"""
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or current_user.role != UserRole.ADMIN:
            from fastapi import HTTPException, status
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper



