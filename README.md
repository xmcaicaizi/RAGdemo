# RAG 功能模块与 API 服务

本项目提供了一个封装好的 RAG (Retrieval-Augmented Generation) 功能模块，以及一个基于该模块的 FastAPI 服务。它旨在为试卷客观题构建一个高效的 RAG 知识库，并支持在 **Ollama 本地部署**和**阿里云 DashScope 云服务**之间灵活切换 Embedding 模型。

## 核心架构：`RAGManager` 模块

项目的核心是 `rag_module.py` 文件中定义的 `RAGManager` 类。这个类封装了所有 RAG 相关的核心逻辑，包括：

-   **初始化**: 自动根据 `config.py` 连接到 ChromaDB 并设置好所选的 Embedding 服务（Ollama 或 DashScope）。
-   **知识库构建**: 提供 `build_from_csv(csv_file_path)` 方法，可以调用此方法并传入一个 CSV 文件路径来构建或更新知识库。
-   **检索**: 提供 `search(query, top_k)` 方法，用于在知识库中执行语义检索。

这种设计使得 RAG 功能可以被轻松地集成到任何 Python 项目中，或者作为一个独立的 API 服务运行。

## 功能特性

- **模块化设计**: 核心功能被封装在 `RAGManager` 类中，实现了逻辑和服务的分离。
- **双模支持**: 可在本地 Ollama 和云端 DashScope 之间一键切换。
- **调用灵活**:
    1.  可以直接在代码中实例化 `RAGManager` 并调用其方法来构建知识库。
    2.  可以通过运行一个独立的 FastAPI 服务来提供 RESTful 风格的 RAG 检索接口。
- **n8n 兼容**: API 接口可以无缝集成到 n8n 等自动化工作流中。

## 如何使用

### 第一步：环境与配置

1.  **创建虚拟环境并安装依赖**:
    ```bash
    # 创建并激活虚拟环境 (例如 venv)
    python -m venv venv
    source venv/bin/activate  # 或者 .\venv\Scripts\activate
    
    # 安装依赖
    pip install -r requirements.txt
    ```

2.  **配置 Embedding 服务**:
    - 打开 `config.py` 文件。
    - 将 `EMBEDDING_PROVIDER` 设置为 `"ollama"` 或 `"dashscope"`。
    - 如果使用 `"dashscope"`，请确保已创建 `.env` 文件并填入 `DASHSCOPE_API_KEY`。
    - 如果使用 `"ollama"`，请确保 Ollama 服务正在运行，并且模型名称与 `config.py` 中的配置匹配。

### 第二步：构建知识库（调用功能模块）

现在，您可以通过运行 `build_knowledge_base.py` 脚本来构建知识库。这个脚本实际上就是对 `RAGManager` 模块的调用演示。

```bash
python build_knowledge_base.py
```

该脚本会实例化 `RAGManager` 并调用 `build_from_csv` 方法，使用 `config.py` 中指定的 `DATA_FILE` (`questions.csv`)。

### 第三步：启动 RAG 检索服务 (RESTful API)

运行 `main.py` 来启动 FastAPI 服务。该服务在启动时会创建一个 `RAGManager` 实例，并用它来处理所有 `/search` 请求。

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后，您可以访问 [http://localhost:8000/docs](http://localhost:8000/docs) 来测试 API 接口。

### 在您自己的项目中使用 `RAGManager`

您可以非常容易地将这个 RAG 模块集成到您自己的代码中。

```python
# 在您的 aplication.py 中
from rag_module import RAGManager
from config import DATA_FILE

# 1. 初始化管理器
my_rag_manager = RAGManager()

# 2. 从您的 CSV 文件构建知识库
my_rag_manager.build_from_csv('path/to/your/data.csv')

# 3. 执行搜索
search_results = my_rag_manager.search("在Python里怎么定义一个函数？", top_k=3)

print(search_results)
```

## 文件结构

```
.
├── .env_template            # 环境变量模板，用于存放 API Key
├── .gitignore               # 忽略不需要版本控制的文件
├── build_knowledge_base.py  # [脚本] 调用 RAGManager 构建知识库的示例
├── config.py                # [核心配置] 服务选择、模型名称、路径等
├── embedding_functions.py   # [模块] 自定义的 DashScope Embedding 函数
├── main.py                  # [API] 基于 RAGManager 的 FastAPI 服务
├── rag_module.py            # [核心模块] 包含 RAGManager 类
├── questions.csv            # [数据] 示例试卷数据
└── requirements.txt         # Python 依赖列表
``` 