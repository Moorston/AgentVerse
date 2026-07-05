# AgentVerse 业务实施与数据源规划

> 本文档是 AgentVerse 项目的**可执行实施指南**，将业务功能与数据源一一映射，作为 AI 编程助手和人类开发者的行动参考。
> 每个模块均包含：目标、数据源、涉及文件、实施步骤、验收标准。

---

## 一、总体实施路线图

```
Phase 1（基础数据层）        Phase 2（检索与映射）       Phase 3（可视化与自动化）     Phase 4（高阶智能）
─────────────────────    ────────────────────────   ───────────────────────────   ─────────────────────
[1] Neo4j Schema 初始化   [5] 框架生态映射             [8] Agent 演化时间线引擎       [11] AI Agent 搜索引擎
[2] ArXiv 论文爬取         [6] GraphRAG 混合检索        [9] Web 前端图谱可视化         [12] Agent 推荐系统
[3] 论文概念 LLM 提取      [7] 概念关系浏览器 API       [10] 多源自动知识流水线        [13] Research Copilot
[4] 本体论规范化入库
```

---

## 二、数据源全景矩阵

### 2.1 数据源分类总表

| 数据源 | 类型 | 获取方式 | 网络要求 | 目标实体 | 目标关系 | 优先级 |
|--------|------|---------|---------|---------|---------|--------|
| arXiv cs.AI / cs.LG / cs.CL | 学术论文 | REST API | 无限制 | `Paper` | `PROPOSES`, `RELATED_TO` | P0 |
| Semantic Scholar | 学术论文 | REST API | 无限制 | `Paper` | `CITES`, `EXTENDS` | P1 |
| Papers with Code | 论文+代码 | REST API | 无限制 | `Paper`, `Framework` | `IMPLEMENTED_BY` | P1 |
| Hugging Face Daily Papers | 学术论文 | RSS / API | 无限制 | `Paper` | `TRENDING_IN` | P2 |
| alphaXiv | 学术论文 | 网页爬虫 | 需翻墙 | `Paper` | `DISCUSSED_IN` | P3 |
| dair-ai/AI-Papers-of-the-Week | Awesome 仓库 | Git clone + MD 解析 | GitHub 限制 | `Paper` | `FEATURED_IN_WEEK` | P1 |
| VoltAgent/awesome-ai-agent-papers | Awesome 仓库 | Git clone + MD 解析 | GitHub 限制 | `Paper` | `CATEGORIZED_AS` | P1 |
| TsinghuaC3I/Awesome-Memory-for-Agents | Awesome 仓库 | Git clone + MD 解析 | GitHub 限制 | `Paper` | `MEMORY_CATEGORY` | P1 |
| caramaschiHG/awesome-ai-agents-2026 | Awesome 仓库 | Git clone + MD 解析 | GitHub 限制 | `Paper`, `Framework`, `Tool` | `PART_OF_ECOSYSTEM` | P2 |
| The Rundown AI / Superhuman AI | 行业资讯 | RSS | 无限制 | `News`, `Product` | `ANNOUNCED_BY` | P1 |
| TLDR AI | 行业资讯 | RSS | 无限制 | `News` | `RELATED_TO` | P2 |
| OpenAI / Anthropic / DeepMind Blog | 官方博客 | RSS / 爬虫 | 无限制 | `Product`, `Research` | `RELEASED` | P1 |
| VentureBeat AI / TechCrunch AI | 行业资讯 | RSS | 无限制 | `Company`, `Startup` | `INVESTED_IN`, `ACQUIRED_BY` | P2 |
| 量子位 / 机器之心 | 中文资讯 | RSS / 爬虫 | 无限制 | `News` | `RELATED_TO` | P3 |
| Track Awesome List | 更新追踪 | RSS | 无限制 | `Framework`, `Tool` | `UPDATED_TO` | P2 |
| LangChain / LangGraph | 开发框架 | GitHub API + docs | npm 镜像 | `Framework`, `Concept` | `IMPLEMENTS` | P0 |
| CrewAI / AutoGen / LlamaIndex | 开发框架 | GitHub API + docs | npm 镜像 | `Framework`, `Concept` | `IMPLEMENTS` | P0 |
| Semantic Kernel / Dify / n8n | 开发框架 | GitHub API + docs | npm 镜像 | `Framework`, `Tool` | `INTEGRATES_WITH` | P1 |
| OpenAI Swarm | 开发框架 | GitHub API | npm 镜像 | `Framework`, `Pattern` | `IMPLEMENTS_PATTERN` | P1 |
| Mem0 | 记忆框架 | GitHub API + docs | npm 镜像 | `MemoryFramework` | `IMPLEMENTS_MEMORY` | P0 |
| Zep / LangMem / Letta / Cognee | 记忆框架 | GitHub API + docs | npm 镜像 | `MemoryFramework` | `IMPLEMENTS_MEMORY_TYPE` | P1 |
| Stanford AI Index Report | 行业报告 | PDF 下载 | 无限制 | `IndustryTrend` | `REPORTS_TREND` | P3 |

### 2.2 数据源→本体节点映射

```
数据源                    →  Neo4j 节点标签          →  关系类型
─────────────────────────────────────────────────────────────────────
arXiv API                 →  Paper, Author           →  AUTHORED_BY, PROPOSES
Semantic Scholar          →  Paper                   →  CITES, EXTENDS, INSPIRED_BY
Papers with Code          →  Paper, CodeRepo         →  IMPLEMENTED_BY, ACHIEVES_SOTA
GitHub Awesome 仓库       →  Paper, Framework, Tool  →  CATEGORIZED_AS, PART_OF_ECOSYSTEM
RSS Newsletters           →  News, Product, Company  →  ANNOUNCED_BY, RAISED_BY
官方技术博客               →  Product, API            →  RELEASED, DOCUMENTS
开发框架仓库               →  Framework, Pattern      →  IMPLEMENTS, SUPPORTS_PATTERN
记忆框架仓库               →  MemoryFramework         →  IMPLEMENTS_MEMORY, BENCHMARKED_ON
行业报告                   →  IndustryTrend           →  REPORTS_TREND, INFLUENCES
```

---

## 三、业务模块实施详情

---

### 模块 1：Neo4j Schema 初始化

**目标：** 建立数据库约束和索引，确保所有后续数据入库的一致性。

**数据源：** 无（纯 schema 操作）

**涉及文件：**
```
packages/graph-core/src/agentverse/graph_core/schema/constraints.py
packages/graph-core/src/agentverse/graph_core/schema/indexes.py
packages/graph-core/src/agentverse/graph_core/client.py
```

**实施步骤：**
1. 确保 Docker 中 Neo4j 服务运行：`docker compose up -d neo4j`
2. 实现 `GraphClient.connect()` 和 `GraphClient.close()`
3. 实现 `apply_constraints()` — 执行 5 条唯一约束（Agent/Framework/Concept/Paper/Protocol）
4. 实现 `apply_indexes()` — 执行 4 条查询索引
5. 新增约束：`MemoryFramework`, `Application`, `Product`, `Company`, `News`

**验收标准：**
- [ ] `GraphClient` 能连接本地 Neo4j（bolt://localhost:7687）
- [ ] 所有约束创建成功，重复插入同名节点报错
- [ ] 索引创建成功，查询性能验证

**工作量：** 0.5 天

---

### 模块 2：ArXiv 论文爬取

**目标：** 通过 arXiv API 自动获取 AI Agent 相关论文，建立论文数据池。

**数据源：** arXiv REST API（无访问限制）

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/arxiv.py     ← 实现 ArxivCrawler
packages/crawler/src/agentverse/crawler/base.py              ← CrawlResult（已定义）
packages/crawler/src/agentverse/crawler/rate_limiter.py      ← 限速（已实现）
apps/worker/src/agentverse/worker/tasks/crawl.py             ← 调度入口
```

**实施步骤：**
1. 实现 `ArxivCrawler.crawl()` — 调用 `http://export.arxiv.org/api/query`
2. 查询参数：`cat:cs.AI OR cat:cs.LG OR cat:cs.CL`，按时间排序，`max_results=100`
3. 解析 XML 响应，提取：标题、作者列表、摘要、DOI、分类、发布日期
4. 封装为 `CrawlResult` 返回
5. `rate_limiter.py` 已实现，设置 `requests_per_second=3`（arXiv 限制）
6. 实现增量爬取：记录上次爬取时间，仅获取新论文

**验收标准：**
- [ ] 单次调用返回 100 篇论文的结构化数据
- [ ] 数据包含 title, authors, abstract, doi, categories, published_date
- [ ] 限速生效，不会触发 arXiv 429 错误
- [ ] 增量爬取正确跳过已有论文

**工作量：** 1 天

---

### 模块 3：论文概念 LLM 提取

**目标：** 从论文摘要中通过 LLM 提取核心概念、概念间关系、框架实现关系。

**数据源：** 模块 2 输出的论文数据 + LLM（OpenAI GPT-4o / Claude Sonnet 4）

**涉及文件：**
```
packages/extractor/src/agentverse/extractor/llm/client.py    ← LLMClient（待实现）
packages/extractor/src/agentverse/extractor/llm/prompts.py    ← 提取 prompt（已定义）
packages/extractor/src/agentverse/extractor/extractors/paper.py     ← PaperExtractor
packages/extractor/src/agentverse/extractor/extractors/concept.py   ← ConceptExtractor
packages/extractor/src/agentverse/extractor/extractors/relationship.py ← RelationshipExtractor
apps/worker/src/agentverse/worker/tasks/extract.py            ← 调度入口
```

**实施步骤：**
1. 实现 `LLMClient.complete()` — 封装 OpenAI / Anthropic API 调用
2. 实现 `PaperExtractor.extract()` — 使用 `PAPER_EXTRACTION_PROMPT` 提取论文元数据
3. 实现 `ConceptExtractor.extract()` — 使用 `CONCEPT_EXTRACTION_PROMPT` 提取概念
4. 实现 `RelationshipExtractor.extract()` — 使用 `RELATIONSHIP_EXTRACTION_PROMPT` 提取关系
5. LLM 输出格式：JSON Schema 约束（`response_format: json`），确保结构化输出
6. 实现重试逻辑（`shared/utils/retry.py` 已实现）

**验收标准：**
- [ ] 输入一篇论文摘要，输出包含 concepts[] 和 relationships[]
- [ ] 概念名称标准化（如 "ReAct" 不会变成 "react" 或 "ReAct framework"）
- [ ] 关系类型限定在 `RelationshipType` 枚举范围内
- [ ] 单篇论文处理延迟 < 10s（GPT-4o）

**工作量：** 2 天

---

### 模块 4：本体论规范化入库

**目标：** 将爬取和提取的数据标准化为本体实例，写入 Neo4j。

**数据源：** 模块 2 + 模块 3 的输出

**涉及文件：**
```
packages/ontology/src/agentverse/ontology/normalizer.py      ← normalize_* 函数（已定义骨架）
packages/ontology/src/agentverse/ontology/concepts/          ← 各概念类（已定义）
packages/graph-core/src/agentverse/graph_core/repository/base.py ← BaseRepository（已实现）
```

**实施步骤：**
1. 实现 `normalize_paper()` — 将 LLM 输出映射为 `PaperConcept`
2. 实现 `normalize_agent()` / `normalize_framework()` / `normalize_protocol()`
3. 扩展概念类：新增 `MemoryTypeConcept`, `ApplicationConcept`, `ProductConcept`
4. 实现 `BaseRepository.create_node()` 的 Cypher 语句（已定义骨架）
5. 实现关系创建：`MERGE` + `CREATE` 避免重复

**验收标准：**
- [ ] 输入 JSON → 标准化本体实例 → Neo4j 节点，全链路打通
- [ ] 重复入库同一篇论文不会创建重复节点（利用唯一约束）
- [ ] 关系正确创建（`Paper --PROPOSES--> Concept`）

**工作量：** 1 天

---

### 模块 5：框架生态映射

**目标：** 爬取主流 AI Agent 框架的 GitHub 仓库信息，构建框架→概念的能力映射图。

**数据源：**
- GitHub API（stars, forks, releases, README）— 无访问限制
- 各框架官方文档站点
- kyrolabs/awesome-agents（Git clone + MD 解析）

**涉及文件：**
```
packages/crawler/src/agentverse/crawler/sources/github.py    ← GitHubCrawler（待实现）
packages/ontology/src/agentverse/ontology/concepts/framework.py ← FrameworkConcept
```

**目标框架清单：**

| 框架 | GitHub 仓库 | 关注维度 |
|------|------------|---------|
| LangGraph | langchain-ai/langgraph | 状态机、持久化、多 Agent |
| CrewAI | crewaiinc/crewai | 角色化协作、任务委派 |
| AutoGen | microsoft/autogen | 多智能体对话、人在回路 |
| LlamaIndex | run-llama/llama_index | RAG、数据检索、Agent 集成 |
| Semantic Kernel | microsoft/semantic-kernel | 企业级、.NET/Java/Python |
| Dify | langgenius/dify | 低代码、可视化编排 |
| n8n | n8n-io/n8n | 工作流自动化、Agent 集成 |
| OpenAI Swarm | openai/swarm | 轻量多 Agent 编排 |

**实施步骤：**
1. 实现 `GitHubCrawler.crawl()` — 调用 GitHub REST API 获取仓库元数据
2. 爬取每个框架的 README，LLM 提取核心特性描述
3. 构建 `Framework --IMPLEMENTS--> Concept` 关系（如 `LangGraph --IMPLEMENTS--> StateMachine`）
4. 定时更新 star 数、最近 release 版本、活跃度指标

**验收标准：**
- [ ] 8 个框架全部入库，包含 stars/forks/latest_version/description
- [ ] 每个框架关联 3+ 个核心概念
- [ ] 支持 `GET /api/v1/frameworks` 查询

**工作量：** 2 天

---

### 模块 6：GraphRAG 混合检索

**目标：** 实现向量检索 + 图遍历 + 混合排序的 GraphRAG 引擎。

**数据源：** Neo4j 中已有的 `Paper` + `Concept` + `Framework` 节点和关系

**涉及文件：**
```
packages/graphrag/src/agentverse/graphrag/embeddings/models.py   ← OpenAIEmbeddingModel（待实现）
packages/graphrag/src/agentverse/graphrag/retrieval/vector.py    ← VectorSearch（待实现）
packages/graphrag/src/agentverse/graphrag/retrieval/graph.py     ← GraphSearch（待实现）
packages/graphrag/src/agentverse/graphrag/retrieval/hybrid.py    ← HybridSearch（待实现）
packages/graphrag/src/agentverse/graphrag/engine.py              ← GraphRAGEngine（待实现）
apps/api/src/agentverse/api/api/v1/search.py                     ← search 端点
```

**实施步骤：**
1. 实现 `OpenAIEmbeddingModel.embed()` — 调用 OpenAI Embedding API
2. 实现 `IndexingPipeline` — 将节点属性（标题+描述）嵌入存入 pgvector
3. 实现 `VectorSearch` — pgvector 余弦相似度检索
4. 实现 `GraphSearch` — Neo4j 多跳遍历（`MATCH path = (n)-[*1..3]-(m)`）
5. 实现 `HybridSearch` — 融合向量分数 + 图距离分数
6. 接入 API 端点 `GET /api/v1/search?q=...`

**验收标准：**
- [ ] 查询 "ReAct 的后继方法" 能返回 Reflexion、Plan-and-Execute 等节点
- [ ] 混合检索比纯向量检索召回率更高（可通过 benchmark 验证）
- [ ] 响应延迟 < 2s（100 跳以内）

**工作量：** 3 天

---

### 模块 7：概念关系浏览器 API

**目标：** 提供概念 CRUD 和图遍历查询的 REST API。

**数据源：** Neo4j 已有数据

**涉及文件：**
```
apps/api/src/agentverse/api/api/v1/concepts.py    ← list/get/create/neighbors 端点
apps/api/src/agentverse/api/models/request.py     ← ConceptCreate（已定义）
apps/api/src/agentverse/api/models/response.py    ← ConceptResponse（已定义）
```

**实施步骤：**
1. 实现 `GET /api/v1/concepts` — 分页列表，支持 category 过滤
2. 实现 `GET /api/v1/concepts/{name}` — 单个概念详情 + 关系列表
3. 实现 `GET /api/v1/concepts/{name}/neighbors` — N 跳邻居子图
4. 实现 `POST /api/v1/concepts` — 创建/更新概念
5. 实现 `DELETE /api/v1/concepts/{name}` — 删除概念及关系

**验收标准：**
- [ ] 所有端点返回 Pydantic 模型，非裸 dict
- [ ] 支持分页（`?page=1&size=20`）
- [ ] 邻居查询支持深度参数（`?depth=2`）

**工作量：** 1 天

---

### 模块 8：Agent 演化时间线引擎

**目标：** 追踪概念的演化路径（如 Chain-of-Thought → ReAct → Reflexion → Graph Agents）。

**数据源：** Neo4j `EVOLVES_TO` 关系链

**涉及文件：**
```
apps/api/src/agentverse/api/api/v1/timeline.py    ← 新增 timeline 端点
packages/graph-core/src/agentverse/graph_core/repository/base.py ← 扩展查询方法
```

**实施步骤：**
1. 实现 Cypher 查询：`MATCH path = (c:Concept {name: $name})-[:EVOLVES_TO*1..5]->(n) RETURN path`
2. 实现正向演化链和反向溯源链
3. 新增 API 端点：`GET /api/v1/concepts/{name}/timeline`
4. 响应格式：按时间排序的节点列表 + 关系列表

**验收标准：**
- [ ] 查询 "Chain-of-Thought" 返回完整演化链
- [ ] 支持 `?direction=forward|backward|both`
- [ ] 响应包含每个节点的时间属性（如论文发表日期）

**工作量：** 1 天

---

### 模块 9：Web 前端知识图谱可视化

**目标：** 在浏览器中交互式浏览知识图谱。

**数据源：** 模块 7 的 API 输出

**涉及文件：**
```
apps/web/src/app/graph/page.tsx              ← GraphExplorer 页面（已有骨架）
apps/web/src/components/graph/GraphCanvas.tsx ← Cytoscape.js 渲染（待实现）
apps/web/src/components/graph/GraphControls.tsx ← 控制面板（待实现）
apps/web/src/lib/api.ts                      ← API 客户端（已实现骨架）
apps/web/src/types/graph.ts                  ← 类型定义（已实现）
```

**实施步骤：**
1. 安装 Cytoscape.js：`npm install cytoscape @types/cytoscape`
2. 实现 `GraphCanvas` 组件 — Cytoscape.js 初始化 + 节点/边渲染
3. 实现节点点击事件 — 展开邻居子图
4. 实现搜索框 — 调用 `/api/v1/search`，高亮结果节点
5. 实现分类过滤 — 按 `Paper/Framework/Concept/MemoryFramework` 切换显示
6. 实现 `GraphControls` — 缩放、布局切换（dagre/cose）、全屏

**验收标准：**
- [ ] 页面加载后自动渲染前 50 个高连接度节点
- [ ] 点击节点展开 1 跳邻居
- [ ] 搜索框输入后 500ms debounce 调用 API
- [ ] 移动端响应式布局

**工作量：** 3 天

---

### 模块 10：多源自动知识流水线

**目标：** 定时自动执行 爬取→提取→入库→索引 全链路。

**数据源：** 所有 P0 + P1 数据源

**涉及文件：**
```
apps/worker/src/agentverse/worker/main.py         ← 入口（已有骨架）
apps/worker/src/agentverse/worker/scheduler.py    ← Scheduler（已实现）
apps/worker/src/agentverse/worker/tasks/crawl.py  ← crawl 任务
apps/worker/src/agentverse/worker/tasks/extract.py ← extract 任务
apps/worker/src/agentverse/worker/tasks/index.py  ← index 任务
```

**调度计划：**

| 任务 | 频率 | 数据源 | 超时 |
|------|------|--------|------|
| ArXiv 论文爬取 | 每日 02:00 | arXiv API | 10min |
| 论文概念提取 | 爬取完成后 | LLM | 30min |
| GitHub 框架更新 | 每周一 03:00 | GitHub API | 5min |
| RSS 资讯爬取 | 每日 08:00 | RSS | 5min |
| GraphRAG 索引更新 | 入库完成后 | pgvector | 10min |
| Awesome 仓库同步 | 每周日 04:00 | Git clone | 15min |

**实施步骤：**
1. 实现 `run_crawl()` — 调用对应 Crawler 子类
2. 实现 `run_extract()` — 调用对应 Extractor 子类
3. 实现 `run_index()` — 调用 `IndexingPipeline`
4. 实现任务链：crawl 完成后自动触发 extract，extract 完成后自动触发 index
5. 实现错误告警：失败时记录日志 + 写入 Neo4j `TaskError` 节点

**验收标准：**
- [ ] Scheduler 正确按计划触发任务
- [ ] 任务链自动串联（crawl → extract → index）
- [ ] 单次失败不影响后续调度（重试 3 次后标记失败）

**工作量：** 2 天

---

### 模块 11-13：Phase 4 高阶业务（预留）

| 模块 | 前置依赖 | 数据需求 | 说明 |
|------|---------|---------|------|
| **AI Agent 搜索引擎** | 模块 6 GraphRAG | 知识图谱 1000+ 节点 | 自然语言→多跳检索→结构化回答 |
| **Agent 推荐系统** | 模块 5 框架映射 + 用户行为 | 框架能力矩阵 | 根据项目需求推荐框架组合 |
| **Research Copilot** | 全部前置 | 全量数据 | 学术助手：概念解释、前沿追踪、文献综述生成 |

---

## 四、新增爬虫实施清单

```
packages/crawler/src/agentverse/crawler/sources/
├── arxiv.py              [待实现] arXiv REST API 爬取
├── github.py             [待实现] GitHub API 仓库元数据
├── web.py                [待实现] 通用网页爬取
├── semantic_scholar.py   [新增]   Semantic Scholar API
├── papers_with_code.py   [新增]   Papers with Code API
├── rss.py                [新增]   RSS 订阅解析器
└── awesome_parser.py     [新增]   GitHub Awesome 仓库 Markdown 解析
```

---

## 五、新增本体类型清单

```
packages/ontology/src/agentverse/ontology/concepts/
├── agent.py              [已有]
├── framework.py          [已有]
├── paper.py              [已有]
├── protocol.py           [已有]
├── news.py               [新增] NewsConcept — 行业资讯
├── product.py            [新增] ProductConcept — AI 产品
├── company.py            [新增] CompanyConcept — 公司
├── memory_type.py        [新增] MemoryTypeConcept — 记忆类型
├── memory_framework.py   [新增] MemoryFrameworkConcept — 记忆框架
├── application.py        [新增] ApplicationConcept — AI 应用
├── pattern.py            [新增] PatternConcept — 设计模式
└── industry_trend.py     [新增] IndustryTrendConcept — 行业趋势
```

---

## 六、Neo4j 关系类型扩展

```
现有关系（RelationshipType 枚举）:
  PROPOSES | IMPLEMENTS | EVOLVES_TO | RELATED_TO | DEPENDS_ON | SUPPORTS | USED_IN | REFERENCES

新增关系:
  CITES                  — Paper → Paper（引用）
  EXTENDS                — Paper → Paper（扩展）
  INSPIRED_BY            — Concept → Concept（启发）
  AUTHORED_BY            — Paper → Author（作者）
  IMPLEMENTED_BY         — Concept → Framework（实现）
  ACHIEVES_SOTA          — Paper → Benchmark（达到 SOTA）
  ANNOUNCED_BY           — News → Company（发布方）
  INVESTED_IN            — Company → Company（投资）
  COLLABORATES_WITH      — Framework → Framework（协作）
  INTEGRATES_WITH        — Framework → Framework（集成）
  SUPPORTS_PATTERN       — Framework → Pattern（支持模式）
  IMPLEMENTS_MEMORY      — MemoryFramework → MemoryType（实现记忆类型）
  BENCHMARKED_ON         — MemoryFramework → MemoryBenchmark（评测基准）
  FEATURED_IN_WEEK       — Paper → TimePeriod（周报收录）
  TRENDING_IN            — Paper → TimePeriod（热门论文）
  UPDATED_TO             — Framework → Version（版本更新）
```

---

## 七、关键 Cypher 查询示例

```cypher
-- 查询某概念的演化链
MATCH path = (c:Concept {name: 'Chain-of-Thought'})-[:EVOLVES_TO*1..5]->(next)
RETURN path

-- 查询某框架实现的所有概念
MATCH (f:Framework {name: 'LangGraph'})-[:IMPLEMENTS]->(c)
RETURN c.name, c.category

-- 查询某论文的所有引用链
MATCH (p:Paper {doi: '10.xxxx'})-[:CITES*1..2]->(cited)
RETURN cited.title, cited.year

-- 查询热门 Agent 论文（按关系数量排序）
MATCH (p:Paper)-[r]->(c:Concept)
WHERE c.category = 'agent'
RETURN p.title, count(r) AS connections
ORDER BY connections DESC LIMIT 20

-- 查询记忆框架及其支持的记忆类型
MATCH (mf:MemoryFramework)-[:IMPLEMENTS_MEMORY]->(mt:MemoryType)
RETURN mf.name, collect(mt.name) AS memory_types

-- 查询框架生态（哪些框架实现了哪些概念）
MATCH (f:Framework)-[:IMPLEMENTS]->(c:Concept)<-[:IMPLEMENTS]-(other:Framework)
WHERE f.name <> other.name
RETURN f.name, other.name, collect(c.name) AS shared_concepts
```

---

## 八、验证与监控

### 8.1 数据质量检查

```cypher
-- 检查孤立节点（无任何关系的节点）
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n), count(*)

-- 检查重复节点（同名不同 ID）
MATCH (n:Concept)
WITH n.name AS name, collect(n) AS nodes
WHERE size(nodes) > 1
RETURN name, size(nodes)

-- 检查缺失属性
MATCH (p:Paper)
WHERE p.title IS NULL OR p.doi IS NULL
RETURN count(p)
```

### 8.2 数据源健康检查

每个爬虫应暴露 `/health` 端点或日志，记录：
- 上次成功爬取时间
- 爬取数量
- 错误率
- API 配额剩余（如 arXiv、Semantic Scholar）

---

## 九、实施总览表

| # | 模块 | 数据源 | 新增节点类型 | 新增爬虫 | 工作量 | 依赖 |
|---|------|--------|------------|---------|--------|------|
| 1 | Neo4j Schema 初始化 | — | — | — | 0.5 天 | 无 |
| 2 | ArXiv 论文爬取 | arXiv API | Paper | arxiv.py | 1 天 | 模块 1 |
| 3 | 论文概念 LLM 提取 | LLM (GPT-4o / Claude) | Concept, Relationship | — | 2 天 | 模块 2 |
| 4 | 本体论规范化入库 | 模块 2+3 输出 | — | — | 1 天 | 模块 3 |
| 5 | 框架生态映射 | GitHub API + Awesome 仓库 | Framework, Concept | github.py, awesome_parser.py | 2 天 | 模块 1 |
| 6 | GraphRAG 混合检索 | Neo4j + pgvector | — | — | 3 天 | 模块 4 |
| 7 | 概念关系浏览器 API | Neo4j | — | — | 1 天 | 模块 4 |
| 8 | Agent 演化时间线 | Neo4j EVOLVES_TO 链 | — | — | 1 天 | 模块 4 |
| 9 | Web 前端可视化 | 模块 7 API | — | — | 3 天 | 模块 7 |
| 10 | 多源自动流水线 | 全部 P0+P1 | — | rss.py, semantic_scholar.py, papers_with_code.py | 2 天 | 模块 2-6 |
| **合计** | | | **8 种新节点** | **5 个新爬虫** | **16.5 天** | |

