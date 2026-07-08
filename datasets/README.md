# Datasets

数据集目录，包含 AgentVerse 使用的数据源引用和示例数据。

## 数据来源

| 来源 | 说明 | 类型 |
|------|------|------|
| arXiv | AI Agent 相关论文 | 学术论文 |
| GitHub | Agent 框架和工具仓库 | 代码仓库 |
| MCP / A2A 协议 | 协议规范文档 | 技术规范 |

## 数据格式

### 论文数据

```json
{
  "title": "AutoGPT: An Autonomous GPT-4 Experiment",
  "authors": ["Significant Gravitas"],
  "abstract": "...",
  "source": "arxiv",
  "url": "https://arxiv.org/abs/2304.05264"
}
```

### 概念节点

```json
{
  "name": "ReAct",
  "description": "Reasoning and Acting paradigm for LLM agents",
  "category": "Architecture"
}
```

### 关系

```json
{
  "source": "AutoGPT",
  "target": "GPT-4",
  "type": "USES"
}
```

## 导入方式

1. **API 批量导入** — `POST /api/v1/batch/concepts` 和 `POST /api/v1/batch/relationships`
2. **Worker 异步任务** — 提交 TaskIQ 任务进行后台批量导入
3. **脚本导入** — 使用 `scripts/kg/` 目录下的图谱构建脚本
