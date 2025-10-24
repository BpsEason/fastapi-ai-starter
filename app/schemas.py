from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    """
    【核心 3：API 請求的輸入格式】
    
    如果想讓使用者傳入新的參數給 AI (例如：語言、溫度)，請在這裡新增。
    """
    prompt: str = Field(..., min_length=1, max_length=2000, description="使用者輸入的文字或問題。")
    max_tokens: Optional[int] = Field(128, ge=1, le=2048, description="AI 回應的最大長度。")

class PredictResponse(BaseModel):
    """
    【核心 3：API 回應的輸出格式】
    """
    text: str = Field(..., description="AI 模型生成的文字回應。")