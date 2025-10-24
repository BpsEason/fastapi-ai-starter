### 專案概覽
fastapi-ai-starter 是一個可立即跑起來的教學專案，目標讓任何背景的使用者在短時間內從 0 到部署一個可呼叫的 AI 推理 API。此教學以繁體中文呈現，包含快速上手、檔案說明、逐步操作、常見錯誤排查與進階練習。

---

### 快速上手（3 分鐘試跑）
1. 下載或在本機執行提供的 bootstrap 腳本，建立專案資料夾。  
2. 進入專案資料夾並建立虛擬環境  
```bash
cd fastapi-ai-starter
python -m venv .venv
source .venv/bin/activate
```
3. 安裝依賴  
```bash
pip install -U pip
pip install -r requirements.txt
```
4. 產生本機測試用 API Key（或手動設定）並匯出環境變數  
```bash
./scripts/bootstrap_keys.sh
# 假設輸出 key 為 ABC，執行：
export APP_API_KEY=ABC
```
5. 啟動服務  
```bash
uvicorn app.main:app --reload --port 8000
```
6. 用 curl 測試 API（替換 x-api-key）  
```bash
curl -X POST http://127.0.0.1:8000/v1/predict \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APP_API_KEY" \
  -d '[{"prompt":"Hello world"}]'
```

---

### 檔案結構與角色說明
- **README.md**：教學與快速啟動說明。  
- **requirements.txt**：本專案 Python 套件清單。  
- **.env.example**：建議的環境變數範例。  
- **app/main.py**：FastAPI 應用工廠與全域路由（/ping、/health）。  
- **app/api/predict.py**：/v1/predict endpoint，支援批次請求。  
- **app/schemas.py**：Pydantic 請求與回應模型（驗證輸入）。  
- **app/core/config.py**：環境變數與設定載入。  
- **app/middleware.py**：API Key 驗證、簡易速率限制、Redis 選項。  
- **app/ai_client.py**：AI client factory；預設 Mock，環境切換可使用 Real（transformers）。  
- **app/models/model_loader.py**：簡單 Mock model 實作。  
- **tests/test_predict.py**：pytest 範例測試（在 Mock 模式執行）。  
- **Dockerfile / docker-compose.yml**：容器化與快速啟動範本。  
- **.github/workflows/**：CI（測試）與產生金鑰工作流程。  
- **deploy/render.yaml**：Render 一鍵部署範本。  
- **scripts/bootstrap_keys.sh**：本機產生 API key 的輔助腳本。

---

### 詳細教學步驟（新手友善）
#### A. 先跑起來並理解
1. 啟動服務後，先確認健康檢查與連線  
   - GET http://127.0.0.1:8000/ping 回傳 {"status":"ok"}  
   - GET http://127.0.0.1:8000/health 回傳 model 狀態  
2. 用 curl 或 Postman 呼叫 /v1/predict，觀察請求/回應格式與 status code。  

#### B. 讀懂最重要的程式檔（逐檔簡短解說）
- app/schemas.py：學習 Pydantic 如何用 Field 設定長度、型別、預設值。  
- app/api/predict.py：學習 FastAPI 路由、response_model 與 Depends（注入 auth 與 ai_client）。  
- app/ai_client.py：理解 Mock 與 Real 的切換邏輯、非同步 predict_batch 的實作。  
- app/middleware.py：了解如何擷取 header、回傳 401/429、以及簡單的 in-memory rate limit。

#### C. 執行測試（建立學習回饋）
```bash
pytest -q
```
測試包含：/ping、未帶 API Key 的 401、帶 Key 的成功回應。測試失敗時把錯誤訊息貼給我，我會分析並告訴你如何修正。

---

### 實作練習（循序漸進）
1. 修改 Mock 回傳格式（15 分）：  
   - 目標：把 MockReply 改成 "Echo: {prompt}"，啟動服務並測一次。  
2. 新增 schema 欄位（30 分）：  
   - 目標：在 PredictRequest 新增 language 欄位，並在回應文字內包含語言標籤。寫一個對應的測試。  
3. 加入失敗情境測試（30 分）：  
   - 目標：新增測試驗證當 prompt 為空時回傳 422 或適當錯誤。執行 pytest 並讓它通過。  
4. 進階：啟用 Real 模型（視硬體）  
   - 安裝 transformers 與 torch，放入小型模型到 models/real，export USE_REAL_MODEL=1，啟動並測試。  
   - 注意：Real 模型可能需要大量記憶體或 GPU，若無法本機跑可略過或使用雲端模型 API。

---

### 常見錯誤與快速修復
- uvicorn 找不到 app.main:app  
  - 解法：確認當前目錄是 repo 根目錄，或用 `uvicorn app.main:app` 從 repo 根啟動。  
- 401 Unauthorized  
  - 解法：確認環境變數 APP_API_KEY 與請求 header x-api-key 相同。  
- pytest 因 settings 錯誤失敗  
  - 解法：在測試前 export APP_API_KEY=test-key，或確保測試 fixture 正常設置。  
- Real model 記憶體不足或超時  
  - 解法：改用 Mock 或小型模型；或在雲端 GPU 執行。

---

### 部署與 CI 建議
- 本教學內含 GitHub Actions 範例，CI 會安裝依賴並執行 pytest。  
- 若要在 CI 中測試 Real model，請避免在公共 runner 安裝大型模型；建議在 CI 使用 Mock 或在專用 runner 測試。  
- 部署建議使用 Render / Fly.io / Railway 等免費層，或把 Docker image 推到容器註冊表再部署到雲端。 deploy/render.yaml 提供範本。

---

### 進階學習路線（完成專案後）
1. 觀察與收集指標：加入 Prometheus / OpenTelemetry，收集 latency、error rate。  
2. 性能優化：把模型轉為 ONNX、量化、混合精度或使用 GPU server。  
3. 金鑰管理：把 API Key 存到 Redis 或資料庫，實作金鑰輪替與用量限制。  
4. 安全性：加入 TLS、認證（OAuth/JWT）、使用 WAF 與速率限制代理。

---
