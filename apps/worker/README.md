# AgentVerse Worker

基于 TaskIQ 的异步任务 Worker，处理后台计算密集型任务。

## 架构

```
src/agentverse/worker/
├── main.py          # TaskIQ app 入口与任务注册
├── tasks/
│   ├── __init__.py
│   └── ...          # 具体任务定义
└── config.py        # Worker 配置
```

## 功能

- **论文处理** — 爬取、提取、向量化论文数据
- **图谱更新** — 异步执行图谱的批量写入操作
- **嵌入生成** — 调用 LLM 服务生成文本嵌入向量
- **重试机制** — 内置指数退避重试策略

## 开发

```bash
# 启动 Worker（需要 Redis 作为 Broker）
taskiq worker agentverse.worker.main:broker

# 运行测试
pytest apps/worker/tests/ -v
```

## 依赖

- **Redis** — 作为 TaskIQ 的消息代理
- **PostgreSQL + pgvector** — 嵌入向量存储
- **Neo4j** — 图数据库操作
