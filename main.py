from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from rag_app import config
from rag_app.rag_module import RAGManager  # 导入核心模块
from rag_app.monitor import KnowledgeBaseMonitor  # 导入监视模块

# --- FastAPI 应用初始化 ---
app = FastAPI(
    title="试卷客观题 RAG 检索 API (模块化)",
    description="使用 RAGManager 模块提供语义检索服务，支持 Ollama 和 DashScope。",
    version="3.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="rag_app/static"), name="static")

# 初始化模板
templates = Jinja2Templates(directory="rag_app/templates")

# --- 应用生命周期事件 ---
@app.on_event("startup")
def startup_event():
    """
    应用启动时执行，初始化 RAGManager 并将其作为单例存储。
    """
    print("API 服务启动中...")
    try:
        # 创建 RAGManager 的单例，整个应用的生命周期内共享
        app.state.rag_manager = RAGManager()
        print("RAGManager 初始化成功，API 已准备就绪。")
        
        # 初始化监视器
        app.state.monitor = KnowledgeBaseMonitor()
        print("知识库监视器初始化成功。")
    except Exception as e:
        error_message = f"关键错误：RAGManager 初始化失败。API 将无法工作。错误: {e}"
        print(error_message)
        # 存储错误信息，以便在请求时返回
        app.state.startup_error = error_message

# --- API 端点 ---
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
def search_knowledge_base(search_query: SearchQuery):
    """
    接收一个问题，使用 RAGManager 在知识库中进行语义搜索，
    并返回最相关的“题目+选项”知识对。
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'rag_manager'):
        raise HTTPException(status_code=503, detail="服务尚未完全初始化，请稍后再试。")

    try:
        # 直接调用 RAGManager 实例的 search 方法
        results = app.state.rag_manager.search(
            query=search_query.query, 
            top_k=search_query.top_k
        )
        return results
    except Exception as e:
        error_message = f"搜索过程中发生内部错误: {e}"
        print(f"查询内容: {search_query.query}, 错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

# --- 监视相关端点 ---
@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    """
    监视页面路由
    """
    return templates.TemplateResponse("monitor.html", {"request": request})

@app.get("/monitor/stats")
async def get_monitor_stats():
    """
    获取知识库统计信息
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'monitor'):
        raise HTTPException(status_code=503, detail="监视器尚未初始化，请稍后再试。")
    
    try:
        stats = app.state.monitor.get_collection_stats()
        return stats
    except Exception as e:
        error_message = f"获取统计信息失败: {e}"
        print(f"错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/monitor/samples")
async def get_monitor_samples(limit: int = 10, offset: int = 0):
    """
    获取数据样本
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'monitor'):
        raise HTTPException(status_code=503, detail="监视器尚未初始化，请稍后再试。")
    
    try:
        samples = app.state.monitor.get_data_samples(limit=limit, offset=offset)
        return samples
    except Exception as e:
        error_message = f"获取数据样本失败: {e}"
        print(f"错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

# --- Reranker相关端点 ---
class RerankQuery(BaseModel):
    query: str
    top_k: int = 5
    strategy: str = "hybrid"

@app.post("/search/reranked")
async def search_with_rerank(rerank_query: RerankQuery):
    """
    带重排序的搜索
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'rag_manager'):
        raise HTTPException(status_code=503, detail="服务尚未完全初始化，请稍后再试。")

    try:
        results = app.state.rag_manager.search_with_rerank(
            query=rerank_query.query,
            top_k=rerank_query.top_k,
            strategy=rerank_query.strategy
        )
        return results
    except Exception as e:
        error_message = f"重排序搜索过程中发生内部错误: {e}"
        print(f"查询内容: {rerank_query.query}, 错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/reranker/strategies")
async def get_reranker_strategies():
    """
    获取可用的重排序策略
    """
    if hasattr(app.state, 'startup_error'):
        raise HTTPException(status_code=503, detail=f"服务不可用: {app.state.startup_error}")
    
    if not hasattr(app.state, 'rag_manager'):
        raise HTTPException(status_code=503, detail="服务尚未完全初始化，请稍后再试。")

    try:
        strategies = app.state.rag_manager.reranker.get_available_strategies()
        return {"strategies": strategies}
    except Exception as e:
        error_message = f"获取重排序策略失败: {e}"
        print(f"错误: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

# --- 运行服务 ---
if __name__ == "__main__":
    print("--- 启动 FastAPI 服务 (模块化版本) ---")
    print(f"服务将运行在 http://{config.API_HOST}:{config.API_PORT}")
    print("如果知识库尚未构建，请在另一终端运行 'python build_knowledge_base.py'。")
    print(f"API 文档位于 http://127.0.0.1:{config.API_PORT}/docs")
    print(f"监视页面位于 http://127.0.0.1:{config.API_PORT}/monitor")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT) 