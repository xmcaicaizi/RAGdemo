from rag_app.rag_module import RAGManager
from rag_app import config

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