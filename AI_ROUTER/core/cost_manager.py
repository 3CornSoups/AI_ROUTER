from litellm import token_counter, cost_per_token
from models.database import APIKey, CallLog, ModelConfig
from typing import Dict, Any, Tuple
from loguru import logger

class CostManager:
    """负责 Token 预估、统计、成本核算、配额校验。"""
    
    @staticmethod
    def estimate_token_usage(model: str, messages: list) -> int:
        """模型调用前的 Token 预估。"""
        try:
            return token_counter(model=model, messages=messages)
        except Exception:
            # Fallback for unrecognized models
            logger.warning(f"Could not estimate tokens for model: {model}")
            return len(str(messages)) // 4

    @staticmethod
    def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        根据模型单价计算本次调用成本 (单位：元)。
        """
        try:
            # 1. 尝试使用 LiteLLM 内置单价
            prompt_cost, completion_cost = cost_per_token(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            # LiteLLM 返回的是美元，转换逻辑视业务而定，假设当前单价直接按单位计
            return prompt_cost + completion_cost
        except Exception:
            # 2. 模拟根据数据库配置的单价进行计算 (待补充 DB 联动逻辑)
            # 假设默认成本 (每 1k token 0.01元)
            total = prompt_tokens + completion_tokens
            return (total / 1000) * 0.01

    @staticmethod
    async def is_quota_exceeded(api_key: APIKey) -> bool:
        """校验配额。"""
        # 实际逻辑应查询数据库中当月已消耗的统计信息
        # return current_usage > api_key.monthly_cost_quota
        return False
