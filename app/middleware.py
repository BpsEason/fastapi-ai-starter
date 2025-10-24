import os
import time
from fastapi import HTTPException
from starlette.requests import Request
from typing import Dict, Any, List

# --- 配置設定 ---
# 決定是否使用外部的 Redis 進行持久化和分散式限流
USE_REDIS = os.getenv("USE_REDIS_FOR_KEYS", "0") == "1"
# 預設的 API 金鑰，若未設定環境變數 APP_API_KEY，則使用 'changeme'
DEFAULT_KEY = os.getenv("APP_API_KEY", "changeme")
# 每分鐘的請求速率限制
RATE_LIMIT = int(os.getenv("API_RATE_LIMIT_PER_MIN", "120"))  # per key per minute

# --- 儲存機制初始化 ---
if USE_REDIS:
    # 如果啟用 Redis，則載入 redis 函式庫並初始化客戶端
    # 🚨 注意：您需要在 requirements.txt 中安裝 'redis' 才能啟用此功能。
    try:
        import redis
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except ImportError:
        # 如果使用者啟用了 USE_REDIS=1 但沒有安裝 redis 函式庫
        print("警告: 已啟用 USE_REDIS，但找不到 'redis' 函式庫。請執行 pip install redis")
        USE_REDIS = False
        _KEY_STORE: Dict[str, Any] = {DEFAULT_KEY: {"created_at": time.time()}}
        _RATE_STORE: Dict[Any, int] = {}
        
else:
    # 內存模式 (非持久化，適用於單一程序/本機測試)
    # _KEY_STORE: 儲存有效的 API Key
    _KEY_STORE: Dict[str, Any] = {DEFAULT_KEY: {"created_at": time.time()}}
    # _RATE_STORE: 儲存 { (key, minute): count } 的請求計數
    _RATE_STORE: Dict[Any, int] = {}

def require_api_key(request: Request):
    """
    【核心驗證函式】API Key 驗證與速率限制 (Rate Limiting)
    
    這個函式會在每次呼叫 /v1/predict 時作為 FastAPI 的依賴項 (Dependency) 運行，
    以確保請求是合法的且未超過限制。

    初學者教學：
    - **不用修改**：這個函式已經涵蓋了安全和性能考量 (如限流)。
    - **如何傳送金鑰**：外部客戶端必須在 HTTP Header 中加入 'x-api-key' 欄位。
    """
    key = request.headers.get("x-api-key")
    if not key:
        # 401: Unauthorized - 缺少金鑰
        raise HTTPException(status_code=401, detail="Missing x-api-key header")

    if USE_REDIS:
        # --- Redis 驗證與限流邏輯 (分佈式) ---
        exists = redis_client.sismember("api_keys", key)
        if not exists:
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        # 速率限制的 Key 格式: rl:<key>:<當前分鐘數>
        key_rl = f"rl:{key}:{int(time.time()//60)}"
        count = redis_client.incr(key_rl)
        
        if count == 1:
            # 第一個請求，設定 70 秒過期 (稍微大於 60 秒，確保換分鐘時計數器已清空)
            redis_client.expire(key_rl, 70) 
            
        if count > RATE_LIMIT:
            # 429: Too Many Requests - 超過限流
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
    else:
        # --- 內存驗證與限流邏輯 (單一程序) ---
        if key not in _KEY_STORE:
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        # 計算當前分鐘
        minute = int(time.time()//60)
        k = (key, minute)
        
        # 增加請求計數
        _RATE_STORE.setdefault(k, 0)
        _RATE_STORE[k] += 1
        
        if _RATE_STORE[k] > RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
    return key

# --- 輔助函式 (Helpers) ---
def add_key(key: str):
    """
    管理函式：新增一個有效的 API Key 到儲存區。
    
    初學者建議：使用 `./scripts/bootstrap_keys.sh` 腳本來生成和設置金鑰，
    除非您想手動在程式運行時動態新增金鑰。
    """
    if USE_REDIS:
        redis_client.sadd("api_keys", key)
    else:
        _KEY_STORE[key] = {"created_at": time.time()}

def remove_key(key: str):
    """管理函式：從儲存區移除一個 API Key。"""
    if USE_REDIS:
        redis_client.srem("api_keys", key)
    else:
        _KEY_STORE.pop(key, None)

def register_dependency_overrides(app):
    """
    這個函式是為了支援測試 (Testing) 或部署 (Deployment) 時，
    可以替換掉 FastAPI 依賴項的預留位置。
    """
    return
