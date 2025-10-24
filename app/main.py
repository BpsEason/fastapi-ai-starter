from fastapi import FastAPI
from app.api import predict
from app.middleware import register_dependency_overrides
from app.core.config import settings
from app.middleware import require_api_key

def create_app() -> FastAPI:
    """
    【核心 1：服務啟動入口】
    初始化 FastAPI 應用程式，並註冊所有路由模組。
    """
    app = FastAPI(title="FastAPI AI Starter")
    # 註冊 /v1 路由，包含核心的 /v1/predict
    app.include_router(predict.router, prefix="/v1")
    register_dependency_overrides(app)
    return app

app = create_app()

@app.get("/ping")
async def ping():
    """標準健康檢查：確認服務是否運行 (Status: OK)"""
    return {"status": "ok"}

@app.get("/health")
async def health():
    """顯示服務的健康狀態和當前使用的模型提供者 (Mock/Real)"""
    return {"status": "healthy", "model": settings.MODEL_PROVIDER}