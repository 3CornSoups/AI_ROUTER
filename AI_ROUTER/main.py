from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import router as api_router
from config.settings import settings
from core.metrics import metrics
from loguru import logger
import sys
import time

# 配置日志
logger.remove()
logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # 启动 Prometheus Exporter
    if settings.ENABLE_METRICS:
        metrics.start_exporter(settings.PROMETHEUS_PORT)

    # 设置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.middleware("http")
    async def log_request_time(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Method: {request.method} Path: {request.url.path} Process Time: {process_time:.4f}s")
        return response

    @app.get("/")
    async def root():
        return {"message": "Welcome to Production-grade AI Gateway", "status": "healthy"}

    return app

app = create_app()
