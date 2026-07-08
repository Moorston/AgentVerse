# AgentVerse Shared

跨包共享的工具库，提供日志、嵌入、向量存储等通用功能。

## 架构

```
src/agentverse/shared/
├── __init__.py
├── logging.py       # 结构化日志（基于 structlog）
├── embeddings.py    # 嵌入生成接口
├── vectorstore.py   # 向量存储抽象
└── utils.py         # 通用工具函数
```

## 模块

### logging — 结构化日志

```python
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing started", paper_id="1234.56789")
```

基于 `structlog`，输出 JSON 格式的结构化日志，便于生产环境日志聚合。

### embeddings — 嵌入生成

定义统一的嵌入生成接口，支持多种嵌入模型后端。

### vectorstore — 向量存储

基于 `asyncpg` + `pgvector` 的向量存储实现，支持：

- 向量相似度搜索（cosine distance）
- 全文搜索（ILIKE 兜底）
- 元数据过滤
- HNSW 近似最近邻索引

```python
from agentverse.shared.vectorstore import PgVectorStore

store = PgVectorStore(dsn="postgresql://localhost/agentverse")
await store.connect()

# 存储嵌入
await store.upsert(id="doc_1", embedding=[0.1, 0.2, ...], content="Hello world")

# 相似度搜索
results = await store.search(query_embedding=[0.1, 0.2, ...], top_k=10)
```

### utils — 通用工具

项目内共享的辅助函数集合。

## 测试

```bash
pytest packages/shared/tests/ -v
```
