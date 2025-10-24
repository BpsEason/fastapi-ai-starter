import os
import asyncio
from typing import List

USE_REAL = os.getenv("USE_REAL_MODEL", "0") == "1"
MODEL_PATH = os.getenv("MODEL_PATH", "models/real")

class MockModel:
    """
    【AI 核心-模擬模型】
    這是您入門 AI 服務的第一個修改點！
    """
    def generate(self, prompt: str, max_tokens: int = 128) -> str:
        """
        AI 邏輯的核心：根據 prompt 生成回應。
        
        **初學任務：** 將回傳的字串修改為你喜歡的內容！
        例如：return f"AI 說：收到您的訊息：{s}，請稍候！"
        """
        s = prompt.strip()
        if len(s) > 120:
            s = s[:117] + "..."
        return f"MockReply: {s}" # <--- 修改此行來改變 AI 的回應

class MockAIClient:
    """提供異步介面給 MockModel。"""
    def __init__(self):
        self.model = MockModel()

    async def predict(self, prompt: str, max_tokens: int = 128) -> str:
        await asyncio.sleep(0.01) # 模擬網路延遲
        return self.model.generate(prompt, max_tokens)

    async def predict_batch(self, prompts: List[str], max_tokens: int = 128) -> List[str]:
        # 透過 asyncio.gather 實現批次並行處理（用於模擬模型）
        tasks = [self.predict(p, max_tokens) for p in prompts]
        return await asyncio.gather(*tasks)

# Real model support using transformers if toggled
if USE_REAL:
    try:
        from transformers import pipeline
        import torch

        class RealAIClient:
            """
            【AI 核心-真實模型】
            這是整合 PyTorch/TensorFlow/Hugging Face 等模型的地方。
            
            **進階任務：** 如果要換用別的模型函式庫 (如 Scikit-learn, TensorFlow)，
            你需要修改 __init__ 中的載入邏輯，並修改 predict/predict_batch 中的呼叫邏輯。
            """
            def __init__(self, model_path: str = MODEL_PATH, device: int = None):
                self.model_path = model_path
                # 自動選擇 GPU (0) 或 CPU (-1)
                if device is None:
                    self.device = 0 if torch.cuda.is_available() else -1
                else:
                    self.device = device
                
                # Load pipeline in constructor (僅用於 transformers 框架)
                self._pipe = pipeline("text-generation", model=self.model_path, device=self.device)

            async def predict(self, prompt: str, max_tokens: int = 128) -> str:
                # 在執行緒池 (thread pool) 中運行阻塞 (blocking) 的推理程式碼
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: self._pipe(prompt, max_length=max_tokens, do_sample=False))
                return result[0]["generated_text"]

            async def predict_batch(self, prompts: List[str], max_tokens: int = 128) -> List[str]:
                # 優化：利用執行緒池並行執行多個推理任務 (非真正的模型批次推理，但對 API 層來說是並行的)
                loop = asyncio.get_event_loop()
                tasks = [
                    loop.run_in_executor(None, lambda p=p: self._pipe(p, max_length=max_tokens, do_sample=False)[0]["generated_text"])
                    for p in prompts
                ]
                return await asyncio.gather(*tasks)

    except Exception:
        # 如果 Real Model 相關套件未安裝 (如 torch, transformers)，則將其設定為 None
        RealAIClient = None

def get_ai_client():
    """
    依據環境變數 USE_REAL_MODEL 動態決定返回 RealAIClient 或 MockAIClient。
    """
    if USE_REAL and 'RealAIClient' in globals() and RealAIClient is not None:
        return RealAIClient(model_path=MODEL_PATH)
    # 預設返回 MockAIClient
    return MockAIClient()