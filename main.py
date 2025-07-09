from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import uvicorn
import ollama
from chromadb.utils import embedding_functions as chroma_ef
from embedding_functions import DashScopeEmbeddingFunction
import config  # 导入配置文件

# --- FastAPI 应用初始化 ---
app = FastAPI(
    title="试卷客观题 RAG 检索 API",
    description="使用 Ollama 或 阿里云 DashScope 进行语义检索，专为 n8n 集成设计。",
    version="1.1.0"  # 版本更新
)

# --- 应用生命周期事件 ---
@app.on_event("startup")
def startup_event():
    """
    应用启动时执行，初始化所有必要的客户端和连接。
    """
    print("应用启动中...")
    try:
        # 1. 初始化 ChromaDB 客户端
        app.state.chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        print(f"ChromaDB 客户端已在 '{config.CHROMA_PATH}' 路径下初始化。")

        # 2. 根据配置获取 embedding function
        if config.EMBEDDING_PROVIDER == "ollama":
            embedding_function = chroma_ef.OllamaEmbeddingFunction(
                url=f"{config.OLLAMA_CONFIG['host']}/api/embeddings",
                model_name=config.OLLAMA_CONFIG['model'],
            )
            # 初始化Ollama客户端以备后用
            app.state.ollama_client = ollama.Client(host=config.OLLAMA_CONFIG['host'])
            app.state.ollama_client.list() # 检查服务可用性
            print(f"Ollama 客户端已连接到 {config.OLLAMA_CONFIG['host']}。")
        elif config.EMBEDDING_PROVIDER == "dashscope":
            embedding_function = DashScopeEmbeddingFunction(
                api_key=config.DASHSCOPE_CONFIG['api_key'],
                model=config.DASHSCOPE_CONFIG['model'],
                dimensions=config.DASHSCOPE_CONFIG['dimensions']
            )
            # DashScope 的调用被封装在 embedding function 中，无需额外客户端
            print("DashScope Embedding Function 已初始化。")
        else:
            raise ValueError("无效的 Embedding 提供商配置。")
            
        app.state.embedding_function = embedding_function

        # 3. 获取集合
        app.state.collection = app.state.chroma_client.get_collection(
            name=config.COLLECTION_NAME,
            embedding_function=embedding_function # 确保查询时也使用相同的 embedding function
        )
        print(f"成功加载 ChromaDB 集合: '{config.COLLECTION_NAME}'")

    except Exception as e:
        error_message = f"启动失败：初始化过程中发生错误。请检查您的配置和相关服务（Ollama 或网络连接）。详细错误: {e}"
        print(error_message)
        # FastAPI 会继续启动，但端点会因为缺少 app.state 属性而失败
        # 我们在这里存储错误信息，以便在请求时返回
        app.state.startup_error = error_message

# --- API 端点 ---
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
def search_knowledge_base(search_query: SearchQuery):
    """
    接收一个问题，在向量知识库中进行语义搜索，
    并返回最相关的“题目+选项”知识对。
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'collection'):
        raise HTTPException(status_code=503, detail="服务尚未完全初始化，请稍后再试。")

    try:
        # ChromaDB 的 query 方法会自动使用在 get_collection 时指定的 embedding_function
        # 来为 query_texts 生成向量。
        results = app.state.collection.query(
            query_texts=[search_query.query],
            n_results=search_query.top_k
        )
        
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
            "provider": config.EMBEDDING_PROVIDER,
            "query": search_query.query,
            "results": response_data
        }
    except Exception as e:
        error_message = f"搜索过程中发生内部错误: {e}"
        print(f"查询内容: {search_query.query}, 错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

# --- 运行服务 ---
if __name__ == "__main__":
    print("--- 启动 FastAPI 服务 ---")
    print(f"服务将运行在 http://{config.API_HOST}:{config.API_PORT}")
    print("请在另一终端运行 'python build_knowledge_base.py' 来构建知识库。")
    print(f"API 文档位于 http://127.0.0.1:{config.API_PORT}/docs")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT) 