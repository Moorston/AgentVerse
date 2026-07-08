# AgentVerse Web

Next.js 前端应用，提供 AgentVerse 知识图谱的可视化交互界面。

## 架构

```
src/
├── app/
│   ├── layout.tsx        # 根布局
│   ├── page.tsx          # 首页
│   ├── globals.css       # 全局样式
│   ├── compare/          # 框架对比页面
│   ├── concept/          # 概念详情页面
│   ├── frameworks/       # 框架列表页面
│   ├── graph/            # 知识图谱可视化页面
│   ├── monitor/          # 实时监控面板
│   ├── paper/            # 论文详情页面
│   ├── papers/           # 论文列表页面
│   ├── roadmap/          # 路线图页面
│   ├── search/           # 搜索页面
│   └── timeline/         # 时间线页面
├── components/           # 可复用 UI 组件
├── hooks/                # 自定义 React Hooks
└── lib/                  # 工具函数和 API 客户端
```

## 核心页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 项目概览和入口 |
| 知识图谱 | `/graph` | 交互式图谱可视化（Cytoscape.js） |
| 搜索 | `/search` | 语义搜索和全文搜索 |
| 论文库 | `/papers` | 论文浏览和筛选 |
| 框架对比 | `/compare` | AI 框架多维对比 |
| 监控面板 | `/monitor` | 系统状态和图谱统计 |
| 时间线 | `/timeline` | 按时间维度浏览事件 |
| 路线图 | `/roadmap` | 项目发展路线图 |

## 技术栈

- **Next.js 15** — React 全栈框架（App Router）
- **React 19** — UI 库
- **Tailwind CSS 4** — 原子化样式
- **Cytoscape.js** — 图谱可视化引擎
- **Vitest** — 单元测试

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
# → http://localhost:3000

# 构建
npm run build

# 运行测试
npm test

# 类型检查
npm run typecheck
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NEXT_PUBLIC_API_URL` | API 服务地址 | `http://localhost:8000` |
