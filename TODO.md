# RAGdemo 功能扩展 TODO

## 当前任务：添加监视模块和Reranker功能

### 1. 监视模块 (Monitor Module) ✅
**目标**: 提供可视化前端展示，查看当前RAG库里的数据片段

#### 子任务：
- [x] 创建 `rag_app/monitor.py` 模块
  - [x] 实现 `KnowledgeBaseMonitor` 类
  - [x] 添加获取知识库统计信息的方法
  - [x] 添加查看数据片段的方法
  - [x] 添加数据可视化功能
- [x] 创建前端界面
  - [x] 创建 `rag_app/static/` 目录存放静态文件
  - [x] 创建 `rag_app/templates/` 目录存放HTML模板
  - [x] 实现数据可视化页面
- [x] 在 `main.py` 中添加监视相关的API端点
  - [x] `GET /monitor/stats` - 获取知识库统计信息
  - [x] `GET /monitor/samples` - 获取数据样本
  - [x] `GET /monitor` - 监视页面路由

### 2. Reranker功能 (Reranker Module) ✅
**目标**: 实现搜索结果的重排序功能

#### 子任务：
- [x] 创建 `rag_app/reranker.py` 模块
  - [x] 实现 `RAGReranker` 类
  - [x] 添加多种重排序策略
    - [x] 基于相似度分数重排序
    - [x] 基于内容相关性重排序
    - [x] 基于元数据权重重排序
  - [x] 添加可配置的重排序参数
- [x] 修改 `rag_module.py` 集成reranker功能
- [x] 在 `main.py` 中添加reranker相关的API端点
  - [x] `POST /search/reranked` - 带重排序的搜索
  - [x] `GET /reranker/strategies` - 获取可用重排序策略

### 3. 配置更新 ✅
- [x] 更新 `config.py` 添加新模块的配置
- [x] 更新 `requirements.txt` 添加新依赖

### 4. 文档更新 ✅
- [x] 更新 `README.md` 添加新功能说明
- [x] 更新 `api_documentation.md` 添加新API文档

### 5. 测试 ✅
- [x] 测试监视模块功能 - ✅ 正常工作
- [x] 测试reranker功能 - ✅ 策略API正常工作
- [x] 测试API端点 - ✅ 监视和重排序策略API正常，搜索功能需要Ollama服务运行

## 实现优先级
1. 监视模块基础功能
2. Reranker基础功能
3. API集成
4. 前端界面
5. 文档更新
6. 测试和优化 