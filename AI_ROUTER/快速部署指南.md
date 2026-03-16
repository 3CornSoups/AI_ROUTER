# 快速部署指南

## 1. 环境准备

### 硬件要求
- 内存: 至少 4GB (推荐 8GB)
- CPU: 至少 2 核 (推荐 4 核)
- 存储: 至少 10GB 可用空间

### 软件依赖
- Docker 20.10+
- Docker Compose v2+
- Python 3.10+ (如果选择本地部署)
- Redis 7.0+ (如果选择本地部署)

## 2. 一键部署步骤

1. **克隆代码库**
   ```bash
   git clone <repository_url>
   cd ai-gateway
   ```

2. **配置环境变量**
   创建 `.env` 文件并填入必要的 API 密钥和数据库连接信息：
   ```env
   # .env 文件
   SECRET_KEY=your-secret-key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   LITELLM_MASTER_KEY=sk-xxxx
   ```

3. **修改模型配置**
   在 `config/settings.py` 或数据库中维护模型路由规则。

4. **启动服务**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

## 3. 部署验证

### 基础健康检查
```bash
curl http://localhost:8000/
```
预期输出: `{"message": "Welcome to Production-grade AI Gateway", "status": "healthy"}`

### 核心功能测试 (Chat API)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 4. 常见问题

- **Redis 连接超时**：请检查 `REDIS_HOST` 是否正确，容器内建议使用 `redis` 作为 host 名。
- **模型调用 401**：请确保 `LITELLM_MASTER_KEY` 或模型对应的 API Key 已正确配置。
- **数据库连接异常**：确认 `DATABASE_URL` 路径及读写权限。
