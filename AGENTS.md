# AGENTS.md — AgentVerse 开发规范

## 项目概述

AgentVerse 是 AI Agent 生态系统的开源知识图谱基础设施，整合了知识图谱、GraphRAG、Agent 本体论、论文情报、框架关系映射、MCP/A2A 协议映射和演化时间线分析。

## 架构约束

### 包依赖 DAG（严格单向）

```
shared
  → graph-core
    → ontology
    → graphrag
      → crawler → extractor
        → api
        → worker
```

**禁止**：反向依赖、循环依赖、跨层依赖。

### 命名空间

所有 Python 包使用 `agentverse.*` 命名空间，采用 `src/` layout：

```
packages/graph-core/src/agentverse/graph_core/
packages/ontology/src/agentverse/ontology/
```

### 构建系统

- **Python**: uv + hatchling
- **前端**: npm + Next.js
- **容器**: docker compose

## 代码风格

### Python

- **格式化**: ruff（line-length=100, target=py312）
- **类型检查**: mypy strict 模式
- **异步优先**: 所有 I/O 操作使用 `async/await`
- **日志**: structlog 结构化日志，禁止 `print()`
- **配置**: pydantic-settings，通过环境变量注入

### TypeScript/React

- **格式化**: ESLint + Prettier
- **组件**: 函数组件 + Hooks
- **状态管理**: React Query（API 缓存）
- **样式**: Tailwind CSS

## 设计模式

| 模式 | 使用场景 | 示例 |
|------|---------|------|
| 仓库模式 | Neo4j 数据访问 | `BaseRepository` |
| 管道模式 | 爬取/提取/索引 | `CrawlPipeline`, `ExtractionPipeline` |
| 应用工厂 | FastAPI 应用创建 | `create_app()` |
| 依赖注入 | API 端点 | `Depends(get_graph_client)` |
| 数据类 | 领域模型 | `GraphNode`, `GraphRelationship`, `Concept` |

## 命名规范

- **Python 文件**: snake_case
- **Python 类**: PascalCase
- **Neo4j 标签**: PascalCase（`Agent`, `Framework`, `Paper`）
- **Neo4j 关系**: UPPER_SNAKE_CASE（`PROPOSES`, `EVOLVES_TO`）
- **Neo4j 属性**: snake_case（`name`, `published_date`）
- **API 路径**: kebab-case（`/api/v1/concepts`）
- **环境变量**: UPPER_SNAKE_CASE

## 测试规范

- **单元测试**: mock 外部依赖（Neo4j, HTTP 调用）
- **集成测试**: 真实数据库（docker compose）
- **测试命名**: `test_<功能>_<场景>`
- **覆盖率目标**: 核心包 80%+

## Git 提交规范

```
<type>(<scope>): <description>

type: feat | fix | docs | style | refactor | test | chore
scope: shared | graph-core | ontology | crawler | extractor | graphrag | api | worker | web
```

## 数据库约定

- **Neo4j**: 所有约束通过 `schema/constraints.py` 统一管理
- **PostgreSQL/pgvector**: 向量维度默认 1536（OpenAI text-embedding-3-small）
- **连接管理**: 通过 FastAPI lifespan 初始化/关闭

## 关键文件索引

| 文件 | 作用 |
|------|------|
| `pyproject.toml` | uv workspace 定义、dev tooling 配置 |
| `AGENTS.md` | 本文件 |
| `docs/ARCHITECTURE_DESIGN.md` | 详细架构设计文档 |
| `docs/EXECUTION_PLAN.md` | 业务实施与数据源规划 |
| `docs/BUSINESS_MODULES.md` | 业务模块清单 |
| `docs/API_REFERENCE.md` | API 参考文档 |
| `docs/DEPLOYMENT.md` | 部署指南 |
