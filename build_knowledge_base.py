import chromadb
import pandas as pd
from chromadb.utils import embedding_functions as chroma_ef
from embedding_functions import DashScopeEmbeddingFunction  # 导入我们自定义的函数
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

def build_knowledge_base():
    """
    从CSV文件读取试卷数据，进行语义切片，生成向量，并构建或更新ChromaDB知识库。
    """
    print("--- 开始构建知识库 ---")

    # 1. 初始化 ChromaDB 客户端
    try:
        client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        print("成功连接到 ChromaDB。")
    except Exception as e:
        print(f"错误：无法连接到 ChromaDB at {config.CHROMA_PATH}。")
        print(f"详细错误: {e}")
        return

    # 2. 根据配置获取 embedding function
    try:
        embedding_function = get_embedding_function()
    except ValueError as e:
        print(e)
        return

    # 3. 获取或创建集合，并指定 embedding 函数
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_function
    )
    print(f"成功获取或创建集合: '{config.COLLECTION_NAME}'")

    # 4. 读取并处理数据
    try:
        df = pd.read_csv(config.DATA_FILE)
        print(f"成功读取数据文件: '{config.DATA_FILE}'，共 {len(df)} 行。")
    except FileNotFoundError:
        print(f"错误：数据文件 '{config.DATA_FILE}' 未找到。")
        return

    documents = []
    metadatas = []
    ids = []

    print("开始处理数据并准备存入知识库...")
    for index, row in df.iterrows():
        doc_text = f"题目：{row['question_text']} 选项{row['option_key']}：{row['option_text']}"
        documents.append(doc_text)
        metadatas.append({
            "question_id": str(row['question_id']),
            "question_text": row['question_text'],
            "option_key": row['option_key'],
            "option_text": row['option_text'],
            "is_correct": bool(row['is_correct'])
        })
        unique_id = f"q{row['question_id']}_{row['option_key']}"
        ids.append(unique_id)

    # 5. 检查文档是否已存在，避免重复添加
    existing_ids = collection.get(ids=ids)['ids']
    new_documents = []
    new_metadatas = []
    new_ids = []

    for i, doc_id in enumerate(ids):
        if doc_id not in existing_ids:
            new_documents.append(documents[i])
            new_metadatas.append(metadatas[i])
            new_ids.append(ids[i])
    
    if not new_documents:
        print("所有数据均已存在于知识库中，无需添加。")
        print("--- 知识库构建完成 ---")
        return

    # 6. 将新数据批量添加到 ChromaDB
    try:
        print(f"准备向知识库中添加 {len(new_documents)} 条新数据...")
        # ChromaDB 将使用我们设置的 embedding_function 自动生成向量
        collection.add(
            documents=new_documents,
            metadatas=new_metadatas,
            ids=new_ids
        )
        print(f"成功将 {len(new_documents)} 条知识对存入 ChromaDB！")
    except Exception as e:
        print("错误：向 ChromaDB 添加数据时发生错误。")
        print(f"请检查您的 '{config.EMBEDDING_PROVIDER}' 服务是否配置正确且正在运行。")
        print(f"详细错误: {e}")

    print("--- 知识库构建完成 ---")


if __name__ == "__main__":
    build_knowledge_base() 