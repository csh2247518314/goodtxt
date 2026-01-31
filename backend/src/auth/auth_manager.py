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
import json
import time
from datetime import datetime, timedelta
import base64
# 使用内置库替代外部依赖
import hashlib
import hmac

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
        # 使用内置加密方法替代外部库
        self.jwt_secret = self.settings.security.jwt_secret_key
        self.jwt_algorithm = "HS256"
        self.token_expire_hours = 24
        
        # 登录失败跟踪
        self.login_attempts: Dict[str, Dict[str, int]] = {}  # username -> {attempts, locked_until}
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def hash_password(self, password: str) -> str:
        """使用PBKDF2进行密码哈希"""
        # 生成随机盐值
        salt = secrets.token_hex(32)
        # 使用PBKDF2进行哈希
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                      password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)  # 100,000次迭代
        # 返回盐值+哈希值的组合
        return salt + pwdhash.hex()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        if len(password_hash) < 64:  # 盐值至少32字节hex编码为64字符
            return False
        
        # 分离盐值和哈希值
        salt = password_hash[:64]
        stored_hash = password_hash[64:]
        
        # 使用相同盐值对输入密码进行哈希
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                      password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        # 比较哈希值
        return hmac.compare_digest(stored_hash, pwdhash.hex())
    
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
        """生成自定义令牌（替代JWT）"""
        import hmac
        import json
        import base64
        
        # 创建payload
        payload = {
            "user_id": user_id,
            "exp": (datetime.utcnow() + timedelta(hours=self.token_expire_hours)).timestamp(),
            "iat": datetime.utcnow().timestamp()
        }
        
        # 编码header和payload
        header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip('=')
        payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        # 创建签名
        signature = hmac.new(
            self.jwt_secret.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256
        ).digest()
        signature = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        return f"{header}.{payload}.{signature}"
    
    def verify_token(self, token: str) -> Optional[str]:
        """验证自定义令牌（替代JWT）"""
        import hmac
        import json
        import base64
        
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header, payload, signature = parts
            
            # 重新添加填充
            header += '=' * (4 - len(header) % 4)
            payload += '=' * (4 - len(payload) % 4)
            signature += '=' * (4 - len(signature) % 4)
            
            # 验证签名
            expected_signature = hmac.new(
                self.jwt_secret.encode(),
                f"{header}.{payload}".encode(),
                hashlib.sha256
            ).digest()
            expected_signature = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # 解码payload
            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_dict = json.loads(decoded_payload)
            
            # 检查过期时间
            exp = payload_dict.get('exp')
            if exp and time.time() > exp:
                return None
            
            return payload_dict.get('user_id')
        except Exception:
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

# 注意：生产环境不应自动创建默认管理员账户
# 以下是示例代码，实际部署时应通过环境变量或命令行创建
# if os.getenv('CREATE_DEFAULT_ADMIN'):
#     try:
#         admin_user = auth_manager.create_user(
#             username=os.getenv('DEFAULT_ADMIN_USERNAME', 'admin'),
#             email=os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com'),
#             password=os.getenv('DEFAULT_ADMIN_PASSWORD', 'SecurePassword123!'),
#             role=UserRole.ADMIN
#         )
#         print("默认管理员账户已创建")
#     except ValueError as e:
#         print(f"管理员账户创建失败: {e}")


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



