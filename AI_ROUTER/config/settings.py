import os
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
from pydantic import Field

class Settings(BaseSettings):
    # API 基础配置
    PROJECT_NAME: str = "AI Gateway"
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = Field(default="your-super-secret-key", env="SECRET_KEY")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./gateway.db", env="DATABASE_URL")
    
    # Redis 配置
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # LiteLLM 配置
    LITELLM_MASTER_KEY: Optional[str] = Field(default=None, env="LITELLM_MASTER_KEY")
    
    # 监控配置
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 8000
    
    # 业务规则默认值
    DEFAULT_QPS_LIMIT: int = 10
    DEFAULT_CONCURRENCY_LIMIT: int = 20
    DEFAULT_DAILY_QUOTA: int = 10000
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5分钟
    
    # 敏感词过滤
    SENSITIVE_WORDS: List[str] = ["敏感词1", "敏感词2"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
