import ollama
import chromadb
import pandas as pd
import uuid
from chromadb.utils import embedding_functions

# --- 配置 ---
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = 'dengcao/qwen3-embedding-0.6b'
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "exam_questions"
DATA_FILE = "questions.csv" # 您的试卷数据文件

def build_knowledge_base():
    """
    从CSV文件读取试卷数据，进行语义切片，生成向量，并构建或更新ChromaDB知识库。
    """
    print("--- 开始构建知识库 ---")
    
    # 1. 初始化 ChromaDB 客户端
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        print("成功连接到 ChromaDB。")
    except Exception as e:
        print(f"错误：无法连接到 ChromaDB at {CHROMA_PATH}。请确保ChromaDB服务正在运行。")
        print(f"详细错误: {e}")
        return

    # 2. 定义 Embedding 函数，指定Ollama模型
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url=f"{OLLAMA_HOST}/api/embeddings",
        model_name=OLLAMA_MODEL,
    )

    # 3. 获取或创建集合，并指定 embedding 函数
    # 这让 ChromaDB 在添加文档时自动调用 Ollama 生成向量
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ollama_ef
    )
    print(f"成功获取或创建集合: '{COLLECTION_NAME}'")

    # 4. 读取并处理数据
    try:
        df = pd.read_csv(DATA_FILE)
        print(f"成功读取数据文件: '{DATA_FILE}'，共 {len(df)} 行。")
    except FileNotFoundError:
        print(f"错误：数据文件 '{DATA_FILE}' 未找到。请确保文件存在于正确路径。")
        return

    documents = []
    metadatas = []
    ids = []

    print("开始处理数据并准备存入知识库...")
    for index, row in df.iterrows():
        # 构造“题目+选项”的语义切片
        doc_text = f"题目：{row['question_text']} 选项{row['option_key']}：{row['option_text']}"
        
        # 准备文档、元数据和ID
        documents.append(doc_text)
        metadatas.append({
            "question_id": str(row['question_id']),
            "question_text": row['question_text'],
            "option_key": row['option_key'],
            "option_text": row['option_text'],
            "is_correct": bool(row['is_correct'])
        })
        # 使用 question_id 和 option_key 生成一个确定性的、唯一的ID
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
    # ChromaDB 将使用我们之前设置的 ollama_ef 自动为 new_documents 生成向量
    try:
        print(f"准备向知识库中添加 {len(new_documents)} 条新数据...")
        collection.add(
            documents=new_documents,
            metadatas=new_metadatas,
            ids=new_ids
        )
        print(f"成功将 {len(new_documents)} 条知识对存入 ChromaDB！")
    except Exception as e:
        print("错误：向 ChromaDB 添加数据时发生错误。")
        print(f"请检查您的 Ollama 服务是否正在运行，并且 '{OLLAMA_MODEL}' 模型是否可用。")
        print(f"详细错误: {e}")

    print("--- 知识库构建完成 ---")


if __name__ == "__main__":
    build_knowledge_base() 