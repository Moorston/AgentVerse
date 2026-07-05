# AgentVerse 业务模块清单（更新版）

> **更新日期：** 2026-07-05
> **前置文档：** `AGENTS.md`（开发规范）、`docs/ARCHITECTURE_DESIGN.md`（架构约束）、`docs/EXECUTION_PLAN.md`（数据源规划）
> **工具链：** Trellis（工程框架）+ OpenSpec（规格驱动）+ Skills（/grill-me 等）

---

## 一、当前状态诊断

### 1.1 代码库统计

| 指标 | 数值 |
|------|------|
| 有实际逻辑的文件 | 55 个 |
| 待实现文件（含 TODO/pass） | 23 个 |
| 已安装 workspace 包 | 8 个 |
| 外部依赖包 | 77 个 |
| Neo4j 节点标签 | 5 种（待扩展到 13 种） |
| Neo4j 关系类型 | 8 种（待扩展到 24 种） |
| 本体概念类 | 5 种（待扩展到 13 种） |
| 已安装开发工具 | Trellis 0.6.5 + OpenSpec 1.5.0 + Skills 1.5.14 |

### 1.2 待实现文件清单

```
packages/crawler/sources/       ← arxiv.py, github.py, web.py（爬虫实现）
packages/extractor/             ← llm/client.py, extractors/paper/concept/relationship.py
packages/graphrag/              ← embeddings/models.py, retrieval/vector/graph/hybrid.py, engine.py, indexing/pipeline.py
apps/api/                       ← db/neo4j.py, db/postgres.py, core/dependencies.py, api/v1/concepts.py, api/v1/search.py
apps/worker/                    ← main.py, tasks/crawl/extract/index.py
```

---

## 二、更新后的总体路线图

```
Phase 0（工具链与规范）      Phase 1（数据管道）         Phase 2（检索与服务）        Phase 3（前端与自动化）      Phase 4（高阶智能）
───────────────────────  ─────────────────────────  ─────────────────────────  ─────────────────────────  ─────────────────────
[0a] Trellis specs 配置   [1] Neo4j Schema 初始化    [5] GraphRAG 混合检索       [9]  Web 前端图谱可视化    [13] AI Agent 搜索引擎
[0b] OpenSpec 变更模板     [2] ArXiv 论文爬取         [6] 概念关系浏览器 API      [10] 多源自动知识流水线    [14] Agent 推荐系统
[0c] grill-me 需求澄清     [3] LLM 概念提取引擎      [7] 框架生态映射            [11] 行业资讯 RSS 管道     [15] Research Copilot
                           [4] 本体论规范化入库       [8] 记忆框架数据采集        [12] Agent 演化时间线
```

---

## 三、Phase 0 — 工具链与规范（1 天）

### 模块 0a：Trellis specs 配置

**目标：** 为每个 workspace 包配置 Trellis specs，确保 AI 编码助手自动注入项目上下文。

**操作：**
```bash
trellis init -u freebytes    # 已完成
```

**待完成：**
```
.trellis/spec/agentverse-crawler/     ← 编写爬虫规范（数据源、限速、增量策略）
.trellis/spec/agentverse-extractor/   ← 编写提取规范（prompt 模板、输出格式、重试策略）
.trellis/spec/agentverse-graphrag/    ← 编写检索规范（向量维度、混合策略、评分公式）
.trellis/spec/agentverse-api/         ← 编写 API 规范（端点设计、错误格式、分页约定）
```

**验收标准：**
- [ ] 每个 spec 包含：目标、约束、示例代码、禁止事项
- [ ] Trellis 自动注入 spec 到对应包的代码生成上下文

**工作量：** 0.5 天

---

### 模块 0b：OpenSpec 变更模板

**目标：** 配置 OpenSpec 变更流程模板，确保新功能从提案→设计→实现→归档全程可控。

**操作：**
```bash
openspec init    # 已完成
```

**待完成：**
```
openspec/specs/crawler-spec.md         ← 爬虫系统规格
openspec/specs/extractor-spec.md       ← 提取系统规格
openspec/specs/graphrag-spec.md        ← 检索系统规格
openspec/specs/api-spec.md             ← API 规格
openspec/specs/ontology-spec.md        ← 本体论规格
```

**验收标准：**
- [ ] 每个 spec 包含：功能描述、输入输出、约束、测试用例
- [ ] 支持 `/opsx:propose` 创建新功能变更

**工作量：** 0.5 天

---

### 模块 0c：grill-me 需求澄清

**目标：** 使用 Matt Pocock 的 `/grill-me` 技能对核心模块进行需求澄清。

**操作：**
```bash
npx skills@latest add mattpocock/skills    # 需交互式安装
# 在 Claude Code 中运行：/grill-me
```

**澄清范围：**
```
1. 爬虫系统：数据源优先级、增量策略、错误恢复机制
2. 提取系统：prompt 工程、输出格式、质量评估指标
3. 检索系统：混合策略权重、结果排序算法、缓存策略
4. API 设计：认证方式、速率限制、版本迁移策略
```

**验收标准：**
- [ ] 每个澄清会话产出明确的需求文档
- [ ] 需求文档存入 `openspec/specs/` 对应文件

**工作量：** 0.5 天（每个模块 15 分钟）

---

## 四、Phase 1 — 数据管道（5 天）

### 模块 1：Neo4j Schema 初始化

**目标：** 建立数据库约束和索引，确保数据一致性。

**数据源：** 无（纯 schema 操作）

**涉及文件：**
```
packages/graph-core/src/agentverse/graph_core/client.py           ← GraphClient.connect()/close()
packages/graph-core/src/agentverse/graph_core/schema/constraints.py ← 5 条约束（待扩展到 13 条）
packages/graph-core/src/agentverse/graph_core/schema/indexes.py     ← 4 条索引（待扩展到 13 条）
```

**实施步骤：**
1. 实现 `GraphClient.connect()` — 连接本地 Neo4j（bolt://localhost:7687）
2. 实现 `GraphClient.close()` — 关闭连接
3. 扩展约束：新增 `MemoryFramework`, `Application`, `Product`, `Company`, `News`, `IndustryTrend`, `Pattern` 约束
4. 扩展索引：为所有新标签创建查询索引
5. 实现 schema 初始化脚本（可作为 Docker 启动 job）

**验收标准：**
- [ ] `GraphClient` 能连接 Neo4j 并执行 `RETURN 1`
- [ ] 重复插入同名节点触发唯一约束错误
- [ ] 所有 13 种标签的约束和索引创建成功

**工作量：** 0.5 天
**依赖：** 无

---

### 模块 2：ArXiv 论文爬取

**目标：** 通过 arXiv API 自动获取 AI Agent 相关论文，建立论文数据池。

**数据源：** arXiv REST API（`http://export.arxiv.org/api/query`，无访问限制）

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/arxiv.py     ← ArxivCrawler.crawl()
packages/crawler/src/agentverse/crawler/base.py              ← CrawlResult（已定义）
packages/crawler/src/agentverse/crawler/rate_limiter.py      ← RateLimiter（已实现，设 3 req/s）
```

**实施步骤：**
1. 实现 `ArxivCrawler.crawl()` — 调用 arXiv API
2. 查询参数：`cat:cs.AI OR cat:cs.LG OR cat:cs.CL`，按时间排序
3. 解析 XML 响应，提取：title, authors[], abstract, doi, categories[], published_date
4. 封装为 `CrawlResult` 返回
5. 实现增量爬取：记录上次爬取时间，仅获取新论文

**验收标准：**
- [ ] 单次调用返回结构化论文数据
- [ ] 限速生效（3 req/s），不触发 429
- [ ] 增量爬取正确跳过已有论文

**工作量：** 1 天
**依赖：** 模块 1

---

### 模块 3：LLM 概念提取引擎

**目标：** 从论文摘要中通过 LLM 提取核心概念、概念间关系。

**数据源：** 模块 2 输出 + OpenAI GPT-4o / Claude Sonnet 4

**涉及文件：**
```
packages/extractor/src/agentverse/extractor/llm/client.py          ← LLMClient.complete()
packages/extractor/src/agentverse/extractor/llm/prompts.py          ← prompt 模板（已定义 3 套）
packages/extractor/src/agentverse/extractor/extractors/paper.py     ← PaperExtractor
packages/extractor/src/agentverse/extractor/extractors/concept.py   ← ConceptExtractor
packages/extractor/src/agentverse/extractor/extractors/relationship.py ← RelationshipExtractor
```

**实施步骤：**
1. 实现 `LLMClient.complete()` — 封装 OpenAI / Anthropic API
2. 实现 `PaperExtractor.extract()` — 使用 `PAPER_EXTRACTION_PROMPT`
3. 实现 `ConceptExtractor.extract()` — 使用 `CONCEPT_EXTRACTION_PROMPT`
4. 实现 `RelationshipExtractor.extract()` — 使用 `RELATIONSHIP_EXTRACTION_PROMPT`
5. LLM 输出格式：JSON Schema 约束，确保结构化输出
6. 实现重试逻辑（`shared/utils/retry.py` 已实现）

**验收标准：**
- [ ] 输入论文摘要，输出包含 concepts[] 和 relationships[]
- [ ] 概念名称标准化（去空格、统一大小写）
- [ ] 关系类型限定在 RelationshipType 枚举范围
- [ ] 单篇处理延迟 < 10s（GPT-4o）

**工作量：** 2 天
**依赖：** 模块 2

---

### 模块 4：本体论规范化入库

**目标：** 将爬取和提取的数据标准化为本体实例，写入 Neo4j。

**数据源：** 模块 2 + 模块 3 的输出

**涉及文件：**
```
packages/ontology/src/agentverse/ontology/normalizer.py              ← normalize_*() 函数
packages/ontology/src/agentverse/ontology/concepts/                  ← 各概念类
packages/graph-core/src/agentverse/graph_core/repository/base.py     ← BaseRepository
```

**新增概念类：**
```
packages/ontology/src/agentverse/ontology/concepts/news.py           ← NewsConcept
packages/ontology/src/agentverse/ontology/concepts/product.py        ← ProductConcept
packages/ontology/src/agentverse/ontology/concepts/company.py        ← CompanyConcept
packages/ontology/src/agentverse/ontology/concepts/memory_type.py    ← MemoryTypeConcept
packages/ontology/src/agentverse/ontology/concepts/memory_framework.py ← MemoryFrameworkConcept
packages/ontology/src/agentverse/ontology/concepts/application.py    ← ApplicationConcept
packages/ontology/src/agentverse/ontology/concepts/pattern.py        ← PatternConcept
packages/ontology/src/agentverse/ontology/concepts/industry_trend.py ← IndustryTrendConcept
```

**验收标准：**
- [ ] JSON → 标准化本体实例 → Neo4j 节点，全链路打通
- [ ] 重复入库不创建重复节点（利用唯一约束）
- [ ] 关系正确创建（Paper --PROPOSES--> Concept）

**工作量：** 1 天
**依赖：** 模块 3

---

## 五、Phase 2 — 检索与服务（6 天）

### 模块 5：GraphRAG 混合检索

**目标：** 实现向量检索 + 图遍历 + 混合排序的 GraphRAG 引擎。

**数据源：** Neo4j 已有节点 + pgvector 嵌入

**涉及文件：**
```
packages/graphrag/src/agentverse/graphrag/embeddings/models.py   ← OpenAIEmbeddingModel.embed()
packages/graphrag/src/agentverse/graphrag/retrieval/vector.py    ← VectorSearch
packages/graphrag/src/agentverse/graphrag/retrieval/graph.py     ← GraphSearch
packages/graphrag/src/agentverse/graphrag/retrieval/hybrid.py    ← HybridSearch
packages/graphrag/src/agentverse/graphrag/engine.py              ← GraphRAGEngine.query()
packages/graphrag/src/agentverse/graphrag/indexing/pipeline.py   ← IndexingPipeline
```

**实施步骤：**
1. 实现 `OpenAIEmbeddingModel.embed()` — 调用 OpenAI text-embedding-3-small
2. 实现 `IndexingPipeline` — 将节点属性嵌入存入 pgvector
3. 实现 `VectorSearch` — pgvector 余弦相似度检索
4. 实现 `GraphSearch` — Neo4j 多跳遍历（`*1..3`）
5. 实现 `HybridSearch` — 融合向量分数 + 图距离分数
6. 实现 `GraphRAGEngine.query()` — 顶层入口

**验收标准：**
- [ ] 查询 "ReAct 的后继方法" 返回 Reflexion、Plan-and-Execute
- [ ] 混合检索比纯向量检索召回率更高
- [ ] 响应延迟 < 2s（100 跳以内）

**工作量：** 3 天
**依赖：** 模块 4

---

### 模块 6：概念关系浏览器 API

**目标：** 提供概念 CRUD 和图遍历查询的 REST API。

**数据源：** Neo4j 已有数据

**涉及文件：**
```
apps/api/src/agentverse/api/api/v1/concepts.py    ← CRUD + neighbors 端点
apps/api/src/agentverse/api/models/request.py     ← ConceptCreate
apps/api/src/agentverse/api/models/response.py    ← ConceptResponse
apps/api/src/agentverse/api/db/neo4j.py           ← Neo4j 连接池
```

**新增端点：**
```
GET    /api/v1/concepts                  ← 概念列表（分页 + 分类过滤）
GET    /api/v1/concepts/{name}           ← 概念详情 + 关系列表
GET    /api/v1/concepts/{name}/neighbors ← N 跳邻居子图
POST   /api/v1/concepts                  ← 创建/更新概念
DELETE /api/v1/concepts/{name}           ← 删除概念及关系
GET    /api/v1/concepts/{name}/timeline  ← 演化时间线
```

**验收标准：**
- [ ] 所有端点返回 Pydantic 模型
- [ ] 支持分页（`?page=1&size=20`）
- [ ] 邻居查询支持深度参数（`?depth=2`）

**工作量：** 1 天
**依赖：** 模块 4

---

### 模块 7：框架生态映射

**目标：** 爬取主流 AI Agent 框架信息，构建框架→概念的能力映射图。

**数据源：**

| 框架 | GitHub 仓库 | 关注维度 |
|------|------------|---------|
| LangGraph | langchain-ai/langgraph | 状态机、持久化、多 Agent |
| CrewAI | crewaiinc/crewai | 角色化协作、任务委派 |
| AutoGen | microsoft/autogen | 多智能体对话、人在回路 |
| LlamaIndex | run-llama/llama_index | RAG、数据检索、Agent 集成 |
| Semantic Kernel | microsoft/semantic-kernel | 企业级、.NET/Java/Python |
| Dify | langgenius/dify | 低代码、可视化编排 |
| Mem0 | mem0ai/mem0 | 生产级长时记忆 |
| Zep | getzep/zep | 对话时序记忆 |
| LangMem | langchain-ai/langmem | LangGraph 原生记忆组件 |

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/github.py    ← GitHubCrawler.crawl()
packages/ontology/src/agentverse/ontology/concepts/framework.py
```

**验收标准：**
- [ ] 9 个框架全部入库，包含 stars/forks/latest_version/description
- [ ] 每个框架关联 3+ 个核心概念
- [ ] `GET /api/v1/frameworks` 可查询

**工作量：** 1 天
**依赖：** 模块 1

---

### 模块 8：记忆框架数据采集

**目标：** 采集 Agent 记忆机制的论文和框架数据，构建记忆专题子图。

**数据源：**

| 数据源 | 类型 | 获取方式 |
|--------|------|---------|
| TsinghuaC3I/Awesome-Memory-for-Agents | Awesome 仓库 | Git clone + MD 解析 |
| AgentMemoryWorld/Awesome-Agent-Memory | Awesome 仓库 | Git clone + MD 解析 |
| yyyujintang/Awesome-Agent-Memory-Papers | Awesome 仓库 | Git clone + MD 解析 |
| DEEP-PolyU/Awesome-GraphMemory | Awesome 仓库 | Git clone + MD 解析 |
| topoteretes/awesome-ai-memory | Awesome 仓库 | Git clone + MD 解析 |
| Mem0 官方文档 | 文档 | 爬虫 |
| LangMem 官方文档 | 文档 | 爬虫 |

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/awesome_parser.py    ← [新增] AwesomeMarkdownParser
packages/ontology/src/agentverse/ontology/concepts/memory_type.py    ← [新增]
packages/ontology/src/agentverse/ontology/concepts/memory_framework.py ← [新增]
```

**新增节点类型：**
```
MemoryType        — 记忆类型（短期/长期/情景/语义/程序/图记忆）
MemoryFramework   — 记忆框架（Mem0/Zep/LangMem/Letta/Cognee）
MemoryBenchmark   — 评测基准（LoCoMo/LongMemEval/BEAM）
```

**验收标准：**
- [ ] 5 个 Awesome 仓库解析成功，提取 50+ 篇记忆论文
- [ ] 5+ 记忆框架入库（Mem0/Zep/LangMem/Letta/Cognee）
- [ ] 记忆类型分类正确（情景/语义/程序/图记忆）

**工作量：** 2 天
**依赖：** 模块 1, 模块 4

---

## 六、Phase 3 — 前端与自动化（6 天）

### 模块 9：Web 前端知识图谱可视化

**目标：** 在浏览器中交互式浏览知识图谱。

**数据源：** 模块 6 的 API 输出

**涉及文件：**
```
apps/web/src/app/graph/page.tsx              ← GraphExplorer 页面
apps/web/src/components/graph/GraphCanvas.tsx ← Cytoscape.js 渲染
apps/web/src/components/graph/GraphControls.tsx ← 控制面板
apps/web/src/lib/api.ts                      ← API 客户端
```

**验收标准：**
- [ ] 自动渲染前 50 个高连接度节点
- [ ] 点击节点展开 1 跳邻居
- [ ] 搜索框输入后 500ms debounce 调用 API
- [ ] 移动端响应式布局

**工作量：** 3 天
**依赖：** 模块 6

---

### 模块 10：多源自动知识流水线

**目标：** 定时自动执行 爬取→提取→入库→索引 全链路。

**涉及文件：**
```
apps/worker/src/agentverse/worker/main.py
apps/worker/src/agentverse/worker/scheduler.py
apps/worker/src/agentverse/worker/tasks/crawl.py
apps/worker/src/agentverse/worker/tasks/extract.py
apps/worker/src/agentverse/worker/tasks/index.py
```

**调度计划：**

| 任务 | 频率 | 数据源 | 超时 |
|------|------|--------|------|
| ArXiv 论文爬取 | 每日 02:00 | arXiv API | 10min |
| 论文概念提取 | 爬取完成后 | LLM | 30min |
| GitHub 框架更新 | 每周一 03:00 | GitHub API | 5min |
| GraphRAG 索引更新 | 入库完成后 | pgvector | 10min |

**验收标准：**
- [ ] 任务链自动串联（crawl → extract → index）
- [ ] 失败重试 3 次（指数退避）
- [ ] 日志记录每次任务的执行状态

**工作量：** 1 天
**依赖：** 模块 2, 3, 4, 5

---

### 模块 11：行业资讯 RSS 管道

**目标：** 通过 RSS 订阅自动采集行业资讯，构建动态知识图谱。

**数据源：**

| 资源 | RSS 地址 | 更新频率 |
|------|---------|---------|
| The Rundown AI | RSS | 每日 |
| Superhuman AI | RSS | 每日 |
| TLDR AI | RSS | 每日 |
| OpenAI Blog | RSS | 不定期 |
| Anthropic Blog | RSS | 不定期 |
| DeepMind Blog | RSS | 不定期 |
| Hugging Face Papers | RSS | 每日 |

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/rss.py    ← [新增] RSSCrawler
packages/ontology/src/agentverse/ontology/concepts/news.py    ← [新增] NewsConcept
packages/ontology/src/agentverse/ontology/concepts/product.py ← [新增] ProductConcept
```

**验收标准：**
- [ ] 7 个 RSS 源全部接入
- [ ] 资讯自动提取标题/来源/日期/摘要
- [ ] LLM 提取资讯中的产品发布/融资/合作关系

**工作量：** 1 天
**依赖：** 模块 3

---

### 模块 12：Agent 演化时间线

**目标：** 追踪概念的演化路径（Chain-of-Thought → ReAct → Reflexion → Graph Agents）。

**涉及文件：**
```
apps/api/src/agentverse/api/api/v1/timeline.py    ← [新增] timeline 端点
```

**Cypher 查询：**
```cypher
MATCH path = (c:Concept {name: $name})-[:EVOLVES_TO*1..5]->(next)
RETURN path
```

**验收标准：**
- [ ] 查询 "Chain-of-Thought" 返回完整演化链
- [ ] 支持 `?direction=forward|backward|both`
- [ ] 响应包含每个节点的时间属性

**工作量：** 0.5 天
**依赖：** 模块 4

---

## 七、Phase 4 — 高阶智能（需大量数据积累后）

| # | 模块 | 数据需求 | 描述 |
|---|------|---------|------|
| 13 | AI Agent 搜索引擎 | 知识图谱 1000+ 节点 | 自然语言→多跳检索→结构化回答 |
| 14 | Agent 推荐系统 | 框架能力矩阵 + 用户行为 | 根据项目需求推荐框架组合 |
| 15 | Research Copilot | 全量数据 | 学术助手：概念解释、前沿追踪、文献综述生成 |

---

## 八、本体类型扩展清单

### 8.1 现有本体（5 种）

```
packages/ontology/src/agentverse/ontology/concepts/
├── base.py          ← Concept 基类（GraphNode）
├── agent.py         ← AgentConcept
├── framework.py     ← FrameworkConcept
├── paper.py         ← PaperConcept
└── protocol.py      ← ProtocolConcept
```

### 8.2 待新增本体（8 种）

| 概念类 | 节点标签 | 核心属性 | 数据源 |
|--------|---------|---------|--------|
| `NewsConcept` | News | title, source, published_at, summary | RSS |
| `ProductConcept` | Product | company, launched_at, description | RSS / 爬虫 |
| `CompanyConcept` | Company | funding_round, valuation | RSS |
| `MemoryTypeConcept` | MemoryType | category（情景/语义/程序/图） | 论文提取 |
| `MemoryFrameworkConcept` | MemoryFramework | github_url, description | GitHub API |
| `ApplicationConcept` | Application | tech_stack, runnable | GitHub |
| `PatternConcept` | Pattern | example_implementation | 论文/文档 |
| `IndustryTrendConcept` | IndustryTrend | direction, strength, time_window | 报告提取 |

---

## 九、爬虫扩展清单

### 9.1 现有爬虫（3 个骨架）

```
packages/crawler/src/agentverse/crawler/sources/
├── arxiv.py         ← ArxivCrawler（待实现）
├── github.py        ← GitHubCrawler（待实现）
└── web.py           ← WebCrawler（待实现）
```

### 9.2 待新增爬虫（4 个）

| 爬虫 | 数据源 | 获取方式 | 难度 |
|------|--------|---------|------|
| `semantic_scholar.py` | Semantic Scholar API | REST API | ⭐ 低 |
| `papers_with_code.py` | Papers with Code API | REST API | ⭐⭐ 中 |
| `rss.py` | 各 Newsletter/Blog | RSS 解析 | ⭐ 低 |
| `awesome_parser.py` | GitHub Awesome 仓库 | Git clone + MD 解析 | ⭐⭐ 中 |

---

## 十、Neo4j 关系类型扩展清单

### 10.1 现有关系（8 种）

```python
class RelationshipType(str, Enum):
    PROPOSES = "PROPOSES"       # Paper → Concept
    IMPLEMENTS = "IMPLEMENTS"   # Framework → Concept
    EVOLVES_TO = "EVOLVES_TO"   # Concept → Concept
    RELATED_TO = "RELATED_TO"   # * → *
    DEPENDS_ON = "DEPENDS_ON"   # Framework → Framework
    SUPPORTS = "SUPPORTS"       # Framework → Concept
    USED_IN = "USED_IN"         # Concept → Application
    REFERENCES = "REFERENCES"   # Paper → Paper
```

### 10.2 待新增关系（16 种）

| 关系 | 源节点 | 目标节点 | 说明 |
|------|--------|---------|------|
| `CITES` | Paper | Paper | 论文引用 |
| `EXTENDS` | Paper | Paper | 论文扩展 |
| `INSPIRED_BY` | Concept | Concept | 概念启发 |
| `AUTHORED_BY` | Paper | Author | 论文作者 |
| `IMPLEMENTED_BY` | Concept | Framework | 概念实现方 |
| `ACHIEVES_SOTA` | Paper | Benchmark | 达到 SOTA |
| `ANNOUNCED_BY` | News | Company | 发布方 |
| `INVESTED_IN` | Company | Company | 投资关系 |
| `COLLABORATES_WITH` | Framework | Framework | 协作关系 |
| `INTEGRATES_WITH` | Framework | Framework | 集成关系 |
| `SUPPORTS_PATTERN` | Framework | Pattern | 支持模式 |
| `IMPLEMENTS_MEMORY` | MemoryFramework | MemoryType | 实现记忆类型 |
| `BENCHMARKED_ON` | MemoryFramework | MemoryBenchmark | 评测基准 |
| `FEATURED_IN_WEEK` | Paper | TimePeriod | 周报收录 |
| `TRENDING_IN` | Paper | TimePeriod | 热门论文 |
| `UPDATED_TO` | Framework | Version | 版本更新 |

---

## 十一、实施总览表

| # | 模块 | 阶段 | 数据源 | 新增文件 | 工作量 | 依赖 |
|---|------|------|--------|---------|--------|------|
| 0a | Trellis specs 配置 | P0 | — | .trellis/spec/* | 0.5 天 | 无 |
| 0b | OpenSpec 变更模板 | P0 | — | openspec/specs/* | 0.5 天 | 无 |
| 0c | grill-me 需求澄清 | P0 | — | openspec/specs/* | 0.5 天 | 无 |
| 1 | Neo4j Schema 初始化 | P1 | — | — | 0.5 天 | 无 |
| 2 | ArXiv 论文爬取 | P1 | arXiv API | arxiv.py | 1 天 | 模块 1 |
| 3 | LLM 概念提取引擎 | P1 | LLM (GPT-4o) | client.py, paper.py, concept.py, relationship.py | 2 天 | 模块 2 |
| 4 | 本体论规范化入库 | P1 | 模块 2+3 输出 | 8 个新概念类 | 1 天 | 模块 3 |
| 5 | GraphRAG 混合检索 | P2 | Neo4j + pgvector | vector.py, graph.py, hybrid.py, engine.py | 3 天 | 模块 4 |
| 6 | 概念关系浏览器 API | P2 | Neo4j | concepts.py, neo4j.py | 1 天 | 模块 4 |
| 7 | 框架生态映射 | P2 | GitHub API | github.py | 1 天 | 模块 1 |
| 8 | 记忆框架数据采集 | P2 | Awesome 仓库 | awesome_parser.py, memory_type.py, memory_framework.py | 2 天 | 模块 1, 4 |
| 9 | Web 前端可视化 | P3 | 模块 6 API | GraphCanvas.tsx, GraphControls.tsx | 3 天 | 模块 6 |
| 10 | 多源自动流水线 | P3 | 全部 P0+P1 | scheduler.py | 1 天 | 模块 2-6 |
| 11 | 行业资讯 RSS 管道 | P3 | RSS | rss.py, news.py, product.py | 1 天 | 模块 3 |
| 12 | Agent 演化时间线 | P3 | Neo4j | timeline.py | 0.5 天 | 模块 4 |
| **合计** | | | **25+ 数据源** | **30+ 新文件** | **19 天** | |

---

## 十二、关键 Cypher 查询速查

```cypher
-- 某概念的演化链
MATCH path = (c:Concept {name: $name})-[:EVOLVES_TO*1..5]->(next) RETURN path

-- 某框架实现的所有概念
MATCH (f:Framework {name: $name})-[:IMPLEMENTS]->(c) RETURN c.name, c.category

-- 热门 Agent 论文（按关系数量排序）
MATCH (p:Paper)-[r]->(c:Concept) WHERE c.category = 'agent'
RETURN p.title, count(r) AS connections ORDER BY connections DESC LIMIT 20

-- 记忆框架及其支持的记忆类型
MATCH (mf:MemoryFramework)-[:IMPLEMENTS_MEMORY]->(mt:MemoryType)
RETURN mf.name, collect(mt.name) AS memory_types

-- 框架生态：哪些框架实现了相同概念
MATCH (f:Framework)-[:IMPLEMENTS]->(c:Concept)<-[:IMPLEMENTS]-(other:Framework)
WHERE f.name <> other.name
RETURN f.name, other.name, collect(c.name) AS shared_concepts

-- 孤立节点检查
MATCH (n) WHERE NOT (n)--() RETURN labels(n), count(*)
```
