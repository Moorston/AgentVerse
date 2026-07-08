# AgentVerse GraphRAG

基于图数据库的检索增强生成（RAG）引擎，结合向量搜索和图遍历实现混合检索。

## 架构

```
src/agentverse/graphrag/
├── __init__.py
├── engine.py        # RAG 引擎核心
├── pipeline.py      # 搜索管线（查询路由 → 检索 → 重排序）
├── query_router.py  # 查询意图识别与路由
└── retrievers/
    ├── vector.py    # pgvector 向量检索
    └── graph.py     # Neo4j 图遍历检索
```

## 搜索流程

```
用户查询
  ↓
QueryRouter（意图识别）
  ↓
┌─────────────┬──────────────┐
│ 向量检索     │ 图遍历检索    │
│ (pgvector)  │ (Neo4j)      │
└──────┬──────┴───────┬──────┘
       ↓              ↓
    结果合并 → 重排序 → 返回 Top-K
```

## 核心功能

- **查询路由** — 自动识别查询意图，路由到合适的检索策略
- **向量检索** — 基于 pgvector 的语义相似度搜索
- **图遍历检索** — 基于 Neo4j 的关系遍历和子图检索
- **混合检索** — 结合两种检索结果的加权融合策略
- **结果重排序** — 按相关性对融合结果重新排序

## 使用

```python
from agentverse.graphrag.engine import GraphRAGEngine

engine = GraphRAGEngine(vector_store=pg_store, graph_repo=neo4j_repo)
results = await engine.search("What are the latest advances in multi-agent systems?", top_k=10)

for result in results:
    print(f"{result.content} (score: {result.score:.3f})")
```

## 测试

```bash
pytest packages/graphrag/tests/ -v
```
