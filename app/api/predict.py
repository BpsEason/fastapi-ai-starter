from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas import PredictRequest, PredictResponse
from app.ai_client import get_ai_client
from app.middleware import require_api_key

router = APIRouter()

@router.post("/predict", response_model=List[PredictResponse], dependencies=[Depends(require_api_key)])
async def predict_endpoint(payload: List[PredictRequest], ai_client = Depends(get_ai_client)):
    """
    【核心 2：AI 預測 API 處理器】
    
    這是接收所有 AI 推理請求的主要路由。
    
    1. dependencies=[Depends(require_api_key)]：強制執行 API Key 驗證和限流。
    2. 呼叫 ai_client.predict_batch() 將請求轉發給 AI 核心。
    """
    results = []
    try:
        # 1. 提取所有 prompt
        texts = [p.prompt for p in payload]
        
        # 2. 呼叫 AI 核心模組進行批次預測
        responses = await ai_client.predict_batch(texts)
        
        # 3. 格式化結果
        for r in responses:
            results.append(PredictResponse(text=r))
            
    except Exception:
        # 通用錯誤處理
        raise HTTPException(status_code=500, detail="Inference failed")
        
    return results