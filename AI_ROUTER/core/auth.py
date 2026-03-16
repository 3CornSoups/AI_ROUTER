from fastapi import Security, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.database import APIKey
from config.settings import settings
from typing import Optional
import hashlib

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_api_key(api_key: str) -> str:
    """对 API Key 进行哈希处理以便安全存储。"""
    return hashlib.sha256(api_key.encode()).hexdigest()

async def get_db_session():
    # 假设已有异步 session 工厂（待实现）
    # yield session
    pass

async def get_current_api_key(
    api_key_header_val: str = Security(api_key_header),
) -> APIKey:
    """验证传入的 API Key 并返回对应的数据库对象。"""
    if not api_key_header_val or not api_key_header_val.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    
    api_key_str = api_key_header_val.replace("Bearer ", "")
    hashed_key = hash_api_key(api_key_str)

    # 模拟从数据库获取 API Key 对象（在此之前应先实现 DB 连接池）
    # 在实际运行中，此处需要调用真正的 DB 查询
    
    # 临时模拟逻辑
    if api_key_str == "test-key-123":
        return APIKey(
            id=1,
            user_id="test_user",
            tenant_id="test_tenant",
            is_active=True,
            allowed_models=["*"],
            qps_limit=10,
            concurrency_limit=20
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

async def check_model_permission(api_key: APIKey, model: str):
    """检查 API Key 是否有权限调用指定的模型。"""
    if "*" in api_key.allowed_models:
        return True
    if model in api_key.allowed_models:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"API Key does not have permission for model '{model}'",
    )
