# AgentVerse API

FastAPI 后端服务，提供 AgentVerse 知识图谱的 RESTful API 接口。

## 架构

```
src/agentverse/api/
├── main.py              # FastAPI 应用入口，生命周期管理
├── api/v1/
│   ├── agents.py        # Agent CRUD 端点
│   ├── batch.py         # 批量操作端点（概念/关系批量创建与删除）
│   ├── search.py        # 向量搜索与全文搜索端点
│   ├── ontology.py      # 本体管理端点
│   ├── paper.py         # 论文管理端点
│   └── ws.py            # WebSocket 实时通信端点
├── core/
│   ├── config.py        # 应用配置（Pydantic Settings）
│   ├── dependencies.py  # FastAPI 依赖注入
│   ├── events.py        # 生命周期事件处理器
│   └── middleware.py     # 中间件（CORS、速率限制、请求日志）
└── tests/               # pytest 测试套件
```

## 核心功能

- **Agent 管理** — 创建、查询、更新、删除 AI Agent
- **图谱搜索** — 基于 pgvector 的语义向量搜索与全文搜索
- **批量操作** — 批量创建/删除概念和关系
- **本体管理** — 本体 Schema 的 CRUD
- **WebSocket** — 实时推送图谱更新事件
- **速率限制** — 基于滑动窗口的内存限流（60 rpm / 1000 rph）
- **健康检查** — `/health` 端点，检测 PostgreSQL 和 Neo4j 连接状态

## 开发

```bash
# 安装依赖
pip install -e '.[api,dev]'

# 启动开发服务器
uvicorn agentverse.api.main:app --reload --port 8000

# 运行测试
pytest apps/api/tests/ -v
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL DSN | `postgresql://localhost:5432/agentverse` |
| `NEO4J_URI` | Neo4j 连接地址 | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | — |
| `API_HOST` | 监听地址 | `0.0.0.0` |
| `API_PORT` | 监听端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
