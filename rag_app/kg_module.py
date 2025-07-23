"""
Knowledge Graph module using LightRAG for building and querying knowledge graphs.
This module integrates with the existing RAG system to provide knowledge graph capabilities.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_embed, openai_complete_if_cache
from lightrag.utils import setup_logger

from . import config


class KGManager:
    """
    Knowledge Graph Manager using LightRAG to build and query knowledge graphs.
    """
    
    def __init__(self):
        """
        Initialize the KGManager.
        """
        print("Initializing KGManager...")
        self.config = config
        self.working_dir = "./kg_storage"
        
        # Create working directory if it doesn't exist
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)
            
        # Setup logger
        setup_logger("lightrag", level="INFO")
        
        # Initialize RAG instance (will be set in initialize method)
        self.rag = None
        
        print("KGManager initialized.")
    
    async def _llm_model_func(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: List[Dict] = [],
        keyword_extraction: bool = False,
        **kwargs
    ) -> str:
        """
        LLM model function for LightRAG.
        Uses Ollama or DashScope based on configuration.
        """
        if self.config.EMBEDDING_PROVIDER == "ollama":
            # For Ollama, we would need to implement a proper integration
            # This is a placeholder implementation
            raise NotImplementedError("Ollama integration for LLM not implemented yet")
        elif self.config.EMBEDDING_PROVIDER == "dashscope":
            # Use DashScope API
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DASHSCOPE_API_KEY not set in environment variables")
            
            return await openai_complete_if_cache(
                "qwen-plus",  # Using Qwen-Plus as default model
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {self.config.EMBEDDING_PROVIDER}")
    
    async def _embedding_func(self, texts: List[str]) -> np.ndarray:
        """
        Embedding function for LightRAG.
        Uses Ollama or DashScope based on configuration.
        """
        if self.config.EMBEDDING_PROVIDER == "ollama":
            # Placeholder for Ollama embedding integration
            raise NotImplementedError("Ollama embedding integration not implemented yet")
        elif self.config.EMBEDDING_PROVIDER == "dashscope":
            # Use DashScope embedding
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DASHSCOPE_API_KEY not set in environment variables")
                
            return await openai_embed(
                texts,
                model="text-embedding-v2",  # Using DashScope embedding model
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        else:
            raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {self.config.EMBEDDING_PROVIDER}")
    
    async def initialize(self):
        """
        Initialize the LightRAG instance with proper LLM and embedding functions.
        """
        print("Initializing LightRAG...")
        
        try:
            self.rag = LightRAG(
                working_dir=self.working_dir,
                llm_model_func=self._llm_model_func,
                embedding_func=lambda texts: asyncio.run(self._embedding_func(texts)),
            )
            
            # Initialize storage backends
            await self.rag.initialize_storages()
            
            print("LightRAG initialized successfully.")
        except Exception as e:
            print(f"Error initializing LightRAG: {e}")
            raise
    
    def insert_text(self, text: str):
        """
        Insert text into the knowledge graph.
        
        Args:
            text (str): Text to insert into the knowledge graph
        """
        if self.rag is None:
            raise RuntimeError("KGManager not initialized. Call initialize() first.")
            
        print(f"Inserting text into knowledge graph: {text[:100]}...")
        try:
            # LightRAG's insert method is async, so we need to run it in an event loop
            asyncio.run(self.rag.insert(text))
            print("Text inserted successfully.")
        except Exception as e:
            print(f"Error inserting text: {e}")
            raise
    
    def query(self, query_text: str, mode: str = "hybrid", **kwargs) -> Dict[str, Any]:
        """
        Query the knowledge graph.
        
        Args:
            query_text (str): Query text
            mode (str): Query mode (local, global, hybrid, naive, mix)
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing query results
        """
        if self.rag is None:
            raise RuntimeError("KGManager not initialized. Call initialize() first.")
            
        print(f"Querying knowledge graph with mode '{mode}': {query_text}")
        
        try:
            # Create query parameters
            query_param = QueryParam(
                mode=mode,
                **kwargs
            )
            
            # Execute query (LightRAG query is async)
            result = asyncio.run(self.rag.query(query_text, param=query_param))
            
            return {
                "query": query_text,
                "mode": mode,
                "result": result
            }
        except Exception as e:
            print(f"Error querying knowledge graph: {e}")
            raise
    
    def build_from_file(self, file_path: str):
        """
        Build knowledge graph from a text file.
        
        Args:
            file_path (str): Path to the text file
        """
        if self.rag is None:
            raise RuntimeError("KGManager not initialized. Call initialize() first.")
            
        print(f"Building knowledge graph from file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Insert content into knowledge graph
            self.insert_text(content)
            
            print("Knowledge graph built successfully from file.")
        except Exception as e:
            print(f"Error building knowledge graph from file: {e}")
            raise


# Example usage (commented out)
"""
# Initialize the KGManager
kg_manager = KGManager()

# Initialize LightRAG (async)
await kg_manager.initialize()

# Insert text
kg_manager.insert_text("Alan Turing was a British mathematician and computer scientist.")

# Query the knowledge graph
result = kg_manager.query("Who was Alan Turing?", mode="hybrid")
print(result)
"""