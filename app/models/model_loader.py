# 檔案路徑: app/models/model_loader.py

# 註釋：在您目前提供的專案骨架中，這個檔案通常用來集中定義所有 AI 模型的載入和核心推理邏輯。
# 雖然您目前只看到 MockModel，但 RealModel 的邏輯最終應該也會被移動或集中到類似這樣的檔案結構中。

class MockModel:
    """
    【AI 核心邏輯 - 模擬模型】

    這個類別負責模擬一個 AI 模型的行為。它是您專案的起點。
    
    初學者教學：
    - **主要功能**：模擬 AI 服務的延遲和輸出，確保 API 流程正確。
    - **修改點**：請修改 `generate` 函式中的 `return` 語句，來改變 AI 在 Mock 模式下的回應文字。
    """
    def generate(self, prompt: str, max_tokens: int = 128) -> str:
        """
        根據輸入的 prompt 模擬生成一段回應文字。

        Args:
            prompt (str): 使用者的輸入文字。
            max_tokens (int): 模擬的最大回應長度。

        Returns:
            str: 模擬的 AI 回應。
        """
        # 簡單的清理輸入
        summary = prompt.strip()
        
        # 模擬截斷長度
        if len(summary) > 120:
            summary = summary[:117] + "..."
            
        # <-- 您可以在這裡修改回覆內容 -->
        return f"MockReply: {summary}" 
