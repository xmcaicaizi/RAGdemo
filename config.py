import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# --- 全局配置 ---
# 通过修改此变量来选择使用的 Embedding 服务: "ollama" 或 "dashscope"
EMBEDDING_PROVIDER = "ollama"  # 或者 "dashscope"

# 数据和数据库路径
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "exam_questions"
DATA_FILE = "questions.csv"

# --- Ollama 配置 ---
OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "dengcao/qwen3-embedding-0.6b"
}

# --- 阿里云 DashScope 配置 ---
DASHSCOPE_CONFIG = {
    "api_key": os.getenv("DASHSCOPE_API_KEY"),
    "model": "text-embedding-v4",
    "dimensions": 1024  # text-embedding-v4 支持的维度之一
}

# --- API 服务配置 ---
API_HOST = "0.0.0.0"
API_PORT = 8000


# --- 配置验证 ---
def validate_config():
    """检查所选提供商的配置是否正确"""
    print(f"当前选择的 Embedding 服务提供商: {EMBEDDING_PROVIDER}")
    if EMBEDDING_PROVIDER == "dashscope":
        if not DASHSCOPE_CONFIG["api_key"] or DASHSCOPE_CONFIG["api_key"] == "YOUR_DASHSCOPE_API_KEY_HERE":
            raise ValueError(
                "错误: DashScope API Key 未设置. "
                "请将 .env_template 文件重命名为 .env 并填入您的 API Key."
            )
        print("DashScope 配置验证通过。")
    elif EMBEDDING_PROVIDER == "ollama":
        print("Ollama 配置已选择。请确保 Ollama 服务正在运行。")
    else:
        raise ValueError(f"错误: 无效的 EMBEDDING_PROVIDER: '{EMBEDDING_PROVIDER}'. "
                         f"请选择 'ollama' 或 'dashscope'.")

# 在模块加载时执行验证
try:
    validate_config()
except ValueError as e:
    print(e)
    exit(1) 