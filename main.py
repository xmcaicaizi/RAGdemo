"""
Main application script that demonstrates how to use both RAG and fine-tuning packages.
This script sets up a FastAPI server that provides endpoints for both RAG and fine-tuning functionality.
"""

import os
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import from our packages
from finetune_app.finetune_module import FineTuneManager
from rag_app.rag_module import RAGManager
from rag_app.kg_module import KGManager
from rag_app.monitor import KnowledgeBaseMonitor

# Create FastAPI app
app = FastAPI(
    title="RAG and Fine-tuning API",
    description="API for RAG search and model fine-tuning",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our managers
rag_manager = RAGManager()
ft_manager = FineTuneManager()
kg_manager = KGManager()

# Set up templates and static files for the monitor UI
templates = Jinja2Templates(directory="rag_app/templates")
app.mount("/static", StaticFiles(directory="rag_app/static"), name="static")

# Initialize the monitor
kb_monitor = KnowledgeBaseMonitor(rag_manager.collection)

# Define request and response models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class FineTuneRequest(BaseModel):
    model_name: str
    data_file: str
    training_args: Optional[Dict] = None

class KGInsertRequest(BaseModel):
    text: str

class KGQueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    top_k: int = 60

# Define API routes
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>RAG and Fine-tuning API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .endpoint { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                .method { font-weight: bold; color: #009900; }
            </style>
        </head>
        <body>
            <h1>RAG and Fine-tuning API</h1>
            <p>Welcome to the RAG and Fine-tuning API. Use the following endpoints:</p>
            
            <div class="endpoint">
                <span class="method">GET</span> <a href="/docs">/docs</a> - Interactive API documentation
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <a href="/search">/search</a> - Search the knowledge base
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <a href="/search/reranked">/search/reranked</a> - Search with reranking
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <a href="/monitor">/monitor</a> - Knowledge base monitor UI
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <a href="/finetune">/finetune</a> - Fine-tune a model
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <a href="/kg/insert">/kg/insert</a> - Insert text into knowledge graph
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <a href="/kg/query">/kg/query</a> - Query the knowledge graph
            </div>
        </body>
    </html>
    """

@app.post("/search")
async def search(request: SearchRequest):
    try:
        return rag_manager.search(query=request.query, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/reranked")
async def search_reranked(request: SearchRequest):
    try:
        return rag_manager.search_with_rerank(query=request.query, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitor")
async def monitor_ui(request: Request):
    return templates.TemplateResponse("monitor.html", {"request": request})

@app.get("/monitor/stats")
async def monitor_stats():
    try:
        return kb_monitor.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitor/samples")
async def monitor_samples(
    limit: int = Query(10, description="Number of samples to return"),
    offset: int = Query(0, description="Offset for pagination"),
):
    try:
        return kb_monitor.get_samples(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/finetune")
async def finetune(request: FineTuneRequest):
    try:
        # Prepare data
        data_dir = ft_manager.prepare_data(request.data_file)
        
        # Load model
        ft_manager.load_model(request.model_name)
        
        # Fine-tune
        model_path = ft_manager.fine_tune(
            train_data_dir=data_dir,
            training_args=request.training_args
        )
        
        # Evaluate
        metrics = ft_manager.evaluate(model_path=model_path)
        
        return {
            "status": "success",
            "model_path": model_path,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kg/insert")
async def kg_insert(request: KGInsertRequest):
    try:
        # Initialize KG manager if not already initialized
        if not hasattr(kg_manager, 'rag') or kg_manager.rag is None:
            await kg_manager.initialize()
        
        # Insert text into knowledge graph
        kg_manager.insert_text(request.text)
        
        return {"status": "success", "message": "Text inserted into knowledge graph"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kg/query")
async def kg_query(request: KGQueryRequest):
    try:
        # Initialize KG manager if not already initialized
        if not hasattr(kg_manager, 'rag') or kg_manager.rag is None:
            await kg_manager.initialize()
        
        # Query the knowledge graph
        result = kg_manager.query(
            query_text=request.query,
            mode=request.mode,
            top_k=request.top_k
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    # Get configuration from rag_app.config
    from rag_app import config
    
    print(f"Starting API server on {config.API_HOST}:{config.API_PORT}")
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )