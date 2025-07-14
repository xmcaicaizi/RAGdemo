import chromadb
import pandas as pd
from chromadb.utils import embedding_functions as chroma_ef
import ollama

# 在同一个包/文件夹下的其他模块
from . import config
from .embedding_functions import DashScopeEmbeddingFunction
from .reranker import Qwen3Reranker

class RAGManager:
    """
    一个封装了 RAG 功能的核心模块。
    它处理知识库的生命周期（创建、填充）和检索操作。
    """
    def __init__(self):
        """
        初始化 RAGManager。
        - 设置基于 config.py 的配置。
        - 初始化 ChromaDB 客户端。
        - 根据配置选择并初始化 embedding function。
        - 获取或创建 ChromaDB 集合。
        """
        print("正在初始化 RAGManager...")
        self.config = config
        self._embedding_function = self._get_embedding_function()
        
        self.client = chromadb.PersistentClient(path=self.config.CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name=self.config.COLLECTION_NAME,
            embedding_function=self._embedding_function
        )
        print(f"ChromaDB 集合 '{self.config.COLLECTION_NAME}' 已准备就绪。")
        
        # 如果需要，保留一个Ollama客户端以备直接使用
        if self.config.EMBEDDING_PROVIDER == "ollama":
            self.ollama_client = ollama.Client(host=self.config.OLLAMA_CONFIG['host'])
            print("Ollama 客户端已初始化。")
        
        # 初始化重排序器
        self.qwen3_reranker = Qwen3Reranker()
        print("Qwen3-Reranker已初始化。")

    def _get_embedding_function(self):
        """
        根据配置文件动态选择并返回相应的 embedding function。
        """
        provider = self.config.EMBEDDING_PROVIDER
        print(f"选择的 embedding 服务提供商: {provider}")
        if provider == "ollama":
            return chroma_ef.OllamaEmbeddingFunction(
                url=f"{self.config.OLLAMA_CONFIG['host']}/api/embeddings",
                model_name=self.config.OLLAMA_CONFIG['model'],
            )
        elif provider == "dashscope":
            return DashScopeEmbeddingFunction(
                api_key=self.config.DASHSCOPE_CONFIG['api_key'],
                model=self.config.DASHSCOPE_CONFIG['model'],
                dimensions=self.config.DASHSCOPE_CONFIG['dimensions']
            )
        else:
            raise ValueError(f"无效的 EMBEDDING_PROVIDER: {provider}")

    def build_from_csv(self, csv_file_path: str):
        """
        从 CSV 文件读取数据，进行语义切片，生成向量，并存入 ChromaDB 知识库。
        此函数是幂等的，不会重复添加已存在的条目。

        参数:
            csv_file_path (str): CSV 文件的路径。
        """
        print(f"--- 正在从 {csv_file_path} 构建知识库 ---")
        import os
        filename = os.path.basename(csv_file_path)
        try:
            df = pd.read_csv(csv_file_path)
            print(f"成功读取文件: '{csv_file_path}', 共 {len(df)} 行。")
        except FileNotFoundError:
            print(f"错误: 数据文件 '{csv_file_path}' 未找到。")
            return
        
        documents, metadatas, ids = [], [], []

        # 针对指定的两个表格，采用精细化切片逻辑
        if filename in ["计算机组成原理客观题.csv", "数字逻辑客观题.csv"]:
            for _, row in df.iterrows():
                # 只拼接题干+选项
                doc = f"{row['题干']} {row['选项']}"
                documents.append(doc)
                # id 仍然用编号+选项，metadata 只保留编号
                metadatas.append({"编号": str(row['编号'])})
                ids.append(f"q{row['编号']}_{row['选项']}")
        else:
            # 保持原有逻辑
            for _, row in df.iterrows():
                documents.append(f"题目：{row['question_text']} 选项{row['option_key']}：{row['option_text']}")
                metadatas.append({
                    "question_id": str(row['question_id']),
                    "question_text": row['question_text'],
                    "option_key": row['option_key'],
                    "option_text": row['option_text'],
                    "is_correct": bool(row['is_correct'])
                })
                ids.append(f"q{row['question_id']}_{row['option_key']}")
        
        existing_ids_set = set(self.collection.get(ids=ids)['ids'])
        new_documents, new_metadatas, new_ids = [], [], []

        for i, doc_id in enumerate(ids):
            if doc_id not in existing_ids_set:
                new_documents.append(documents[i])
                new_metadatas.append(metadatas[i])
                new_ids.append(ids[i])
        
        if not new_documents:
            print("文件中的所有数据均已存在于知识库中，无需添加。")
            print("--- 知识库构建完成 ---")
            return

        try:
            print(f"正在向 ChromaDB 添加 {len(new_documents)} 条新知识...")
            self.collection.add(documents=new_documents, metadatas=new_metadatas, ids=new_ids)
            print(f"成功添加 {len(new_documents)} 条。")
        except Exception as e:
            print(f"向 ChromaDB 添加数据时出错。请检查您的 '{self.config.EMBEDDING_PROVIDER}' 服务。")
            print(f"详细错误: {e}")

        print("--- 知识库构建完成 ---")

    def search(self, query: str, top_k: int = 5) -> dict:
        """
        在知识库中执行语义搜索。

        参数:
            query (str): 搜索查询文本。
            top_k (int): 返回的最相关结果数量。

        返回:
            dict: 包含搜索结果的字典。
        """
        print(f"正在为查询执行搜索: '{query}' (top_k={top_k})")
        try:
            results = self.collection.query(query_texts=[query], n_results=top_k)
            
            response_data = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    response_data.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            return {
                "provider": self.config.EMBEDDING_PROVIDER,
                "query": query,
                "results": response_data
            }
        except Exception as e:
            print(f"搜索过程中发生错误: {e}")
            raise
    
    def search_with_rerank(self, query: str, top_k: int = 5) -> dict:
        """
        在知识库中执行语义搜索并用Qwen3-Reranker cross-encoder进行精排。
        
        精排流程：
        1. 使用embedding模型进行初步召回，获取较多候选结果
        2. 使用Qwen3-Reranker cross-encoder对每个候选进行相关性打分
        3. 按相关性分数降序排序，返回top_k个最相关的结果
        
        Args:
            query (str): 搜索查询文本
            top_k (int): 返回的最相关结果数量
            
        Returns:
            dict: 包含精排后搜索结果的字典，包含以下字段：
                - provider: embedding服务提供商
                - query: 原始查询
                - rerank_strategy: 精排策略名称
                - results: 精排后的结果列表，每个结果包含：
                    - id: 知识片段ID
                    - content: 知识片段内容
                    - metadata: 元数据
                    - distance: embedding初步检索距离
                    - original_rank: embedding初步检索排名
                    - rerank_score: Qwen3-Reranker相关性分数（越大越相关）
                    - final_rank: 精排后最终排名
        """
        print(f"正在为查询执行Qwen3-Reranker精排搜索: '{query}' (top_k={top_k})")
        try:
            # 1. 先用embedding检索，取较多候选
            initial_top_k = min(top_k * 5, 30)
            results = self.collection.query(query_texts=[query], n_results=initial_top_k)
            candidates = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    candidates.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i],
                        "original_rank": i + 1
                    })
            if not candidates:
                return {"query": query, "results": []}

            # 2. 用Qwen3-Reranker对每个候选打分
            texts = [c["content"] for c in candidates]
            scores = self.qwen3_reranker.rerank(query, texts)
            for c, s in zip(candidates, scores):
                c["rerank_score"] = s

            # 3. 按分数排序，取top_k
            reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
            for i, c in enumerate(reranked):
                c["final_rank"] = i + 1

            return {
                "provider": self.config.EMBEDDING_PROVIDER,
                "query": query,
                "rerank_strategy": "qwen3-reranker",
                "results": reranked
            }
        except Exception as e:
            print(f"Qwen3-Reranker精排搜索过程中发生错误: {e}")
            raise 