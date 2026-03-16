import litellm
from litellm import completion, acompletion
from config.settings import settings
from loguru import logger
from typing import List, Dict, Any, Optional, Union
import json
import base64
import httpx

# LiteLLM 全局配置
litellm.telemetry = False
litellm.drop_params = True # 自动过滤后端不支持的参数

class LiteLLMClient:
    """LiteLLM 封装，提供多模型一致性接入和图片处理逻辑。"""
    
    @staticmethod
    async def process_multimodal_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        自动处理多模态输入，将图片 URL 或路径转换为 Base64。
        """
        processed_messages = []
        for msg in messages:
            if isinstance(msg.get("content"), list):
                new_content = []
                for item in msg["content"]:
                    if item.get("type") == "image_url":
                        image_data = item["image_url"].get("url")
                        if image_data.startswith("http"):
                            # 远程 URL
                            async with httpx.AsyncClient() as client:
                                resp = await client.get(image_data)
                                if resp.status_code == 200:
                                    mime_type = resp.headers.get("content-type", "image/jpeg")
                                    b64_data = base64.b64encode(resp.content).decode("utf-8")
                                    new_content.append({
                                        "type": "image_url",
                                        "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}
                                    })
                        else:
                            new_content.append(item)
                    else:
                        new_content.append(item)
                processed_messages.append({**msg, "content": new_content})
            else:
                processed_messages.append(msg)
        return processed_messages

    @staticmethod
    async def chat_completion(
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        通过 LiteLLM 调用大模型。
        """
        try:
            # 统一多模态处理
            messages = await LiteLLMClient.process_multimodal_input(messages)
            
            # 记录调用参数供调试
            logger.debug(f"Calling LiteLLM model={model}, stream={stream}")
            
            # 使用异步调用
            response = await acompletion(
                model=model,
                messages=messages,
                stream=stream,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"LiteLLM completion error: {str(e)}")
            raise e
