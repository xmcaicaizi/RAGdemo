# RAG 功能模块与 API 服务

本项目提供了一个封装好的 RAG (Retrieval-Augmented Generation) 功能模块。其核心是 `RAGManager` 类，它封装了构建和查询 RAG 知识库的所有逻辑。

同时，本项目也提供了多个使用该模块的示例：
- 通过脚本批量构建知识库
- 将检索功能包装成 RESTful API 服务
- **监视模块**：提供可视化前端展示，查看RAG库里的数据片段
- **Reranker功能**：对初步检索结果进行重新排序，提升相关性

## 核心模块: `RAGManager`

所有核心功能都封装在 `rag_app/rag_module.py` 的 `RAGManager` 类中。您可以直接在您的 Python 项目中导入并使用它。

### 初始化

`RAGManager` 在初始化时会自动读取 `rag_app/config.py` 中的配置，并设置好所有必要的组件。

```python
from rag_app.rag_module import RAGManager

# 初始化管理器，所有配置将自动加载
rag_manager = RAGManager()
```

### 方法一: 构建知识库

使用 `build_from_csv(csv_file_path: str)` 方法来处理 CSV 文件并填充知识库。该方法接收一个文件路径作为参数。

```python
# 调用方法，传入您的 CSV 文件路径
rag_manager.build_from_csv('path/to/your/questions.csv')
```

### 方法二: 检索知识库

使用 `search(query: str, top_k: int)` 方法来执行语义检索。

```python
# 调用方法，传入查询文本和需要返回的结果数量
search_results = rag_manager.search(
    query="python里怎么定义一个函数？", 
    top_k=3
)

# 打印结果
import json
print(json.dumps(search_results, indent=2, ensure_ascii=False))
```
该方法返回的 `search_results` 是一个字典，其结构在下面的 API 示例中有详细说明。

---

## API 文档

为了方便开发者快速理解和使用本项目的 API，我们提供了详细的接口规范文档。

- **[API 接口文档](./api_documentation.md)**: 点击查看所有接口的详细定义、请求/响应格式及示例。

---

## 使用示例

以下是两个使用 `RAGManager` 模块的示例脚本。

### 示例 A: 通过脚本构建知识库

`build_knowledge_base.py` 脚本演示了如何调用 `RAGManager` 来处理在 `config.py` 中定义的默认 CSV 文件。

**1. 配置与环境**
   - 确保已安装依赖 (`pip install -r requirements.txt`)。
   - 在 `rag_app/config.py` 中配置好您的 Embedding 服务。

**2. 运行脚本**
   ```bash
   python build_knowledge_base.py
   ```

### 示例 B: 将检索功能包装为 RESTful API

`main.py` 脚本演示了如何将 `RAGManager` 的检索功能包装成一个 FastAPI 服务，这对于需要跨语言调用或与 n8n 等工具集成的场景非常有用。

**1. 启动 API 服务**
   - 确保知识库已经通过示例 A 或其他方式构建完毕。
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   - 访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看交互式 API 文档。
   - 访问 [http://localhost:8000/monitor](http://localhost:8000/monitor) 查看知识库监视页面。

**2. API 接口详解 (`POST /search`)**

   - **请求体 (Request Body)**:
     ```json
     {
       "query": "您要查询的问题文本",
       "top_k": 5
     }
     ```

   - **成功响应 (Success Response)**:
     ```json
     {
       "provider": "ollama", 
       "query": "python里怎么定义一个函数",
       "results": [
         {
           "id": "q1_B",
           "content": "题目：在Python中，哪个关键字用于定义一个函数？ 选项B：def",
           "metadata": {
             "question_id": "1",
             "question_text": "在Python中，哪个关键字用于定义一个函数？",
             "option_key": "B",
             "option_text": "def",
             "is_correct": true
           },
           "distance": 0.23561
         }
       ]
     }
     ```

### 示例 C: 监视模块

监视模块提供了可视化前端展示，可以查看当前RAG库里的数据片段。

**1. 访问监视页面**
   - 启动API服务后，访问 [http://localhost:8000/monitor](http://localhost:8000/monitor)
   - 查看知识库统计信息、数据样本和元数据分析

**2. 监视功能**
   - **统计信息**：查看总文档数、集合数量、平均内容长度等
   - **数据样本**：浏览知识库中的数据片段，支持分页
   - **搜索测试**：在界面上直接测试搜索功能
   - **元数据分析**：查看元数据字段的分布和统计

### 示例 D: Reranker功能

Reranker功能对初步检索结果进行重新排序，提升相关性。

**1. 重排序策略**
   - `similarity_score`：基于相似度分数重排序
   - `content_relevance`：基于内容相关性重排序
   - `metadata_weight`：基于元数据权重重排序
   - `hybrid`：混合多种策略的综合重排序

**2. 使用重排序搜索**
   ```bash
   curl -X POST "http://localhost:8000/search/reranked" \
        -H "Content-Type: application/json" \
        -d '{
          "query": "python里怎么定义一个函数？",
          "top_k": 5,
          "strategy": "hybrid"
        }'
   ```

## 文件结构

```
.
├── rag_app/                 # [核心模块] 封装好的 RAG 功能包
│   ├── __init__.py          # 标记为 Python 包
│   ├── config.py            # 模块的配置文件
│   ├── embedding_functions.py # 自定义的 Embedding 函数
│   ├── rag_module.py        # RAGManager 类的定义
│   ├── monitor.py           # 监视模块
│   ├── reranker.py          # 重排序模块
│   ├── static/              # 静态文件目录
│   └── templates/           # HTML模板目录
│       └── monitor.html     # 监视页面模板
│
├── build_knowledge_base.py  # [示例A] 调用模块构建知识库的脚本
├── main.py                  # [示例B] 将模块包装为 API 服务的脚本
├── api_documentation.md     # [文档] 详细的 API 接口规范
├── questions.csv            # 示例数据
├── requirements.txt         # Python 依赖
├── .env_template            # 环境变量模板
└── .gitignore               
``` 

---

## 知识库多表支持与切片逻辑

本项目支持多种结构化客观题表格的知识入库，当前已适配：

- `计算机组成原理客观题.csv`
- `数字逻辑客观题.csv`

对于上述两类表格，知识切片方式为：**每条知识仅拼接“题干+选项”**，如：

```
在编译选项当中增加 –fopenmp。如果修改第25行代码... A. 对
```

无需保留完整字段信息，入库内容更精炼。

> 其它表格将继续采用原有的“题目+选项+元数据”切片逻辑。

### 构建知识库示例

```bash
python build_knowledge_base.py  # 自动识别并处理上述表格
```

如需扩展更多表格类型或自定义切片方式，请修改 `rag_module.py` 的 `build_from_csv` 方法。 

---

## 2024-07 更新：Qwen3-Reranker Cross-Encoder 精排集成

### 新特性
- 集成了Qwen3-Reranker cross-encoder模型（支持本地量化模型如Qwen3-Reranker-4B:Q4_K_M）
- 检索流程：先用Qwen3-embedding做初步检索，再用Qwen3-reranker对候选切片进行精细化相关性打分排序
- 支持批量推理，效率更高
- `/search/reranked` API返回真实cross-encoder相关性分数排序结果

### 使用说明
1. **模型准备**
   - 下载Qwen3-Reranker-4B:Q4_K_M模型（本地路径或Ollama/Transformers支持的路径）
   - 默认模型名已设为`Qwen3-Reranker-4B:Q4_K_M`，如需更换请在`rag_app/reranker.py`中修改
2. **依赖**
   - 需安装`transformers`、`torch`等依赖
   - 推荐transformers>=4.51.0，torch>=2.0
3. **API调用**
   - `/search/reranked`端点将自动使用Qwen3-reranker cross-encoder进行精排
   - 返回结果中的`rerank_score`字段即为相关性分数

### 示例代码片段
```python
from rag_app.reranker import Qwen3Reranker
reranker = Qwen3Reranker()
scores = reranker.rerank(query, [chunk1, chunk2, ...])
```

### 性能建议
- 量化模型（如Q4_K_M）可大幅降低显存需求，适合本地部署
- 首次加载模型较慢，后续推理速度较快

--- 