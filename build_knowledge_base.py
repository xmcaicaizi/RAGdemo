import chromadb
import pandas as pd
from chromadb.utils import embedding_functions as chroma_ef
from embedding_functions import DashScopeEmbeddingFunction  # 导入我们自定义的函数
from rag_module import RAGManager
import config  # 导入配置文件

def get_embedding_function():
    """
    根据配置文件选择并返回相应的 embedding function。
    """
    if config.EMBEDDING_PROVIDER == "ollama":
        print(f"使用 Ollama: {config.OLLAMA_CONFIG['host']}, 模型: {config.OLLAMA_CONFIG['model']}")
        return chroma_ef.OllamaEmbeddingFunction(
            url=f"{config.OLLAMA_CONFIG['host']}/api/embeddings",
            model_name=config.OLLAMA_CONFIG['model'],
        )
    elif config.EMBEDDING_PROVIDER == "dashscope":
        print(f"使用 DashScope, 模型: {config.DASHSCOPE_CONFIG['model']}")
        return DashScopeEmbeddingFunction(
            api_key=config.DASHSCOPE_CONFIG['api_key'],
            model=config.DASHSCOPE_CONFIG['model'],
            dimensions=config.DASHSCOPE_CONFIG['dimensions']
        )
    else:
        # 这个错误理论上在 config.py 中已经被捕获，但作为双重保障
        raise ValueError(f"无效的 EMBEDDING_PROVIDER: {config.EMBEDDING_PROVIDER}")

def main():
    """
    该脚本用于从 CSV 文件构建或更新 RAG 知识库。
    它实例化 RAGManager 并调用其 build_from_csv 方法。
    """
    print("--- 知识库构建脚本启动 ---")
    try:
        # 1. 初始化 RAG 管理器
        # RAGManager 在其构造函数中处理所有必要的设置
        rag_manager = RAGManager()

        # 2. 从 CSV 文件构建知识库
        # 使用配置文件中定义的默认数据文件
        rag_manager.build_from_csv(config.DATA_FILE)

    except Exception as e:
        print(f"脚本执行过程中发生未处理的错误: {e}")
        # 可以在这里添加更详细的错误处理或日志记录

    print("--- 知识库构建脚本执行完毕 ---")

if __name__ == "__main__":
    main() 