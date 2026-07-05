# AgentVerse 架构设计规范

> **文档性质：** 强制性架构约束文档。所有代码变更必须符合本规范，代码审查以此为依据。
> **关联文档：** `AGENTS.md`（开发规范）、`docs/EXECUTION_PLAN.md`（实施计划）、`docs/ARCHITECTURE.md`（快速概览）

---

## 1. 架构总览

### 1.1 系统定位

AgentVerse 是一个 **AI Agent 生态系统的知识基础设施平台**，核心职责：

```
数据采集 → 结构化提取 → 知识图谱存储 → 智能检索 → API 服务 → 可视化呈现
```

### 1.2 四层架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                      表现层 (Presentation)                          │
│    apps/web (Next.js 15 + React 19 + TypeScript + TailwindCSS)     │
├─────────────────────────────────────────────────────────────────────┤
│                      服务层 (Service)                               │
│    apps/api (FastAPI)          │    apps/worker (Python scheduler)  │
│    REST API v1 + GraphRAG      │    定时任务：爬取/提取/索引          │
├─────────────────────────────────────────────────────────────────────┤
│                      领域层 (Domain)                                │
│    ontology   │   crawler   │   extractor   │   graphrag           │
│    本体定义     │   数据采集    │   LLM 提取     │   检索引擎           │
├─────────────────────────────────────────────────────────────────────┤
│                      基础层 (Foundation)                            │
│    shared (配置/日志/异常/工具)  │  graph-core (Neo4j 驱动/模型/仓库)  │
├─────────────────────────────────────────────────────────────────────┤
│                      基础设施 (Infrastructure)                      │
│    Neo4j 5 (知识图谱)  │  PostgreSQL 17 + pgvector (向量)  │  Docker │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 核心数据流水线

```
[数据源层]                  [处理层]                    [存储层]              [服务层]
──────────                ──────────                  ──────────           ──────────
arXiv API         ─┐                                  ┌→ Neo4j             ┌→ REST API
GitHub API         ├→ crawler → extractor → ontology ─┤  (知识图谱)         ├→ GraphRAG
RSS / Newsletter   │   (采集)     (提取)      (规范化)  │                    │  (检索)
Semantic Scholar   │                                  └→ pgvector           └→ Web UI
Awesome 仓库       ┘                                     (向量索引)
```

---

## 2. 包依赖架构（严格 DAG）

### 2.1 依赖关系图

```
                    agentverse-shared           ← 零内部依赖
                         │
                    agentverse-graph-core       ← 仅依赖 shared
                     ╱           ╲
            agentverse-ontology   agentverse-graphrag
                     │                     │
            agentverse-crawler              │
                     │                     │
            agentverse-extractor            │
                     ╲           ╱         ╱
                      ╲         ╱         ╱
                 ┌──────┴───────┴─────────┘
                 │
            agentverse-api          agentverse-worker
            (依赖所有 packages)      (依赖所有 packages)

            agentverse-web          (独立 Next.js，通过 HTTP 与 api 通信)
```

### 2.2 依赖约束（强制）

| 规则 | 说明 | 违反后果 |
|------|------|---------|
| **禁止循环依赖** | 包 A 不能直接或间接依赖包 B 同时被包 B 依赖 | 构建失败 |
| **禁止跳层依赖** | `extractor` 不得直接导入 `graph-core`，必须通过 `shared` | 违反关注点分离 |
| **禁止反向依赖** | `packages/` 不得导入 `apps/` | 架构崩溃 |
| **shared 是唯一叶子** | `shared` 不得依赖任何其他 `agentverse-*` 包 | 循环依赖 |
| **apps 只出不进** | `apps/` 可以依赖所有 `packages/`，但不可反向 | 层次污染 |

### 2.3 各包职责边界

| 包 | 职责 | 可以做什么 | 不可以做什么 |
|----|------|-----------|-------------|
| **shared** | 配置、日志、异常、工具函数 | 定义 Settings、get_logger、AgentVerseError | 包含任何业务逻辑 |
| **graph-core** | Neo4j 驱动、图模型、仓库 | GraphClient、GraphNode、BaseRepository | 包含具体业务概念（Agent/Paper） |
| **ontology** | AI Agent 领域本体定义 | AgentConcept、FrameworkConcept、normalizer | 直接访问数据库 |
| **crawler** | 数据采集 | ArxivCrawler、GitHubCrawler、RateLimiter | 调用 LLM、访问数据库 |
| **extractor** | LLM 信息提取 | PaperExtractor、ConceptExtractor | 直接访问数据库 |
| **graphrag** | 检索引擎 | VectorSearch、GraphSearch、HybridSearch | 包含爬取或提取逻辑 |
| **api** | REST API 服务 | FastAPI 路由、中间件、依赖注入 | 包含爬取或 LLM 调用逻辑 |
| **worker** | 后台任务调度 | 定时任务、任务链编排 | 直接暴露 HTTP 端点 |

---

## 3. 数据架构

### 3.1 Neo4j 知识图谱 Schema

#### 节点标签（Node Labels）

| 标签 | 唯一约束属性 | 核心属性 | 来源 |
|------|------------|---------|------|
| `Concept` | `name` | description, category | LLM 提取 |
| `Agent` | `name` | description, category | LLM 提取 |
| `Framework` | `name` | stars, latest_version, description | GitHub API |
| `Paper` | `doi` | title, abstract, authors[], published_date | arXiv API |
| `Protocol` | `name` | description, version | 文档解析 |
| `News` | `url` | title, source, published_at, summary | RSS |
| `Product` | `name` | company, launched_at, description | RSS / 爬虫 |
| `Company` | `name` | funding_round, valuation | RSS |
| `MemoryFramework` | `name` | description, github_url | GitHub API |
| `MemoryType` | `name` | description, category | 论文提取 |
| `Application` | `name` | tech_stack, runnable | GitHub |
| `Pattern` | `name` | description, example_implementation | 论文/文档 |
| `IndustryTrend` | `name` | direction, strength, time_window | 报告提取 |

#### 关系类型（Relationship Types）

所有关系类型必须注册在 `packages/graph-core/src/agentverse/graph_core/models/relationship.py` 的 `RelationshipType` 枚举中。

**现有关系：**
```python
PROPOSES     # Paper → Concept        论文提出概念
IMPLEMENTS   # Framework → Concept    框架实现概念
EVOLVES_TO   # Concept → Concept      概念演化链
RELATED_TO   # * → *                  通用关联
DEPENDS_ON   # Framework → Framework  框架依赖
SUPPORTS     # Framework → Concept    框架支持特性
USED_IN      # Concept → Application  概念使用场景
REFERENCES   # Paper → Paper          论文引用
```

**待扩展关系（见 docs/EXECUTION_PLAN.md 第六章）：**
```
CITES, EXTENDS, INSPIRED_BY, AUTHORED_BY, IMPLEMENTED_BY,
ACHIEVES_SOTA, ANNOUNCED_BY, INVESTED_IN, COLLABORATES_WITH,
INTEGRATES_WITH, SUPPORTS_PATTERN, IMPLEMENTS_MEMORY,
BENCHMARKED_ON, FEATURED_IN_WEEK, TRENDING_IN, UPDATED_TO
```

#### 约束与索引

```
约束文件：packages/graph-core/src/agentverse/graph_core/schema/constraints.py
索引文件：packages/graph-core/src/agentverse/graph_core/schema/indexes.py

规则：新增节点标签必须同步更新约束和索引文件
```

### 3.2 PostgreSQL 向量存储 Schema

```sql
-- pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 节点嵌入表
CREATE TABLE node_embeddings (
    id           SERIAL PRIMARY KEY,
    node_id      TEXT NOT NULL,          -- Neo4j element_id
    node_label   TEXT NOT NULL,          -- 节点标签
    content      TEXT NOT NULL,          -- 被嵌入的文本（标题+描述）
    embedding    vector(1536) NOT NULL,  -- OpenAI text-embedding-3-small
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(node_id)
);

-- 向量相似度索引
CREATE INDEX idx_embeddings_cosine
    ON node_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 3.3 数据流约束

```
约束 1：所有写入 Neo4j 的操作必须通过 BaseRepository 子类
约束 2：所有写入 pgvector 的操作必须通过 IndexingPipeline
约束 3：数据流向严格单向：外部源 → crawler → extractor → ontology → graph-core/graphrag → api
约束 4：禁止反向数据流：api 不得直接调用 crawler 或 extractor
约束 5：Neo4j 和 pgvector 之间通过 node_id 关联，不得直接 JOIN
```

---

## 4. API 架构

### 4.1 REST API 设计规范

```
基础路径：/api/v1
版本策略：URL 路径版本（/api/v1, /api/v2）
响应格式：application/json
认证方式：Phase 1 无认证，Phase 2 起使用 API Key
```

### 4.2 端点规范

| 方法 | 路径 | 说明 | 请求模型 | 响应模型 |
|------|------|------|---------|---------|
| `GET` | `/health` | 健康检查 | — | `HealthResponse` |
| `GET` | `/api/v1/concepts` | 概念列表 | `?page=&size=&category=` | `list[ConceptResponse]` |
| `GET` | `/api/v1/concepts/{name}` | 概念详情 | — | `ConceptDetailResponse` |
| `GET` | `/api/v1/concepts/{name}/neighbors` | 邻居子图 | `?depth=` | `GraphData` |
| `GET` | `/api/v1/concepts/{name}/timeline` | 演化时间线 | `?direction=` | `TimelineResponse` |
| `POST` | `/api/v1/concepts` | 创建概念 | `ConceptCreate` | `ConceptResponse` |
| `DELETE` | `/api/v1/concepts/{name}` | 删除概念 | — | `204` |
| `GET` | `/api/v1/frameworks` | 框架列表 | `?page=&size=` | `list[FrameworkResponse]` |
| `GET` | `/api/v1/search` | GraphRAG 检索 | `?q=&top_k=` | `SearchResponse` |
| `GET` | `/api/v1/papers` | 论文列表 | `?page=&size=&category=` | `list[PaperResponse]` |

### 4.3 API 约束

| 约束 | 说明 |
|------|------|
| **所有端点返回 Pydantic 模型** | 禁止直接返回 `dict` |
| **请求体使用 Pydantic BaseModel** | 禁止直接接收 `dict` |
| **错误响应统一格式** | `{"error": "...", "detail": "...", "status_code": 4xx}` |
| **分页参数统一** | `?page=1&size=20`，默认 size=20，最大 size=100 |
| **异步端点** | 所有路由函数必须是 `async def` |
| **依赖注入** | 数据库连接通过 `Depends()` 注入，禁止在端点中直接创建 |
| **中间件顺序** | CORS → Logging → Error Handler（在 `setup_middleware()` 中配置） |

### 4.4 错误处理层次

```python
# apps/api/src/agentverse/api/core/middleware.py

全局异常处理器：
  AgentVerseError     → 400 Bad Request
  NotFoundError       → 404 Not Found
  ValidationError     → 422 Unprocessable Entity
  DatabaseError       → 503 Service Unavailable
  Exception           → 500 Internal Server Error（记录完整 traceback）
```

---

## 5. 领域层架构

### 5.1 Crawler 架构

```
packages/crawler/src/agentverse/crawler/
├── base.py              ← BaseCrawler ABC + CrawlResult dataclass
├── rate_limiter.py      ← RateLimiter（requests_per_second 可配置）
├── pipeline.py          ← CrawlPipeline（register + run_all）
└── sources/
    ├── arxiv.py         ← ArxivCrawler（REST API，3 req/s）
    ├── github.py        ← GitHubCrawler（REST API，5000 req/h）
    ├── web.py           ← WebCrawler（httpx + BeautifulSoup）
    ├── semantic_scholar.py  ← [新增] SemanticScholarCrawler
    ├── papers_with_code.py  ← [新增] PapersWithCodeCrawler
    ├── rss.py           ← [新增] RSSCrawler
    └── awesome_parser.py    ← [新增] AwesomeMarkdownParser
```

**设计约束：**
```
1. 所有爬虫继承 BaseCrawler，实现 async def crawl(**kwargs) -> CrawlResult
2. CrawlResult.source 标识数据源，CrawlResult.items 为 list[dict]
3. 所有 HTTP 请求使用 httpx.AsyncClient，禁止 requests
4. 所有爬虫必须通过 RateLimiter 限速
5. 爬虫禁止直接写入数据库，只返回 CrawlResult
6. 增量爬取：通过 since 参数或上次爬取时间戳过滤
```

### 5.2 Extractor 架构

```
packages/extractor/src/agentverse/extractor/
├── base.py              ← BaseExtractor ABC + ExtractionResult dataclass
├── llm/
│   ├── client.py        ← LLMClient（OpenAI / Anthropic 双通道）
│   └── prompts.py       ← 提取 prompt 模板（3 套：paper/concept/relationship）
├── extractors/
│   ├── paper.py         ← PaperExtractor
│   ├── concept.py       ← ConceptExtractor
│   └── relationship.py  ← RelationshipExtractor
└── pipeline.py          ← ExtractionPipeline
```

**设计约束：**
```
1. 所有提取器继承 BaseExtractor，实现 async def extract(text, **kwargs) -> ExtractionResult
2. LLM 调用必须通过 LLMClient，禁止直接构造 OpenAI/Anthropic 客户端
3. 提取结果必须为 JSON Schema 格式，通过 response_format 约束
4. 概念名称必须标准化：去除前后空格、统一大小写、合并同义词
5. 关系类型必须限定在 RelationshipType 枚举范围内
6. 提取器禁止直接写入数据库，只返回 ExtractionResult
7. 单篇处理超时：10s（GPT-4o），30s（Claude Sonnet 4）
```

### 5.3 Ontology 架构

```
packages/ontology/src/agentverse/ontology/
├── concepts/
│   ├── base.py          ← Concept(GraphNode) 基类
│   ├── agent.py         ← AgentConcept
│   ├── framework.py     ← FrameworkConcept
│   ├── paper.py         ← PaperConcept
│   ├── protocol.py      ← ProtocolConcept
│   ├── news.py          ← [新增] NewsConcept
│   ├── product.py       ← [新增] ProductConcept
│   ├── company.py       ← [新增] CompanyConcept
│   ├── memory_type.py   ← [新增] MemoryTypeConcept
│   ├── memory_framework.py ← [新增] MemoryFrameworkConcept
│   ├── application.py   ← [新增] ApplicationConcept
│   ├── pattern.py       ← [新增] PatternConcept
│   └── industry_trend.py    ← [新增] IndustryTrendConcept
├── schema/
│   └── definitions.py   ← 标签→属性映射定义
└── normalizer.py        ← normalize_*() 函数
```

**设计约束：**
```
1. 所有概念类继承 Concept(GraphNode)，__post_init__ 设置 labels 和 properties
2. labels 必须包含 "Concept" 父标签 + 具体类型标签
3. properties 字典的 key 必须使用 snake_case
4. normalizer 函数接收 raw dict，返回标准化概念实例
5. normalizer 不得访问数据库，纯数据转换
6. 新增概念类必须同步更新 schema/definitions.py 的 TAG_LABELS 和 PROPERTY_DEFINITIONS
```

### 5.4 GraphRAG 架构

```
packages/graphrag/src/agentverse/graphrag/
├── engine.py            ← GraphRAGEngine（顶层入口）
├── embeddings/
│   ├── base.py          ← BaseEmbeddingModel ABC
│   └── models.py        ← OpenAIEmbeddingModel
├── retrieval/
│   ├── vector.py        ← VectorSearch（pgvector 余弦相似度）
│   ├── graph.py         ← GraphSearch（Neo4j 多跳遍历）
│   └── hybrid.py        ← HybridSearch（融合排序）
└── indexing/
    └── pipeline.py      ← IndexingPipeline（写入 pgvector）
```

**设计约束：**
```
1. 嵌入模型通过 BaseEmbeddingModel 抽象，禁止直接调用 OpenAI API
2. 向量维度必须与 Settings.embedding_dimension 一致（默认 1536）
3. HybridSearch 必须同时查询 Neo4j 和 pgvector，融合后排序
4. IndexingPipeline 负责将节点属性嵌入并写入 pgvector
5. Neo4j 和 pgvector 通过 node_id 字段关联
6. 检索结果去重：同一节点在 vector 和 graph 结果中只保留一次
```

---

## 6. 服务层架构

### 6.1 FastAPI 应用架构

```
apps/api/src/agentverse/api/
├── main.py              ← create_app() 工厂函数
├── core/
│   ├── config.py        ← APISettings(Settings) 扩展配置
│   ├── dependencies.py  ← FastAPI Depends() 依赖注入
│   ├── events.py        ← lifespan 上下文管理器
│   └── middleware.py    ← CORS / Logging / Error Handler
├── api/v1/
│   ├── router.py        ← api_v1_router 聚合器
│   ├── health.py        ← GET /health
│   ├── concepts.py      ← /concepts CRUD
│   ├── search.py        ← /search GraphRAG
│   └── frameworks.py    ← [新增] /frameworks
├── db/
│   ├── neo4j.py         ← Neo4j 连接池管理
│   └── postgres.py      ← PostgreSQL 连接池管理
└── models/
    ├── request.py       ← Pydantic 请求模型
    └── response.py      ← Pydantic 响应模型
```

**应用工厂模式约束：**
```python
def create_app() -> FastAPI:
    app = FastAPI(title="AgentVerse API", version="0.1.0", lifespan=lifespan)
    setup_middleware(app)
    app.include_router(api_v1_router, prefix="/api/v1")
    return app

# 全局实例（uvicorn 入口）
app = create_app()

# 测试中必须使用 create_app()，禁止直接使用全局 app
```

### 6.2 Worker 架构

```
apps/worker/src/agentverse/worker/
├── main.py              ← asyncio.run(main()) 入口
├── config.py            ← WorkerSettings(Settings)
├── scheduler.py         ← Scheduler（interval-based）
└── tasks/
    ├── crawl.py         ← run_crawl(source)
    ├── extract.py       ← run_extract(source)
    └── index.py         ← run_index(documents)
```

**任务链约束：**
```
crawl 完成 → 自动触发 extract → 自动触发 index
单次失败重试 3 次（指数退避），3 次后标记失败并记录日志
任务间通过 asyncio.Queue 传递数据
```

---

## 7. 前端架构

### 7.1 Next.js 应用结构

```
apps/web/src/
├── app/
│   ├── layout.tsx       ← 根布局（HTML + 全局样式）
│   ├── page.tsx         ← 首页（项目介绍 + 导航）
│   ├── globals.css      ← TailwindCSS 全局样式
│   └── graph/
│       └── page.tsx     ← 图谱探索页
├── components/
│   ├── ui/              ← 通用 UI 组件（Button, Card, Input）
│   ├── graph/           ← 图谱专用组件（GraphCanvas, GraphControls）
│   └── layout/          ← 布局组件（Header, Sidebar, Footer）
├── lib/
│   ├── api.ts           ← apiFetch<T>() 统一 API 客户端
│   └── utils.ts         ← 工具函数（cn() 等）
└── types/
    ├── graph.ts         ← GraphNode, GraphEdge, GraphData
    └── api.ts           ← HealthResponse, ConceptResponse, SearchResponse
```

**前端约束：**
```
1. 所有 API 调用通过 lib/api.ts 的 apiFetch<T>()，禁止直接 fetch
2. 所有组件使用 React 函数组件 + hooks，禁止类组件
3. 样式使用 TailwindCSS 工具类，禁止内联 style
4. API 响应类型定义在 types/，禁止使用 any
5. 状态管理使用本地 useState/useReducer，暂不引入外部状态库
6. 图谱渲染使用 Cytoscape.js，禁止自定义 canvas 绘制
7. Next.js 通过 rewrites() 将 /api/* 代理到后端，前端不直接访问数据库
```

### 7.2 前端路由规划

| 路径 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 项目介绍、数据统计、快速导航 |
| `/graph` | 图谱探索 | 交互式知识图谱浏览 |
| `/graph/{name}` | 概念详情 | 单个概念的详情页 + 关系图 |
| `/search` | 搜索 | GraphRAG 搜索结果页 |
| `/frameworks` | 框架生态 | 框架列表 + 能力映射 |
| `/timeline` | 演化时间线 | 概念演化路径可视化 |

---

## 8. 部署架构

### 8.1 Docker Compose 服务拓扑

```
┌──────────────────────────────────────────────────────┐
│                  Docker Compose                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   neo4j:5    │  │ pgvector:pg17│  │   api:8000 │ │
│  │  :7474 HTTP  │  │  :5432       │  │  FastAPI   │ │
│  │  :7687 Bolt  │  │  PostgreSQL  │  │  uvicorn   │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                │         │
│         └────────┬────────┘                │         │
│                  │                         │         │
│           ┌──────┴───────┐         ┌──────┴──────┐  │
│           │  worker:     │         │   web:3000  │  │
│           │  调度器       │         │   Next.js   │  │
│           └──────────────┘         └─────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 8.2 服务依赖关系

```
neo4j        ← 无依赖（最先启动）
postgres     ← 无依赖（最先启动）
api          ← depends_on: neo4j(healthy), postgres(healthy)
worker       ← depends_on: neo4j(healthy), postgres(healthy)
web          ← depends_on: api
```

### 8.3 端口分配

| 服务 | 端口 | 协议 |
|------|------|------|
| Neo4j HTTP | 7474 | HTTP |
| Neo4j Bolt | 7687 | Bolt |
| PostgreSQL | 5432 | PostgreSQL |
| API | 8000 | HTTP |
| Web | 3000 | HTTP |

### 8.4 环境变量管理

```
统一来源：.env 文件（开发）/ 环境变量注入（生产）
继承机制：所有服务共享 x-shared-environment 锚点
敏感信息：通过 ${VAR:-default} 语法提供开发默认值，生产环境覆盖
禁止行为：Docker Compose 中不得硬编码密码
```

---

## 9. 横切关注点

### 9.1 配置管理

```
继承链：shared.Settings → api.APISettings / worker.WorkerSettings

加载优先级：环境变量 > .env 文件 > 默认值

配置类必须：
  - 继承 pydantic_settings.BaseSettings
  - 使用 SettingsConfigDict(env_file=".env", extra="ignore")
  - 提供合理的默认值（开发环境可直接运行）
  - 敏感字段默认为空字符串（api_key 等）
```

### 9.2 日志规范

```python
# 获取 logger
from agentverse.shared.logging import get_logger
logger = get_logger(__name__)

# 约束：
# 1. 所有模块使用 structlog，禁止 print()
# 2. 日志级别通过 Settings.log_level 配置
# 3. 生产环境使用 JSON 格式，开发环境使用 ConsoleRenderer
# 4. 敏感信息（API key、密码）不得出现在日志中
```

### 9.3 异常处理

```
异常层次（packages/shared/.../exceptions.py）：
  AgentVerseError          ← 基类
  ├── ConfigurationError   ← 配置缺失/无效
  ├── DatabaseError        ← 数据库连接/查询失败
  └── NotFoundError        ← 资源未找到

约束：
  1. 所有业务异常继承 AgentVerseError
  2. 不得捕获裸 Exception 后静默处理
  3. API 层全局异常处理器将异常转为标准 JSON 错误响应
  4. Worker 层任务异常记录日志后继续运行，不中断调度器
```

### 9.4 异步编程规范

```
约束：
  1. 所有 I/O 函数必须是 async def
  2. 禁止在 async 函数中调用阻塞 I/O（requests、time.sleep、open）
  3. 替代方案：httpx、asyncio.sleep、aiofiles
  4. 并发控制：使用 asyncio.Semaphore 限制并发数
  5. 超时控制：所有外部调用必须设置 timeout
  6. 重试逻辑：使用 shared/utils/retry.py 的 @retry 装饰器
```

---

## 10. 架构反模式（禁止）

| 反模式 | 描述 | 正确做法 |
|--------|------|---------|
| **上帝类** | 单个类承担多个职责 | 职责单一，一包一职责 |
| **循环依赖** | A 依赖 B 同时 B 依赖 A | 提取公共部分到 shared |
| **跳层依赖** | extractor 直接导入 graph-core | 通过 shared 传递 |
| **硬编码配置** | 代码中直接写数据库地址 | 通过 Settings 注入 |
| **裸字典传递** | 函数间直接传 dict | 使用 dataclass 或 Pydantic |
| **同步阻塞** | async 中调用 requests | 使用 httpx.AsyncClient |
| **日志打印** | 使用 print() 输出 | 使用 get_logger() |
| **数据库直连** | 在端点中创建连接 | 通过 Depends() 注入 |
| **Cypher 内联** | 业务逻辑中写 Cypher 字符串 | 通过 BaseRepository |
| **前端 any** | TypeScript 中使用 any | 定义具体类型 |

---

## 11. 扩展点设计

### 11.1 可扩展组件

| 组件 | 扩展方式 | 注册机制 |
|------|---------|---------|
| **新爬虫** | 继承 BaseCrawler | CrawlPipeline.register() |
| **新提取器** | 继承 BaseExtractor | ExtractionPipeline.register() |
| **新概念类型** | 继承 Concept | 更新 schema/definitions.py |
| **新关系类型** | 添加到 RelationshipType 枚举 | 更新 constraints.py |
| **新 API 端点** | 创建路由文件 | router.py include_router() |
| **新检索策略** | 继承检索基类 | HybridSearch 组合 |
| **新嵌入模型** | 继承 BaseEmbeddingModel | Settings.embedding_model 切换 |
| **新前端页面** | 创建 app/ 子目录 | Next.js 文件系统路由 |

### 11.2 插件化方向（Phase 3+）

```
未来可考虑的插件化：
  - crawler/sources/ 作为插件目录，运行时发现
  - 检索策略通过配置切换（vector-only / graph-only / hybrid）
  - LLM Provider 通过配置切换（openai / anthropic / local）
```

---

## 12. 性能约束

| 指标 | 目标 | 说明 |
|------|------|------|
| API 响应延迟 | < 200ms（非搜索端点） | P95 延迟 |
| GraphRAG 搜索延迟 | < 2s | 100 跳以内 |
| 爬取吞吐量 | 100 论文/分钟 | arXiv API 限速 |
| LLM 提取延迟 | < 10s/篇 | GPT-4o |
| 并发 API 请求 | 100+ | uvicorn workers |
| Neo4j 查询延迟 | < 50ms | 索引命中 |
| pgvector 查询延迟 | < 100ms | 100k 节点以内 |

---

## 13. 安全约束

| 维度 | 约束 |
|------|------|
| **API 认证** | Phase 1 开放，Phase 2 起 API Key |
| **CORS** | 开发环境 `allow_origins=["*"]`，生产环境限定域名 |
| **密码管理** | 环境变量注入，禁止硬编码或提交到 Git |
| **SQL/Cypher 注入** | 使用参数化查询，禁止字符串拼接 |
| **依赖安全** | 定期 `uv audit`，锁定版本（uv.lock） |
| **日志脱敏** | API Key、密码不得出现在日志 |

---

## 14. 架构决策记录（ADR）

| 编号 | 决策 | 原因 | 状态 |
|------|------|------|------|
| ADR-001 | 选择 uv workspace 而非 poetry monorepo | uv 速度快 10x，原生 workspace 支持 | 已采纳 |
| ADR-002 | 选择 Hatchling 而非 setuptools | 轻量、标准、与 uv 原生兼容 | 已采纳 |
| ADR-003 | 异步优先（async/await 全链路） | FastAPI 异步优势、高并发爬取 | 已采纳 |
| ADR-004 | Neo4j + pgvector 双存储 | 图遍历 + 向量检索互补，GraphRAG 核心 | 已采纳 |
| ADR-005 | 命名空间包（agentverse.*） | 避免包名冲突，统一导入路径 | 已采纳 |
| ADR-006 | src/ 布局而非扁平布局 | 避免导入混乱，强制显式安装 | 已采纳 |
| ADR-007 | 应用工厂模式（create_app） | 测试友好，多实例支持 | 已采纳 |
| ADR-008 | Cytoscape.js 而非 D3.js | 图谱渲染性能更优，API 更简单 | 已采纳 |
