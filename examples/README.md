# Examples

使用示例和快速入门指南。

## 快速开始

### 启动服务

```bash
docker compose up -d
```

启动 PostgreSQL、Neo4j、API、Web 和 Worker 服务。

### 通过 API 查询知识图谱

```bash
curl "http://localhost:8000/api/v1/search?q=multi-agent+systems&top_k=5"
```

### 批量导入概念

```bash
curl -X POST "http://localhost:8000/api/v1/batch/concepts" \
  -H "Content-Type: application/json" \
  -d '{
    "concepts": [
      {"name": "LLM", "description": "Large Language Model", "category": "Model"},
      {"name": "RAG", "description": "Retrieval Augmented Generation", "category": "Technique"}
    ]
  }'
```

### Python SDK 使用

```python
import httpx

# 搜索
resp = httpx.get("http://localhost:8000/api/v1/search", params={"q": "agent frameworks", "top_k": 10})
for result in resp.json():
    print(f"{result['name']} (score: {result['score']})")
```

### 可视化面板

访问 `http://localhost:3000` 查看前端界面，支持：

- 知识图谱交互式可视化（`/graph`）
- 语义搜索（`/search`）
- 论文浏览（`/papers`）
- 框架对比（`/compare`）
- 实时监控（`/monitor`）

## 更多资源

- [主 README](../README.md) — 项目总览
- [API 文档](../apps/api/README.md) — API 服务
- [GraphRAG](../packages/graphrag/README.md) — RAG 引擎
- [图谱核心](../packages/graph-core/README.md) — 图数据库层
