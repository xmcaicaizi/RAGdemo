# RAG 功能模块与 API 服务

本项目提供了一个封装好的 RAG (Retrieval-Augmented Generation) 功能模块，以及一个基于该模块的 FastAPI 服务。它旨在为试卷客观题构建一个高效的 RAG 知识库，并支持在 **Ollama 本地部署**和**阿里云 DashScope 云服务**之间灵活切换 Embedding 模型。

## 核心架构：`RAGManager` 模块

项目的核心是 `rag_module.py` 文件中定义的 `RAGManager` 类。这个类封装了所有 RAG 相关的核心逻辑，使得 RAG 功能可以被轻松地集成到任何 Python 项目中，或者作为一个独立的 API 服务运行。

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
    - 打开 `config.py` 文件，将 `EMBEDDING_PROVIDER` 设置为 `"ollama"` 或 `"dashscope"`。
    - 如果使用 `"dashscope"`，请确保已创建 `.env` 文件并填入 `DASHSCOPE_API_KEY`。
    - 如果使用 `"ollama"`，请确保 Ollama 服务正在运行，并且模型名称与 `config.py` 中的配置匹配。

### 第二步：选择使用模式

您可以根据需求，选择以下两种模式之一来使用本项目。

---

### 模式一：调用函数处理 `.CSV` 文件

此模式直接使用 `RAGManager` 模块来构建知识库，满足您的第一个需求。

**1. 运行示例脚本**

我们提供了一个 `build_knowledge_base.py` 脚本作为调用示例。它会实例化 `RAGManager` 并调用其 `build_from_csv` 方法来处理 `questions.csv` 文件。

```bash
python build_knowledge_base.py
```

**2. 在您自己的项目中使用**

您可以非常容易地将这个 RAG 模块集成到您自己的代码中，处理您指定的任何 CSV 文件。

```python
# 在您的 application.py 中
from rag_module import RAGManager

# 1. 初始化管理器
my_rag_manager = RAGManager()

# 2. 从您的 CSV 文件构建知识库
#    方法接收一个文件路径作为参数
my_rag_manager.build_from_csv('path/to/your/data.csv')

print("知识库构建完成！")
```

---

### 模式二：通过 RESTful API 进行 RAG 检索

此模式将项目作为一个独立的 API 服务运行，满足您的第二个需求。

**1. 启动 API 服务**

运行 `main.py` 来启动 FastAPI 服务。

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，您可以访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看交互式 API 文档。

**2. API 接口详解**

- **端点**: `POST /search`
- **功能**: 接收一个查询，返回最相关的 `k` 个知识对。
- **请求体 (Request Body)**:
    ```json
    {
      "query": "您要查询的问题文本",
      "top_k": 5
    }
    ```
    - `query` (str, 必需): 您的搜索问题。
    - `top_k` (int, 可选): 希望返回的结果数量，默认为 5。

- **成功响应 (Success Response)**: `200 OK`
    下面是一个返回结果的示例，包含了详细的字段说明。

    ```json
    {
      "provider": "ollama", // 当前使用的 Embedding 服务提供商
      "query": "python里怎么定义一个函数", // 您发送的原始查询
      "results": [ // 检索结果列表
        {
          "id": "q1_B", // 知识对的唯一ID (question_id + option_key)
          "content": "题目：在Python中，哪个关键字用于定义一个函数？ 选项B：def", // 知识对的原始内容
          "metadata": { // 原始的元数据
            "question_id": "1",
            "question_text": "在Python中，哪个关键字用于定义一个函数？",
            "option_key": "B",
            "option_text": "def",
            "is_correct": true // 指示该选项是否为正确答案
          },
          "distance": 0.23561... // 与查询向量的距离（或相似度得分），越小表示越相关
        },
        {
          "id": "q1_C",
          "content": "题目：在Python中，哪个关键字用于定义一个函数？ 选项C：function",
          "metadata": {
            "question_id": "1",
            "question_text": "在Python中，哪个关键字用于定义一个函数？",
            "option_key": "C",
            "option_text": "function",
            "is_correct": false
          },
          "distance": 0.89127...
        }
      ]
    }
    ```

## 文件结构

```
.
├── .env_template            # 环境变量模板
├── .gitignore               #
├── build_knowledge_base.py  # [模式一] 调用模块构建知识库的示例
├── config.py                # 全局配置文件
├── embedding_functions.py   # 自定义 Embedding 函数
├── main.py                  # [模式二] FastAPI 服务
├── rag_module.py            # [核心] RAGManager 模块
├── questions.csv            # 示例数据
└── requirements.txt         # Python 依赖
``` 