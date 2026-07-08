# AgentVerse Graph-Core

核心图数据库抽象层，定义统一的节点/关系模型和仓库接口，屏蔽底层 Neo4j 细节。

## 架构

```
src/agentverse/graph_core/
├── __init__.py
├── models.py            # 节点和关系的 Pydantic 模型
├── repository/
│   ├── base.py          # 抽象仓库接口
│   └── neo4j_repository.py  # Neo4j 实现
└── driver.py            # Neo4j 驱动管理
```

## 核心抽象

### 节点模型

```python
class Node:
    id: str
    labels: list[str]
    properties: dict[str, Any]
```

### 关系模型

```python
class Relationship:
    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: dict[str, Any]
```

### 仓库接口

| 方法 | 说明 |
|------|------|
| `create_node()` | 创建节点 |
| `get_node()` | 按 ID 获取节点 |
| `list_nodes()` | 列出节点（支持分页和过滤） |
| `delete_node()` | 删除节点（级联删除关系） |
| `create_relationship()` | 创建关系 |
| `delete_relationship()` | 删除关系 |
| `find_paths()` | 查找两节点间的路径 |
| `count_nodes()` | 统计节点数量 |
| `count_relationships()` | 统计关系数量 |

## 使用

```python
from agentverse.graph_core.repository.neo4j_repository import Neo4jRepository

repo = Neo4jRepository(uri="bolt://localhost:7687", user="neo4j", password="pass")
await repo.connect()

node = await repo.create_node(["Concept"], {"name": "LLM", "description": "Large Language Model"})
paths = await repo.find_paths("Concept", "LLM", "Concept", "Attention", max_depth=3)
```

## 测试

```bash
pytest packages/graph-core/tests/ -v
```
