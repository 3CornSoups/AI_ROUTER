from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
from core.auth import get_current_api_key, check_model_permission
from core.llm_client import LiteLLMClient
from models.database import APIKey
from config.settings import settings
from loguru import logger
from typing import List, Dict, Any, Optional
import json

router = APIRouter()

@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    body: Dict[str, Any] = Body(...),
    current_key: APIKey = Depends(get_current_api_key)
):
    """
    OpenAI 格式的聊天补全接口。
    """
    model = body.get("model")
    if not model:
        raise HTTPException(status_code=400, detail="Missing 'model' field")
    
    # 权限校验
    await check_model_permission(current_key, model)
    
    # 获取调用参数（过滤掉不需要的部分）
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    kwargs = {k: v for k, v in body.items() if k not in ["model", "messages", "stream"]}
    
    # 获取调用响应
    try:
        response = await LiteLLMClient.chat_completion(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs
        )
        
        if stream:
            async def generate():
                async for chunk in response:
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        # 非流式响应直接返回
        return response.model_dump()
    
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        # 统一报错格式
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models(current_key: APIKey = Depends(get_current_api_key)):
    """
    获取当前 API Key 允许调用的模型列表。
    """
    return {"object": "list", "data": [{"id": m, "object": "model"} for m in current_key.allowed_models]}
