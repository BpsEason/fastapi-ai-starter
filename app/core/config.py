import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    【應用程式核心設定】
    
    這個類別使用 Pydantic 的 BaseSettings 來讀取環境變數 (Environment Variables)。
    這意味著您可以透過設置環境變數 (例如：`export APP_API_KEY="new_key"`)
    來覆蓋這裡設定的預設值，而無需修改程式碼。
    
    初學者建議：
    - 您可以在這裡查看並修改所有的應用程式參數預設值。
    - 如果您要新增新的全局配置 (例如數據庫連接字串)，請在這裡定義。
    """
    
    # --- API 安全與驗證設定 ---
    APP_API_KEY: str = os.getenv("APP_API_KEY", "changeme")
    """服務主金鑰，用於內存模式 (非 Redis) 下的預設驗證。"""
    
    # --- 模型控制設定 ---
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "mock")  # mock or external
    """
    顯示模型提供者資訊，用於 /health 路由。
    'mock' 表示使用模擬服務；'external' 或其他值表示使用真實模型或外部服務。
    """
    
    USE_REAL_MODEL: bool = os.getenv("USE_REAL_MODEL", "0") == "1"
    """
    決定是否使用 app/ai_client.py 中定義的 RealAIClient。
    '1' (True) 啟用真實模型，'0' (False) 啟用 Mock 模型。
    """
    
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/real")
    """
    真實模型 (RealAIClient) 載入模型權重的本地路徑或 Hugging Face 模型名稱。
    """
    
settings = Settings()
