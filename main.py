from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import chromadb
import uvicorn
from chromadb.utils import embedding_functions

# --- 配置 ---
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = 'dengcao/qwen3-embedding-0.6b'
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "exam_questions"

# --- 初始化 ---
app = FastAPI(
    title="试卷客观题 RAG 检索 API",
    description="使用 Ollama 和 Qwen3-Embedding 模型进行语义检索，专为 n8n 集成设计。",
    version="1.0.0"
)

# 使用 context manager 来确保在应用生命周期内管理资源
@app.on_event("startup")
def startup_event():
    """
    应用启动时执行，初始化所有必要的客户端和连接。
    """
    print("应用启动中...")
    try:
        # 初始化 ChromaDB 客户端并将其存储在 app.state 中
        app.state.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        print(f"ChromaDB 客户端已在 '{CHROMA_PATH}' 路径下初始化。")
        
        # 定义 Embedding 函数
        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            url=f"{OLLAMA_HOST}/api/embeddings",
            model_name=OLLAMA_MODEL,
        )
        
        # 获取集合，如果不存在则会报错，因为集合应由 build_knowledge_base.py 创建
        app.state.collection = app.state.chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ollama_ef
        )
        print(f"成功加载 ChromaDB 集合: '{COLLECTION_NAME}'")
        
        # 初始化 Ollama 客户端
        app.state.ollama_client = ollama.Client(host=OLLAMA_HOST)
        # 检查Ollama服务和模型是否可用
        app.state.ollama_client.list()
        print(f"Ollama 客户端已连接到 {OLLAMA_HOST}，并确认服务可用。")

    except Exception as e:
        print(f"启动失败：初始化过程中发生错误。")
        print(f"详细错误: {e}")
        # 在这种情况下，我们可能希望应用无法启动或进入错误状态
        # FastAPI 没有内置的方法来中止启动，但我们可以记录错误
        # 实际部署中可能需要更复杂的健康检查逻辑
        raise HTTPException(status_code=500, detail=f"初始化失败: {e}")


# 定义请求体模型
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5 # 默认返回最相似的5个结果

@app.post("/search")
def search_knowledge_base(search_query: SearchQuery):
    """
    接收一个问题，在向量知识库中进行语义搜索，
    并返回最相关的“题目+选项”知识对。
    """
    if not hasattr(app.state, 'collection') or not hasattr(app.state, 'ollama_client'):
        raise HTTPException(status_code=503, detail="服务尚未完全初始化，请稍后再试。")

    try:
        # 1. 在 ChromaDB 中执行相似度搜索
        # embedding 会由 get_collection 时指定的 ollama_ef 自动处理
        results = app.state.collection.query(
            query_texts=[search_query.query],
            n_results=search_query.top_k
        )
        
        # 2. 格式化并返回结果
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
            "query": search_query.query,
            "results": response_data
        }
    except Exception as e:
        print(f"错误：在执行搜索时发生错误。")
        print(f"查询内容: {search_query.query}")
        print(f"详细错误: {e}")
        raise HTTPException(status_code=500, detail=f"搜索过程中发生内部错误: {e}")

# 用于直接运行进行快速测试
if __name__ == "__main__":
    print("正在启动 FastAPI 服务...")
    print("请在另一终端运行 'python build_knowledge_base.py' 来构建知识库。")
    print("API 文档将位于 http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 