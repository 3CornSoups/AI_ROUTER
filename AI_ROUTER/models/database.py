from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True, nullable=False)
    tenant_id = Column(String(100), index=True, nullable=False)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # 权限与配额限制
    allowed_models = Column(JSON, default=["*"]) # 允许访问的模型列表，["*"] 表示所有
    monthly_token_quota = Column(Integer, default=1000000) # 月度Token配额
    monthly_cost_quota = Column(Float, default=10.0) # 月度成本配额（元）
    qps_limit = Column(Integer, default=10) # 每秒请求数限制
    concurrency_limit = Column(Integer, default=20) # 并发数限制

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(64), index=True)
    api_key_id = Column(Integer, index=True)
    tenant_id = Column(String(100), index=True)
    model = Column(String(100))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    latency_ms = Column(Integer)
    status_code = Column(Integer)
    error_msg = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

class ModelConfig(Base):
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True) # 内部引用的模型名
    litellm_params = Column(JSON) # LiteLLM 所需的参数，如 model, api_base, api_key 等
    priority = Column(Integer, default=1) # 优先级，数值越小越高
    is_active = Column(Boolean, default=True)
    cost_per_1k_tokens = Column(Float, default=0.0) # 每1000个Token的成本
    scenario = Column(String(50)) # 适用场景：chat, long_text, low_cost
