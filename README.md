# 基于 Ollama 和 DashScope 的可切换 RAG 知识库 API

本项目是一个灵活的、可配置的 RAG 解决方案，演示了如何为试卷客观题构建一个基于“语义切片”的知识库。它同时支持 **Ollama 本地部署**和**阿里云 DashScope 云服务**两种 Embedding 模式，您可以通过简单的配置进行切换。

该项目通过一个 FastAPI 接口提供服务，可轻松与 n8n 等自动化工具集成。

## 核心技术栈

- **Embedding 服务 (可切换)**:
    - **`Ollama`**: 在本地轻松部署和管理大语言模型，如 `qwen3-embedding`。
    - **`DashScope`**: 使用阿里云百炼提供的 `text-embedding-v4` 等高性能在线 Embedding 服务。
- **向量数据库**: `ChromaDB` - 轻量级、对开发者友好的开源向量数据库。
- **API 框架**: `FastAPI` - 高性能的现代 Python Web 框架。
- **配置管理**: `python-dotenv` - 用于安全管理 API 密钥等敏感信息。

## 功能特性

- **双模支持**: 可在本地 Ollama 和云端 DashScope 之间一键切换，兼顾开发便利性、数据隐私和生产级性能。
- **模块化设计**: 通过配置文件 (`config.py`) 和自定义 Embedding 函数，将服务选择与核心逻辑解耦。
- **语义切片**: 将“题目+选项”作为独立的知识单元进行向量化，实现更精细、准确的语义检索。
- **n8n 兼容**: 提供标准的 RESTful API 接口，可以无缝集成到 n8n 的自动化工作流中。
- **开箱即用**: 提供了完整的代码和示例数据，只需几步即可运行。

## 安装与运行指南

### 1. 下载项目文件

将项目的所有文件下载到您的本地工作目录。

### 2. 环境与依赖安装

**a) 创建并激活虚拟环境 (推荐)**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**b) 安装 Python 依赖**

```bash
pip install -r requirements.txt
```

### 3. 配置 Embedding 服务

这是关键的一步。您需要决定使用 Ollama 还是 DashScope。

**a) 选项一：使用 Ollama (本地部署)**

1.  **安装 Ollama**: 访问 [Ollama 官网](https://ollama.com/) 并根据您的操作系统进行安装。
2.  **拉取模型**: 在终端中运行以下命令来下载 `qwen3-embedding` 模型。

    ```bash
    ollama pull dengcao/qwen3-embedding-0.6b
    ```
3.  **配置项目**: 打开 `config.py` 文件，确保 `EMBEDDING_PROVIDER` 设置为 `"ollama"`。

    ```python
    # config.py
    EMBEDDING_PROVIDER = "ollama"
    ```

**b) 选项二：使用 阿里云 DashScope (云服务)**

1.  **获取 API Key**: 登录您的阿里云百炼控制台，获取 API Key。
2.  **配置环境变量**:
    - 将 `.env_template` 文件重命名为 `.env`。
    - 打开 `.env` 文件，将您的 API Key 填入其中。
      ```
      DASHSCOPE_API_KEY="sk-your-real-api-key"
      ```
3.  **配置项目**: 打开 `config.py` 文件，将 `EMBEDDING_PROVIDER` 修改为 `"dashscope"`。

    ```python
    # config.py
    EMBEDDING_PROVIDER = "dashscope"
    ```
    您还可以根据需要在 `config.py` 中修改 `DASHSCOPE_CONFIG` 下的模型或向量维度。

### 4. 构建知识库

配置好 Embedding 服务后，运行脚本来处理 `questions.csv` 数据并存入 ChromaDB。

```bash
python build_knowledge_base.py
```

脚本会根据您在 `config.py` 中的设置，自动调用 Ollama 或 DashScope 来生成向量。

### 5. 启动 API 服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 测试与集成

服务启动后，您可以像之前一样通过访问 [http://localhost:8000/docs](http://localhost:8000/docs) 或使用 `curl` 命令进行测试。返回的 JSON 结果中会包含一个 `provider` 字段，明确指出当前使用的是哪个 Embedding 服务。

与 n8n 的集成方式保持不变。

## 文件结构

```
.
├── .env_template            # 环境变量模板，用于存放 API Key
├── .gitignore               # 忽略不需要版本控制的文件
├── build_knowledge_base.py  # [脚本] 读取CSV，构建向量知识库
├── config.py                # [核心配置] 服务选择、模型名称、路径等
├── embedding_functions.py   # [模块] 自定义的 DashScope Embedding 函数
├── main.py                  # [核心] FastAPI 应用，提供 API 接口
├── questions.csv            # [数据] 示例试卷数据
└── requirements.txt         # Python 依赖列表
``` 