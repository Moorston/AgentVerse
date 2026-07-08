# AgentVerse Ontology

本体定义与 Schema 管理模块，定义 AgentVerse 知识图谱的核心概念和关系类型。

## 架构

```
src/agentverse/ontology/
├── __init__.py
├── schema.py        # 本体 Schema 定义
└── registry.py      # Schema 注册与验证
```

## 核心概念

### 节点类型

| 标签 | 说明 | 关键属性 |
|------|------|----------|
| `Agent` | AI Agent 实体 | name, description, model, framework |
| `Concept` | 知识概念 | name, description, category |
| `Paper` | 学术论文 | title, authors, abstract, doi |
| `Framework` | 技术框架 | name, version, language |
| `Protocol` | 通信协议 | name, version |
| `Task` | 任务类型 | name, description, complexity |

### 关系类型

| 关系 | 源 → 目标 | 说明 |
|------|----------|------|
| `USES` | Agent → Framework | Agent 使用某框架 |
| `IMPLEMENTS` | Agent → Protocol | Agent 实现某协议 |
| `BASED_ON` | Concept → Concept | 概念间的层级关系 |
| `CITES` | Paper → Paper | 论文引用关系 |
| `MENTIONS` | Paper → Concept | 论文中提到的概念 |
| `SOLVES` | Agent → Task | Agent 能解决的任务 |
| `RELATED_TO` | * → * | 通用关联 |

## 使用

```python
from agentverse.ontology.schema import get_schema

schema = get_schema()
print(schema.node_labels)       # ["Agent", "Concept", "Paper", ...]
print(schema.relationship_types) # ["USES", "BASED_ON", ...]
```

## 测试

```bash
pytest packages/ontology/tests/ -v
```
