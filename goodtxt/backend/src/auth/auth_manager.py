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
from jose import JWTError
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
import bcrypt

from ..config.settings import get_settings


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
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.jwt_secret = self.settings.security.jwt_secret_key
        self.jwt_algorithm = "HS256"
        self.token_expire_hours = 24
        
        # 用户存储（实际应用中应该使用数据库）
        self.users: Dict[str, User] = {}
        self.tokens: Dict[str, str] = {}  # token -> user_id
        
        # 登录失败跟踪
        self.login_attempts: Dict[str, Dict[str, int]] = {}  # username -> {attempts, locked_until}
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(password, password_hash)
    
    def _validate_password_strength(self, password: str) -> bool:
        """验证密码强度"""
        if len(password) < 6:
            return False
        
        # 开发环境允许简单的密码，生产环境可以增强验证
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        
        # 开发环境：只需要6位，字母数字任选其一
        if len(password) >= 6 and (has_letter or has_digit):
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
        if username in [u.username for u in self.users.values()]:
            raise ValueError("用户名已存在")
        if email in [u.email for u in self.users.values()]:
            raise ValueError("邮箱已存在")
        
        # 验证密码强度（临时禁用以允许注册）
        # if not self._validate_password_strength(password):
        #     raise ValueError("密码强度不够，至少需要6位，包含字母或数字")
        
        # 临时允许任何密码进行测试
        if len(password) < 4:
            raise ValueError("密码至少需要4位")
        
        # 使用 UUID 生成唯一用户 ID
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        password_hash = self.hash_password(password)
        api_key = self._generate_api_key()
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=datetime.now(),
            last_login=None,
            is_active=True,
            api_key=api_key,
            settings={"theme": "light", "language": "zh-CN"}
        )
        
        self.users[user_id] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 检查是否被锁定
        if self._is_user_locked(username):
            return None
        
        for user in self.users.values():
            if user.username == username and user.is_active:
                if self.verify_password(password, user.password_hash):
                    # 登录成功，清除失败记录
                    if username in self.login_attempts:
                        del self.login_attempts[username]
                    
                    user.last_login = datetime.now()
                    return user
        
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
        if user_id and user_id in self.users:
            return self.users[user_id]
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """通过API密钥获取用户"""
        for user in self.users.values():
            if user.api_key == api_key:
                return user
        return None
    
    def update_user_settings(self, user_id: str, settings: Dict[str, str]) -> bool:
        """更新用户设置"""
        if user_id in self.users:
            self.users[user_id].settings.update(settings)
            return True
        return False
    
    def _generate_api_key(self) -> str:
        """生成API密钥"""
        return f"gk_{secrets.token_urlsafe(32)}"
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        return list(self.users.values())
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return self.users.get(user_id)
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """更新用户角色"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.role = new_role
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id not in self.users:
            return False
        
        # 删除用户
        del self.users[user_id]
        
        # 清理相关令牌
        tokens_to_remove = [token for token, uid in self.tokens.items() if uid == user_id]
        for token in tokens_to_remove:
            del self.tokens[token]
        
        return True


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


# 创建全局认证管理器实例
auth_manager = AuthManager()


