import re
from config.settings import settings
from typing import Union, List, Dict, Any, Tuple
from loguru import logger

class SafetyFilter:
    """输入/输出敏感内容过滤。"""
    
    def __init__(self, sensitive_words: List[str] = None):
        self.sensitive_words = sensitive_words or settings.SENSITIVE_WORDS

    def filter_text(self, text: str) -> Tuple[bool, str]:
        """
        检查文本中是否包含敏感词。
        返回 (是否通过, 处理后的文本/错误提示)。
        """
        for word in self.sensitive_words:
            if re.search(re.escape(word), text, re.IGNORECASE):
                logger.warning(f"Sensitive word detected: {word}")
                return False, "Content contains sensitive words and has been blocked."
        return True, text

    def filter_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """检查整个消息历史是否包含敏感内容。"""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                passed, _ = self.filter_text(content)
                if not passed:
                    return False
            elif isinstance(content, list):
                # 图片描述等
                for item in content:
                    if item.get("type") == "text":
                        passed, _ = self.filter_text(item.get("text", ""))
                        if not passed:
                            return False
        return True

safety_filter = SafetyFilter()

# 修改入口：
# 敏感词库可以在 config/settings.py 的 SENSITIVE_WORDS 中更新，
# 或在 SafetyFilter.__init__ 中动态加载库文件。
