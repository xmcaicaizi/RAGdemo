# 基于 Ollama 和 Qwen3-Embedding 的 RAG 知识库 API

本项目是一个完整的示例，演示了如何使用 Ollama 在本地运行 `qwen3-embedding` 模型，为试卷客观题构建一个基于“语义切片”的 RAG (Retrieval-Augmented Generation) 知识库，并通过一个 FastAPI 接口供 n8n 等工具调用。

## 核心技术栈

- **模型运行**: `Ollama` - 本地部署和管理大语言模型。
- **Embedding 模型**: `qwen3-embedding-0.6b` - 阿里开源高性能中文 Embedding 模型。
- **向量数据库**: `ChromaDB` - 轻量级、对开发者友好的开源向量数据库。
- **API 框架**: `FastAPI` - 高性能的现代 Python Web 框架。
- **数据处理**: `pandas` - 用于方便地处理 CSV 格式的试卷数据。

## 功能特性

- **本地化部署**: 所有模型和数据均在本地处理，确保数据隐私和安全。
- **语义切片**: 将“题目+选项”作为独立的知识单元进行向量化，实现更精细、准确的语义检索。
- **n8n 兼容**: 提供标准的 RESTful API 接口，可以无缝集成到 n8n 的自动化工作流中。
- **开箱即用**: 提供了完整的代码和示例数据，只需几步即可运行。
- **高可扩展性**: 可以轻松替换 Embedding 模型、数据源和向量数据库。

## 环境准备

在开始之前，请确保您已经安装了以下软件：

1.  **Python 3.8+**: [Python 官网](https://www.python.org/)
2.  **Ollama**: [Ollama 官网](https://ollama.com/)

## 安装与运行指南

按照以下步骤来设置和运行项目：

### 1. 下载项目文件

将项目的所有文件 (`main.py`, `build_knowledge_base.py`, `questions.csv`, `requirements.txt`, `.gitignore`) 下载到您的本地工作目录。

### 2. 安装 Ollama 并拉取模型

安装 Ollama 后，在终端中运行以下命令来下载 `qwen3-embedding-0.6b` 模型。如果您有足够的硬件资源（如 >16GB RAM），也可以选择性能更强的 `dengcao/qwen3-embedding-8b` 模型。

```bash
ollama pull dengcao/qwen3-embedding-0.6b
```

您可以通过 `ollama list` 命令确认模型已成功安装。

### 3. 安装 Python 依赖
创建一个虚拟环境
```bash
python -m venv myenv
```

切换至虚拟环境
```bash
myenv/Scripts/activate
```

在项目根目录下，使用 `pip` 安装所有必需的 Python 库。

```bash
pip install -r requirements.txt
```

### 4. 构建知识库

这是将您的试卷数据向量化并存入 ChromaDB 的关键一步。

在终端中运行以下脚本：

```bash
python build_knowledge_base.py
```

您将看到类似以下的输出，表明数据正在被处理并存入本地的 `chroma_db` 目录中：

```
--- 开始构建知识库 ---
成功连接到 ChromaDB。
成功获取或创建集合: 'exam_questions'
成功读取数据文件: 'questions.csv'，共 12 行。
开始处理数据并准备存入知识库...
准备向知识库中添加 12 条新数据...
成功将 12 条知识对存入 ChromaDB！
--- 知识库构建完成 ---
```

**注意**: 此脚本有幂等性设计，重复运行不会重复添加相同的数据。

### 5. 启动 API 服务

知识库构建完成后，启动 FastAPI 应用来提供检索服务。

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，您会看到如下信息：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
...
INFO:     Application startup complete.
```

### 6. 测试 API 接口

API 服务现在正在运行。您可以通过两种方式进行测试：

**a) 使用自动生成的 API 文档 (Swagger UI):**

在浏览器中访问 [http://localhost:8000/docs](http://localhost:8000/docs)。这是一个交互式文档页面，您可以在这里直接测试 `/search` 接口。

1.  点击 `/search` 端点展开它。
2.  点击 "Try it out"。
3.  在请求体中输入您的查询，例如：
    ```json
    {
      "query": "python里怎么定义一个函数",
      "top_k": 3
    }
    ```
4.  点击 "Execute"，您将在下方看到 JSON 格式的返回结果。

**b) 使用 `curl` 命令:**

打开一个新的终端，运行以下命令：

```bash
curl -X 'POST' \
  'http://localhost:8000/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "python数据类型",
  "top_k": 2
}'
```

### 7. 在 n8n 中集成

1.  在您的 n8n 工作流中，添加一个 **HTTP Request** 节点。
2.  配置该节点：
    - **Method**: `POST`
    - **URL**: `http://<您的IP地址>:8000/search` (如果 n8n 和 API 运行在同一台机器上，可以使用 `http://localhost:8000/search`)
    - **Body Content Type**: `JSON`
    - **JSON/RAW Parameters**: `On`
    - 在 **Body** 区域输入您的查询，可以使用 n8n 的表达式动态传入：
      ```json
      {
        "query": "{{ $json.question }}",
        "top_k": 3
      }
      ```
3.  执行该节点，即可在 n8n 中获取 RAG 检索结果，并将其传递给后续节点进行处理。

## 文件结构

```
.
├── .gitignore               # 忽略不需要版本控制的文件
├── build_knowledge_base.py  # [脚本] 读取CSV，构建向量知识库
├── main.py                  # [核心] FastAPI 应用，提供 API 接口
├── questions.csv            # [数据] 示例试卷数据
└── requirements.txt         # Python 依赖列表
``` 