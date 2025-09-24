"""
Authentication and Rate Limiting System
Implements JWT authentication, API key management, and rate limiting
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from functools import wraps
from collections import defaultdict, deque
import time

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"
    GUEST = "guest"

class RateLimitTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    rate_limit_tier: RateLimitTier
    api_key: Optional[str] = None
    created_at: datetime = None
    last_active: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RateLimit:
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    window_size: int  # seconds

class APIKeyManager:
    """Manages API keys for authentication"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_keys: Dict[str, User] = {}
        self.key_to_user: Dict[str, str] = {}
    
    def generate_api_key(self, user: User) -> str:
        """Generate a new API key for user"""
        # Create a secure random key
        key_material = f"{user.user_id}:{secrets.token_urlsafe(32)}"
        api_key = hashlib.sha256(key_material.encode()).hexdigest()
        
        # Store the mapping
        self.api_keys[api_key] = user
        self.key_to_user[api_key] = user.user_id
        
        # Update user's API key
        user.api_key = api_key
        
        logger.info(f"Generated API key for user {user.user_id}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return user"""
        if api_key in self.api_keys:
            user = self.api_keys[api_key]
            if user.is_active:
                user.last_active = datetime.now()
                return user
        return None
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            if api_key in self.key_to_user:
                del self.key_to_user[api_key]
            logger.info(f"Revoked API key: {api_key[:8]}...")
            return True
        return False
    
    def get_user_by_key(self, api_key: str) -> Optional[User]:
        """Get user by API key"""
        return self.api_keys.get(api_key)

class JWTManager:
    """Manages JWT tokens for authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_blacklist: set = set()
    
    def generate_token(self, user: User, expires_in_hours: int = 24) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'rate_limit_tier': user.rate_limit_tier.value,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Generated JWT token for user {user.user_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                return None
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist"""
        self.token_blacklist.add(token)
        logger.info("Token added to blacklist")
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token"""
        payload = self.validate_token(token)
        if payload:
            # Create new token with same user info
            user = User(
                user_id=payload['user_id'],
                username=payload['username'],
                email="",  # Not in JWT payload
                role=UserRole(payload['role']),
                rate_limit_tier=RateLimitTier(payload['rate_limit_tier'])
            )
            return self.generate_token(user)
        return None

class RateLimiter:
    """Implements rate limiting with sliding window"""
    
    def __init__(self):
        self.rate_limits = {
            RateLimitTier.FREE: RateLimit(10, 100, 1000, 5, 60),
            RateLimitTier.BASIC: RateLimit(30, 500, 5000, 15, 60),
            RateLimitTier.PREMIUM: RateLimit(100, 2000, 20000, 50, 60),
            RateLimitTier.ENTERPRISE: RateLimit(500, 10000, 100000, 200, 60)
        }
        
        # Track requests per user/IP
        self.user_requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.ip_requests: Dict[str, deque] = defaultdict(lambda: deque())
    
    def is_rate_limited(self, identifier: str, tier: RateLimitTier, 
                       is_ip: bool = False) -> tuple[bool, Dict[str, Any]]:
        """Check if request is rate limited"""
        now = time.time()
        rate_limit = self.rate_limits[tier]
        
        # Choose the appropriate request tracker
        requests_tracker = self.ip_requests if is_ip else self.user_requests
        
        # Clean old requests outside the window
        window_start = now - rate_limit.window_size
        while (requests_tracker[identifier] and 
               requests_tracker[identifier][0] < window_start):
            requests_tracker[identifier].popleft()
        
        # Check if adding this request would exceed limits
        current_requests = len(requests_tracker[identifier])
        
        # Check minute limit
        minute_requests = sum(1 for req_time in requests_tracker[identifier] 
                            if req_time > now - 60)
        if minute_requests >= rate_limit.requests_per_minute:
            return True, {
                'limit_type': 'minute',
                'current': minute_requests,
                'limit': rate_limit.requests_per_minute,
                'reset_time': now + 60
            }
        
        # Check hour limit
        hour_requests = sum(1 for req_time in requests_tracker[identifier] 
                          if req_time > now - 3600)
        if hour_requests >= rate_limit.requests_per_hour:
            return True, {
                'limit_type': 'hour',
                'current': hour_requests,
                'limit': rate_limit.requests_per_hour,
                'reset_time': now + 3600
            }
        
        # Check day limit
        day_requests = sum(1 for req_time in requests_tracker[identifier] 
                          if req_time > now - 86400)
        if day_requests >= rate_limit.requests_per_day:
            return True, {
                'limit_type': 'day',
                'current': day_requests,
                'limit': rate_limit.requests_per_day,
                'reset_time': now + 86400
            }
        
        # Add current request
        requests_tracker[identifier].append(now)
        
        return False, {
            'current_requests': current_requests + 1,
            'minute_remaining': rate_limit.requests_per_minute - minute_requests - 1,
            'hour_remaining': rate_limit.requests_per_hour - hour_requests - 1,
            'day_remaining': rate_limit.requests_per_day - day_requests - 1
        }
    
    def get_rate_limit_info(self, identifier: str, tier: RateLimitTier, 
                           is_ip: bool = False) -> Dict[str, Any]:
        """Get current rate limit information"""
        now = time.time()
        rate_limit = self.rate_limits[tier]
        requests_tracker = self.ip_requests if is_ip else self.user_requests
        
        # Clean old requests
        window_start = now - rate_limit.window_size
        while (requests_tracker[identifier] and 
               requests_tracker[identifier][0] < window_start):
            requests_tracker[identifier].popleft()
        
        current_requests = len(requests_tracker[identifier])
        minute_requests = sum(1 for req_time in requests_tracker[identifier] 
                            if req_time > now - 60)
        hour_requests = sum(1 for req_time in requests_tracker[identifier] 
                          if req_time > now - 3600)
        day_requests = sum(1 for req_time in requests_tracker[identifier] 
                         if req_time > now - 86400)
        
        return {
            'tier': tier.value,
            'current_requests': current_requests,
            'minute_usage': f"{minute_requests}/{rate_limit.requests_per_minute}",
            'hour_usage': f"{hour_requests}/{rate_limit.requests_per_hour}",
            'day_usage': f"{day_requests}/{rate_limit.requests_per_day}",
            'limits': {
                'per_minute': rate_limit.requests_per_minute,
                'per_hour': rate_limit.requests_per_hour,
                'per_day': rate_limit.requests_per_day,
                'burst_limit': rate_limit.burst_limit
            }
        }

class AuthenticationSystem:
    """Main authentication system combining all components"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_key_manager = APIKeyManager(secret_key)
        self.jwt_manager = JWTManager(secret_key)
        self.rate_limiter = RateLimiter()
        self.users: Dict[str, User] = {}
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self) -> None:
        """Create default admin user"""
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@example.com",
            role=UserRole.ADMIN,
            rate_limit_tier=RateLimitTier.ENTERPRISE
        )
        self.users["admin"] = admin_user
        self.api_key_manager.generate_api_key(admin_user)
        logger.info("Created default admin user")
    
    def create_user(self, username: str, email: str, role: UserRole = UserRole.USER,
                   rate_limit_tier: RateLimitTier = RateLimitTier.BASIC) -> User:
        """Create a new user"""
        user_id = hashlib.sha256(f"{username}:{email}".encode()).hexdigest()[:16]
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            rate_limit_tier=rate_limit_tier
        )
        
        self.users[user_id] = user
        self.api_key_manager.generate_api_key(user)
        
        logger.info(f"Created user: {username} ({user_id})")
        return user
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate using API key"""
        return self.api_key_manager.validate_api_key(api_key)
    
    def authenticate_jwt(self, token: str) -> Optional[User]:
        """Authenticate using JWT token"""
        payload = self.jwt_manager.validate_token(token)
        if payload:
            user_id = payload['user_id']
            return self.users.get(user_id)
        return None
    
    def check_rate_limit(self, user: User, client_ip: str) -> tuple[bool, Dict[str, Any]]:
        """Check rate limit for user"""
        # Check user-based rate limit
        user_limited, user_info = self.rate_limiter.is_rate_limited(
            user.user_id, user.rate_limit_tier, is_ip=False
        )
        
        # Check IP-based rate limit (stricter for anonymous users)
        ip_tier = RateLimitTier.FREE if user.role == UserRole.GUEST else user.rate_limit_tier
        ip_limited, ip_info = self.rate_limiter.is_rate_limited(
            client_ip, ip_tier, is_ip=True
        )
        
        if user_limited or ip_limited:
            return True, {
                'user_limited': user_limited,
                'ip_limited': ip_limited,
                'user_info': user_info,
                'ip_info': ip_info
            }
        
        return False, {
            'user_info': user_info,
            'ip_info': ip_info
        }
    
    def get_user_info(self, user_id: str) -> Optional[User]:
        """Get user information"""
        return self.users.get(user_id)
    
    def update_user_tier(self, user_id: str, new_tier: RateLimitTier) -> bool:
        """Update user's rate limit tier"""
        if user_id in self.users:
            self.users[user_id].rate_limit_tier = new_tier
            logger.info(f"Updated user {user_id} to tier {new_tier.value}")
            return True
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        if user_id in self.users:
            self.users[user_id].is_active = False
            logger.info(f"Deactivated user {user_id}")
            return True
        return False
    
    def get_rate_limit_status(self, user: User, client_ip: str) -> Dict[str, Any]:
        """Get comprehensive rate limit status"""
        user_info = self.rate_limiter.get_rate_limit_info(
            user.user_id, user.rate_limit_tier, is_ip=False
        )
        ip_info = self.rate_limiter.get_rate_limit_info(
            client_ip, user.rate_limit_tier, is_ip=True
        )
        
        return {
            'user': user_info,
            'ip': ip_info,
            'user_role': user.role.value,
            'user_tier': user.rate_limit_tier.value
        }

def require_auth(auth_system: AuthenticationSystem, allow_guests: bool = False):
    """Decorator for requiring authentication"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the FastAPI context
            # For now, return the function as-is
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: UserRole):
    """Decorator for requiring specific role"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the FastAPI context
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit_check(auth_system: AuthenticationSystem):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the FastAPI context
            return func(*args, **kwargs)
        return wrapper
    return decorator
