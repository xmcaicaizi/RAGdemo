# RAG and Fine-tuning for Qwen Models

This project provides two main packages:
1. A RAG (Retrieval-Augmented Generation) module for building and querying knowledge bases with semantic search and reranking capabilities
2. A fine-tuning module for customizing Qwen models on specific datasets using LoRA

The system is built on top of FastAPI for a high-performance API service, ChromaDB as the vector database, and integrates with both Ollama and DashScope for embedding generation.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Knowledge Base Multi-table Support](#knowledge-base-multi-table-support)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Features

### RAG Package
- **Build knowledge bases** from structured CSV data with intelligent slicing strategies
- **Semantic search** with configurable embedding models (Ollama or DashScope)
- **High-quality reranking** with Qwen3-Reranker cross-encoder for improved search relevance
- **Knowledge base monitoring** with a web-based interface for inspecting data fragments
- **RESTful API** for easy integration with other services
- **Powerful metadata analysis** for understanding your knowledge base composition

### Knowledge Graph Package
- **Knowledge graph construction** from unstructured text using LightRAG
- **Entity and relationship extraction** powered by large language models
- **Multiple query modes** including local, global, and hybrid search
- **Graph-based reasoning** for complex question answering
- **Integration with existing RAG system** for enhanced capabilities

### Fine-tuning Package
- **Support for fine-tuning Qwen models** using Parameter-Efficient Fine-Tuning (PEFT) with LoRA
- **Data preparation and preprocessing utilities** for formatting training data
- **Comprehensive training configuration** with customizable hyperparameters
- **Model evaluation tools** for assessing fine-tuned model performance
- **Integration with the RAG application** for end-to-end workflows

## Architecture

```
rag-qwen/
├── rag_app/                # RAG functionality package
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration settings
│   ├── embedding_functions.py # Custom embedding functions
│   ├── kg_module.py        # Knowledge Graph module using LightRAG
│   ├── monitor.py          # Monitoring module
│   ├── rag_module.py       # Core RAG module
│   ├── reranker.py         # Qwen3-Reranker module
│   ├── static/             # Static files for web UI
│   └── templates/          # HTML templates
│       └── monitor.html    # Monitoring page
│
├── finetune_app/           # Fine-tuning functionality package
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration settings
│   ├── finetune_module.py  # Core fine-tuning module
│   └── README.md           # Package documentation
│
├── tests/                  # Test directory
│   ├── test_finetune.py    # Tests for fine-tuning
│   └── test_rag.py         # Tests for RAG functionality
│
├── data/                   # Data directory (created at runtime)
│   ├── questions.csv       # Example data
│   └── ...                 # Other data files
│
├── models/                 # Model directory (created at runtime)
│   └── ...                 # Fine-tuned models
│
├── build_knowledge_base.py # Script to build knowledge base
├── main.py                 # Main application script
├── pyproject.toml          # Modern Python project configuration
├── setup.py                # Backward compatibility with older tools
├── requirements.txt        # Dependencies list
├── README.md               # Project documentation
├── api_documentation.md    # API documentation
└── .env_template           # Environment variables template
```

## Requirements

- Python 3.12+
- PyTorch 2.0+
- Transformers 4.51.0+
- FastAPI 0.104.0+
- ChromaDB 0.4.0+
- Ollama 0.1.0+ or DashScope API access
- LightRAG 1.0.0+

## Installation

### Prerequisites
1. Python 3.12+ installed
2. (Optional) Ollama service running with required models
3. (Optional) DashScope API key for cloud-based embeddings

### Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-qwen.git
cd rag-qwen

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

Note: For Windows users, you might need to enable script execution with `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` before activating the virtual environment.

## Configuration

1. Copy the environment template:
   ```bash
   cp .env_template .env
   ```

2. Edit `.env` to add your API keys and other settings:
   ```
   # API Keys
   DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY_HERE"
   
   # RAG Configuration
   EMBEDDING_PROVIDER="ollama"  # Options: "ollama" or "dashscope"
   CHROMA_PATH="./chroma_db"
   COLLECTION_NAME="exam_questions"
   
   # Ollama Configuration
   OLLAMA_HOST="http://localhost:11434"
   OLLAMA_MODEL="dengcao/Qwen3-Embedding-0.6B:F16"
   
   # Fine-tuning Configuration
   BASE_MODEL="Qwen/Qwen1.5-7B"
   USE_LORA="true"
   MODELS_DIR="./models"
   DATA_DIR="./data"
   ```

3. Configure the packages in:
   - `rag_app/config.py` for RAG settings
   - `finetune_app/config.py` for fine-tuning settings

## Usage

### Building a Knowledge Base

Before performing searches, you need to build a knowledge base from your data:

```bash
python build_knowledge_base.py
```

Or programmatically:

```python
from rag_app.rag_module import RAGManager

# Initialize the RAG manager
rag_manager = RAGManager()

# Build knowledge base from CSV
rag_manager.build_from_csv('questions.csv')
```

### RAG Module

```python
from rag_app.rag_module import RAGManager

# Initialize the RAG manager
rag_manager = RAGManager()

# Build knowledge base from CSV
rag_manager.build_from_csv('questions.csv')

# Search the knowledge base
results = rag_manager.search("python里怎么定义一个函数？", top_k=3)

# Search with reranking
reranked_results = rag_manager.search_with_rerank(
    query="python里怎么定义一个函数？", 
    top_k=3
)
```

### Knowledge Graph Module

```python
from rag_app.kg_module import KGManager
import asyncio

# Initialize the KG manager
kg_manager = KGManager()

# Initialize LightRAG (required for KG functionality)
await kg_manager.initialize()

# Insert text into knowledge graph
kg_manager.insert_text("Alan Turing was a British mathematician and computer scientist. He formalized the concepts of algorithm and computation with the Turing machine.")

# Query the knowledge graph (multiple modes available: local, global, hybrid)
result = kg_manager.query("Who was Alan Turing?", mode="hybrid")
print(result)
```

### Fine-tuning Module

```python
from finetune_app.finetune_module import FineTuneManager

# Initialize the fine-tuning manager
ft_manager = FineTuneManager()

# Prepare your data
data_dir = ft_manager.prepare_data("path/to/your/data.json")

# Load the base model
ft_manager.load_model()

# Fine-tune the model
model_path = ft_manager.fine_tune(train_data_dir=data_dir)

# Evaluate the fine-tuned model
metrics = ft_manager.evaluate(model_path=model_path)
```

## API Endpoints

Run the API service to access both RAG and fine-tuning functionality:

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Available Endpoints

- **API Root**: [http://localhost:8000/](http://localhost:8000/) - Shows available endpoints
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interactive API documentation
- **Monitor UI**: [http://localhost:8000/monitor](http://localhost:8000/monitor) - Knowledge base monitoring interface
- **Search**: `POST /search` - Semantic search in knowledge base
- **Reranked Search**: `POST /search/reranked` - Search with Qwen3-Reranker reranking
- **Fine-tuning**: `POST /finetune` - Fine-tune a Qwen model
- **Monitor Stats**: `GET /monitor/stats` - Get knowledge base statistics
- **Monitor Samples**: `GET /monitor/samples` - Get sample knowledge base entries
- **KG Insert**: `POST /kg/insert` - Insert text into knowledge graph
- **KG Query**: `POST /kg/query` - Query the knowledge graph

For detailed API documentation, see [API Documentation](./api_documentation.md).

## Knowledge Base Multi-table Support

The project supports multiple structured objective question tables, with specialized processing for:
- `计算机组成原理客观题.csv` (Computer Organization Objective Questions)
- `数字逻辑客观题.csv` (Digital Logic Objective Questions)

For these tables, the knowledge slicing method is: **only concatenate "question stem + options"**, such as:
```
在编译选项当中增加 –fopenmp。如果修改第25行代码... A. 对
```

No need to retain complete field information, making the database content more concise.

Other tables will continue to use the original "question + options + metadata" slicing logic.

## Knowledge Graph Capabilities

This project now includes knowledge graph capabilities powered by LightRAG. The knowledge graph module can:

1. Extract entities and relationships from unstructured text
2. Build a graph representation of the knowledge
3. Perform complex reasoning through graph traversal
4. Support multiple query modes (local, global, hybrid)

### Query Modes

- **Local Mode**: Focuses on context-dependent information, suitable for specific entity queries
- **Global Mode**: Utilizes global knowledge, ideal for relationship discovery
- **Hybrid Mode**: Combines local and global retrieval methods for comprehensive answers

## Monitoring

The project includes a web-based monitoring interface that allows you to:
- View knowledge base statistics
- Browse data samples with pagination
- Analyze metadata distribution
- Test search functionality

Access the monitor at [http://localhost:8000/monitor](http://localhost:8000/monitor) when the API service is running.

## Testing

The project includes test suites for both RAG and fine-tuning modules:

```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_rag.py
python -m pytest tests/test_finetune.py
```

## Troubleshooting

### Common Issues

1. **Service Unavailable Errors**: Ensure your Ollama service is running if using the Ollama provider
2. **API Key Errors**: Verify your DashScope API key is correctly set in the `.env` file
3. **Model Loading Issues**: Check that required models are downloaded and available
4. **Port Conflicts**: Change the `API_PORT` in `rag_app/config.py` if port 8000 is in use

### Getting Help

For issues not covered in this README:
1. Check the detailed [API Documentation](./api_documentation.md)
2. Review the [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
3. Open an issue on the GitHub repository

For a more detailed implementation summary, see [Implementation Summary](./IMPLEMENTATION_SUMMARY.md).