# AgentVerse Extractor

LLM 驱动的信息提取模块，从论文和网页内容中抽取结构化元数据、概念和关系。

## 架构

```
src/agentverse/extractor/
├── __init__.py
├── paper.py         # 论文元数据提取
├── concepts.py      # 概念/实体识别
├── relationships.py # 关系抽取
└── llm.py           # LLM 调用封装
```

## 核心功能

- **论文元数据提取** — 标题、作者、摘要、DOI 等字段解析
- **概念识别** — 从文本中识别 AI Agent 相关的核心概念
- **关系抽取** — 识别概念间的语义关系（如 `AGENT_USES_FRAMEWORK`）
- **LLM 增强** — 利用大语言模型辅助复杂文本的结构化提取

## 使用

```python
from agentverse.extractor.paper import extract_paper_metadata
from agentverse.extractor.concepts import extract_concepts

# 提取论文元数据
metadata = await extract_paper_metadata(raw_text)

# 从文本中提取概念
concepts = await extract_concepts(text, domain="ai-agents")
```

## 依赖

- **PydanticAI** — 结构化 LLM 输出
- **LLM Provider** — 支持 OpenAI / Anthropic 等模型后端

## 测试

```bash
pytest packages/extractor/tests/ -v
```
