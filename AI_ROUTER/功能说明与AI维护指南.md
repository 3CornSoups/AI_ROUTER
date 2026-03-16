# 功能说明与 AI 维护指南

## 1. 功能清单

| 模块 | 功能 | 依赖 | 触发条件 | 返回码 |
| :--- | :--- | :--- | :--- | :--- |
| **接入层** | 统一模型接入 (LiteLLM) | FastAPI, litellm | POST /v1/chat/completions | 200, 401, 500 |
| **接入层** | 多模态输入转换 | httpx, base64 | 消息包含 image_url | 200 |
| **高并发** | Redis 分布式限流 | Redis | API Key 调用频率超限 | 429 |
| **高可用** | 模型熔断与重试 | Redis, tenacity | 连续 10 次调用失败 | 503 |
| **路由** | 智能场景路由 | Pydantic | 请求携带 scenario 标识 | 200 |
| **安全** | 敏感词内容过滤 | re, settings | 匹配内置敏感词库 | 403 |

## 2. 核心配置说明

- `DEFAULT_QPS_LIMIT`: 每秒请求数限制，默认 10。
- `CACHE_TTL`: 请求缓存过期时间（秒），默认 300。
- `LITELLM_MASTER_KEY`: 调用外部模型的主密钥。
- `SENSITIVE_WORDS`: 预定义敏感词列表。

## 3. AI 维护指南 (Prompt 模板)

### 场景 1: 新增模型适配
将以下文本发送给 AI 助手：
> **Prompt**: 请在 `models/database.py` 中新增一个模型配置，模型名为 `ernie-4.0`，所属场景为 `chat`，成本设为 0.05元/1k tokens。同时请在 `core/llm_client.py` 中确认 LiteLLM 的调用逻辑是否需要针对文心一言进行特殊参数调整。

### 场景 2: 修改配置与阈值
将以下文本发送给 AI 助手：
> **Prompt**: 我需要将默认 QPS 限制提高到 50，并将 Redis 缓存时间延长至 10 分钟。请修改 `config/settings.py` 中的相应字段。

### 场景 3: 排查调用报错
将以下文本发送给 AI 助手：
> **Prompt**: 收到用户反馈调用 `gpt-4` 时出现 503 错误，提示熔断器已开启。请分析 `core/governance.py` 中的熔断触发逻辑，并提供一个临时重置熔断状态的脚本。

## 4. 接口说明 (API Docs)

### Chat Completions
- **URL**: `/v1/chat/completions`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <API_KEY>`
- **Payload**:
  ```json
  {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好"}]
  }
  ```
- **Response**: 标准 OpenAI 格式响应。
