# AgentVerse Crawler

论文爬取模块，支持从多种数据源获取学术论文和代码仓库数据。

## 架构

```
src/agentverse/crawler/
├── __init__.py
└── sources/         # 数据源适配器
    ├── base.py      # 抽象基类 BaseCrawler
    └── arxiv.py     # arXiv 适配器
```

## 支持的数据源

| 数据源 | 状态 | 说明 |
|--------|------|------|
| arXiv | ✅ 已实现 | 通过 arXiv API 获取论文元数据和摘要 |
| GitHub | 🚧 计划中 | 仓库和框架爬取 |
| Web | 🚧 计划中 | 通用网页爬取 |

## 使用

```python
from agentverse.crawler.sources.arxiv import ArxivCrawler

crawler = ArxivCrawler()
papers = await crawler.search("large language models", max_results=50)
```

## 扩展新数据源

继承 `BaseCrawler` 基类并实现 `search()` 方法即可接入新的论文数据源。

## 测试

```bash
pytest packages/crawler/tests/ -v
```
