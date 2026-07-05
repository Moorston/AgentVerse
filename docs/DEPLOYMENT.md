# AgentVerse 部署指南

> 本文档说明如何在开发和生产环境中部署 AgentVerse。

---

## 1. 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.12+ | 后端运行时 |
| Node.js | 22+ | 前端构建 |
| Docker | 24+ | 容器化部署 |
| Docker Compose | 2.20+ | 服务编排 |
| uv | 0.11+ | Python 包管理 |

---

## 2. 开发环境部署

### 2.1 快速启动（一键）

```bash
# 克隆仓库
git clone https://github.com/your-org/agentverse.git
cd agentverse

# 安装依赖
uv sync
cd apps/web && npm install && cd ../..

# 复制环境变量
cp .env.example .env

# 启动数据库
docker compose up -d neo4j postgres

# 初始化 Schema
python scripts/init_schema.py

# 加载种子数据
python scripts/seed_data.py

# 启动 API
uvicorn agentverse.api.main:app --reload --port 8000

# 启动前端（另一个终端）
cd apps/web && npm run dev
```

### 2.2 Makefile 快捷命令

```bash
make db-start        # 启动数据库
make schema          # 初始化 Schema
make seed            # 加载种子数据
make api             # 启动 API
make web             # 启动前端
make test-unit       # 运行单元测试
make pipeline        # 运行数据管道
make pipeline-dry    # 干跑数据管道
```

### 2.3 验证部署

```bash
# 检查 API 健康
curl http://localhost:8000/api/v1/health

# 查看 API 文档
open http://localhost:8000/docs

# 检查前端
open http://localhost:3000
```

---

## 3. Docker 部署

### 3.1 使用 Docker Compose（推荐）

```bash
# 启动全部服务
docker compose up -d --build

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f api
docker compose logs -f worker

# 停止服务
docker compose down
```

### 3.2 单独构建服务

```bash
# 构建 API
docker build -f docker/api.Dockerfile -t agentverse-api .

# 构建 Worker
docker build -f docker/worker.Dockerfile -t agentverse-worker .

# 构建 Web
docker build -f docker/web.Dockerfile -t agentverse-web ./apps/web
```

### 3.3 环境变量配置

创建 `.env` 文件：

```bash
# 环境
ENVIRONMENT=production
LOG_LEVEL=INFO

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# PostgreSQL
POSTGRES_DSN=postgresql+asyncpg://agentverse:your_password@postgres:5432/agentverse
POSTGRES_USER=agentverse
POSTGRES_PASSWORD=your_password
POSTGRES_DB=agentverse

# LLM
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# 前端
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 4. 生产环境配置

### 4.1 Neo4j 生产配置

```yaml
# docker-compose.yml 中 neo4j 服务
neo4j:
  image: neo4j:5-enterprise  # 或 neo4j:5-community
  environment:
    NEO4J_AUTH: neo4j/your_secure_password
    NEO4J_dbms_memory_pagecache_size: 2G
    NEO4J_dbms_memory_heap_max__size: 4G
    NEO4J_dbms_connector_bolt_listen__address: ":7687"
    NEO4J_dbms_connector_http_listen__address: ":7474"
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs
  deploy:
    resources:
      limits:
        memory: 8G
        cpus: "4"
```

### 4.2 PostgreSQL 生产配置

```yaml
postgres:
  image: pgvector/pgvector:pg17
  environment:
    POSTGRES_USER: agentverse
    POSTGRES_PASSWORD: your_secure_password
    POSTGRES_DB: agentverse
  volumes:
    - postgres_data:/var/lib/postgresql/data
  command: >
    postgres
    -c shared_buffers=1GB
    -c effective_cache_size=4GB
    -c maintenance_work_mem=256MB
    -c max_connections=200
```

### 4.3 API 生产配置

```bash
# 使用 uvicorn 生产模式
uvicorn agentverse.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --access-log \
  --log-level info
```

### 4.4 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name agentverse.example.com;

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Web
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. 数据管道配置

### 5.1 定时任务（Cron）

```bash
# 每日 2:00 爬取 arXiv
0 2 * * * cd /app && python scripts/run_pipeline.py --max-papers 100

# 每周一 3:00 更新框架数据
0 3 * * 1 cd /app && python -c "import asyncio; from agentverse.worker.tasks.crawl import run_crawl; asyncio.run(run_crawl('github'))"

# 每日 8:00 爬取 RSS
0 8 * * * cd /app && python -c "import asyncio; from agentverse.worker.tasks.crawl import run_crawl; asyncio.run(run_crawl('rss'))"
```

### 5.2 Worker 后台服务

```bash
# 启动 Worker（包含所有定时任务）
python -m agentverse.worker.main
```

---

## 6. 监控与日志

### 6.1 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/v1/health

# 数据库健康检查（需要 Neo4j 连接）
curl http://localhost:8000/api/v1/health | jq '.neo4j'
```

### 6.2 日志配置

```bash
# 开发环境：Console 格式
LOG_LEVEL=DEBUG

# 生产环境：JSON 格式
LOG_LEVEL=INFO
```

### 6.3 指标端点

```
GET /api/v1/health           — 服务状态
GET /api/v1/concepts?size=1  — 数据库连接状态
GET /docs                    — API 文档
GET /openapi.json            — OpenAPI Schema
```

---

## 7. 备份与恢复

### 7.1 Neo4j 备份

```bash
# 备份
docker exec agentverse-neo4j neo4j-admin database dump neo4j --to-path=/backups/

# 恢复
docker exec agentverse-neo4j neo4j-admin database load neo4j --from-path=/backups/
```

### 7.2 PostgreSQL 备份

```bash
# 备份
docker exec agentverse-postgres pg_dump -U agentverse agentverse > backup.sql

# 恢复
docker exec -i agentverse-postgres psql -U agentverse agentverse < backup.sql
```

---

## 8. 故障排查

| 问题 | 排查步骤 |
|------|---------|
| API 无法连接 Neo4j | 检查 `docker compose ps` 确认 Neo4j 运行；检查 `.env` 中 `NEO4J_URI` |
| 前端无法连接 API | 检查 `NEXT_PUBLIC_API_URL` 配置；检查 CORS 设置 |
| 爬虫超时 | 检查网络连接；增加 `timeout` 参数；检查 API 限速 |
| LLM 提取失败 | 检查 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`；检查 API 配额 |
| pgvector 查询慢 | 检查索引：`CREATE INDEX ON node_embeddings USING ivfflat (embedding)` |
| 内存不足 | 增加 Docker 内存限制；减少 Neo4j pagecache_size |
