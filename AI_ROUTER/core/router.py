from typing import List, Dict, Any, Optional
from models.database import ModelConfig
from loguru import logger
import random

class Router:
    """智能路由，根据场景、成本和模型健康状况选择后端模型。"""
    
    def __init__(self, models_configs: List[ModelConfig]):
        self.models_configs = models_configs

    async def select_best_model(
        self, 
        scenario: Optional[str] = None, 
        preferred_model: Optional[str] = None,
        cost_sensitive: bool = False
    ) -> Optional[ModelConfig]:
        """
        根据权重、健康状态、场景过滤最适合的模型。
        """
        # 1. 过滤健康且活跃的模型 (实际需结合熔断检查)
        active_models = [m for m in self.models_configs if m.is_active]
        
        if not active_models:
            logger.error("No active models available in router")
            return None

        # 2. 场景匹配
        if scenario:
            active_models = [m for m in active_models if m.scenario == scenario]
            
        if not active_models:
            logger.warning(f"No active models found for scenario: {scenario}")
            return None

        # 3. 成本优先排序 (Cost Sensitive)
        if cost_sensitive:
            active_models.sort(key=lambda x: x.cost_per_1k_tokens)
            return active_models[0]

        # 4. 指定模型匹配 (Fallback Logic)
        if preferred_model:
            for m in active_models:
                if m.model_name == preferred_model:
                    return m

        # 5. 简单负载均衡 (按优先级和随机性)
        # 将模型按优先级分组
        priority_groups = {}
        for m in active_models:
            priority_groups.setdefault(m.priority, []).append(m)
        
        # 选择最高优先级组中的一个
        best_priority = min(priority_groups.keys())
        return random.choice(priority_groups[best_priority])

# 修改入口：
# 路由规则在 Router.select_best_model 中定义，
# 成本优先逻辑位于 `if cost_sensitive:` 分支。
