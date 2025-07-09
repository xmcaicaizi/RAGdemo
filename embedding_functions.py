from typing import List, Any
import dashscope
from chromadb import Documents, EmbeddingFunction, Embeddings
from http import HTTPStatus

class DashScopeEmbeddingFunction(EmbeddingFunction):
    """
    一个自定义的 ChromaDB Embedding 函数，用于调用阿里云 DashScope 的 text-embedding-v4 模型。
    """
    def __init__(self, api_key: str, model: str = "text-embedding-v4", dimensions: int = 1024):
        if not api_key:
            raise ValueError("DashScope API Key 不能为空。")
        
        dashscope.api_key = api_key
        self._model = model
        self._dimensions = dimensions
        print(f"DashScopeEmbeddingFunction 已初始化，使用模型: {self._model}, 维度: {self._dimensions}")

    def __call__(self, input: Documents) -> Embeddings:
        """
        根据输入文档生成向量。ChromaDB 会在需要时调用此方法。
        """
        # DashScope API 限制每次调用最多 10 个文本
        batch_size = 10
        embeddings = []
        
        for i in range(0, len(input), batch_size):
            batch = input[i:i+batch_size]
            
            try:
                response = dashscope.TextEmbedding.call(
                    model=self._model,
                    input=batch,
                    dimension=self._dimensions
                )
            except Exception as e:
                print(f"调用 DashScope API 时发生错误: {e}")
                # 在出现错误时返回空列表或部分结果，取决于错误处理策略
                # 这里我们选择抛出异常，让调用者处理
                raise e

            if response.status_code == HTTPStatus.OK:
                # 按原始顺序对齐返回的 embeddings
                batch_embeddings = [None] * len(batch)
                for emb in response.output['embeddings']:
                    batch_embeddings[emb['text_index']] = emb['embedding']
                
                # 检查是否有任何 embedding 未能成功生成
                if any(e is None for e in batch_embeddings):
                    raise ValueError("DashScope API 返回的 embedding 结果与输入不匹配。")
                    
                embeddings.extend(batch_embeddings)
            else:
                print(f"DashScope API 调用失败: Code: {response.code}, Message: {response.message}")
                raise Exception(f"DashScope API 错误: {response.message}")

        return embeddings 