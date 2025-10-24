import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import os

# 建立 FastAPI 測試客戶端 (Client)
client = TestClient(app)

@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    """
    【測試設定】確保測試使用一個可預測的 API Key。
    
    `@pytest.fixture(autouse=True)` 確保在運行所有測試前，這個函式都會先執行。
    `monkeypatch` 用來在測試執行期間覆蓋環境變數和設定。
    """
    # 設置環境變數和設定物件，讓測試知道 API Key 是 'test-key'
    monkeypatch.setenv("APP_API_KEY", "test-key")
    settings.APP_API_KEY = "test-key"

def test_ping():
    """
    【測試案例 1】測試 /ping 路由的健康檢查。
    
    目的：確認服務最基本的運行狀態。
    """
    # 呼叫 GET /ping
    r = client.get("/ping")
    
    # 驗證：HTTP 狀態碼必須是 200 (成功)
    assert r.status_code == 200
    # 驗證：JSON 回應內容必須是 {"status": "ok"}
    assert r.json()["status"] == "ok"

def test_predict_missing_key():
    """
    【測試案例 2】測試 API Key 遺失時的錯誤處理。
    
    目的：確認未提供 'x-api-key' 時，服務能正確返回 401 錯誤。
    """
    # 呼叫 POST /v1/predict，但未傳送 Headers (因此缺少 x-api-key)
    r = client.post("/v1/predict", json=[{"prompt": "hello"}])
    
    # 驗證：HTTP 狀態碼必須是 401 (未授權)
    assert r.status_code == 401
    # 驗證：錯誤訊息必須是 "Missing x-api-key header"
    assert r.json()["detail"] == "Missing x-api-key header"

def test_predict_success():
    """
    【測試案例 3】測試 AI 預測成功並批次處理的能力 (Mock Model)。
    
    目的：
    1. 確認帶有正確 API Key 的請求能夠成功通過驗證。
    2. 確認服務能夠處理多個輸入 (批次請求)。
    3. 確認 Mock Model 的回應格式正確。
    """
    # 設置正確的 API Key Headers
    headers = {"x-api-key": "test-key"}
    # 設置包含兩個 prompt 的批次請求 Payload
    payload = [
        {"prompt": "Hello world"}, 
        {"prompt": "Second prompt"}
    ]
    
    # 呼叫 POST /v1/predict
    r = client.post("/v1/predict", json=payload, headers=headers)
    
    # 驗證：HTTP 狀態碼必須是 200 (成功)
    assert r.status_code == 200
    
    data = r.json()
    
    # 驗證：回應必須是一個列表 (list)
    assert isinstance(data, list)
    # 驗證：回應列表的長度必須與輸入的批次大小一致 (2 個)
    assert len(data) == 2
    # 驗證：列表中的每個項目都必須包含 'text' 欄位
    assert all("text" in item for item in data)
    # 驗證：Mock Model 的回應必須以 "MockReply" 開頭
    assert data[0]["text"].startswith("MockReply")
