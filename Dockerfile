FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製所有檔案
COPY . /app

# 安裝依賴 (不含 AI 模型相關的大型依賴，這些應該在 REAL_MODEL=1 時手動安裝或使用特定的 Dockerfile)
# 此處為基礎依賴
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 設定預設環境變數
ENV APP_API_KEY=changeme
ENV USE_REAL_MODEL=0

# 暴露服務埠口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
