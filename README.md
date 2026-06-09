# AI 医管智能体

面向医院管理层的智能数据查询、运营分析与报告生成系统。项目由原来的通用 Text-to-SQL 电商数据问答升级而来，重点从“能生成 SQL”升级为“能服务医院运营管理场景”。

> 所有患者、医生、收费和运营明细均为模拟数据，不涉及真实患者隐私，也不提供诊疗建议。

## 核心能力

- 自然语言查询医院运营数据：门诊量、科室收入、药品收入占比、床位使用率、平均住院日、手术量。
- SQL 安全校验：只允许单条 SELECT，禁止修改性 SQL，默认补 LIMIT。
- 医院管理知识库：解释指标口径、绩效管理、医保控费和手术分级。
- 医管后台驾驶舱：运营总览、趋势分析、科室绩效、智能问答、知识库和改动记录。
- 图表可视化：使用 Streamlit 和 Plotly 展示 KPI 卡片、表格、柱状图、饼图和趋势图。
- 运营简报：自动生成月度医院运营分析报告和管理建议。
- 桌面小组件：支持置顶、拖动、折叠的 AI 医管桌面小拖件。
- 前端骨架治理：沉淀页面注册、设计 token、组件复用规则和 Vibe Coding 前端骨架说明。

## 项目结构

```text
ai_hospital_agent/
├── app.py
├── desktop_floating_assistant.py
├── desktop_widget_assistant.py
├── README.md
├── requirements.txt
├── data/
│   ├── hospital.db
│   └── hospital_schema.json
├── docs/
│   ├── frontend_skeleton.md
│   ├── optimization_comparison.md
│   └── ui_upgrade_change_log.md
├── hospital_docs/
├── skills/
│   └── vibe-frontend-skeleton/
├── scripts/
│   └── generate_hospital_data.py
└── src/
    ├── analysis.py
    ├── charts.py
    ├── rag_agent.py
    ├── report_generator.py
    ├── router.py
    ├── sql_agent.py
    ├── sql_guard.py
    └── prompts.py
```

## 运行方式

```bash
pip install -r requirements.txt
python scripts/generate_hospital_data.py
streamlit run app.py
```

## 在线部署

在线演示地址：<https://ai-hospital-agent.streamlit.app/>

### Streamlit Community Cloud

- Repository：`zhubojie703-maker/ai_hospital_agent`
- Branch：`main`
- Main file path：`app.py`
- Python dependencies：`requirements.txt`

### Render

项目已包含 `render.yaml`。在 Render 中选择从 GitHub 仓库创建 Web Service 或 Blueprint 后，会使用下面的启动命令：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
```

启动桌面小组件：

```bash
python desktop_widget_assistant.py
```

Windows 也可以双击：

```text
启动桌面小拖件.bat
```

如果想使用普通窗口版本，可以运行：

```bash
python desktop_floating_assistant.py
```

## 示例问题

- 本月门诊量最高的 5 个科室是哪些？
- 统计 2026 年 5 月各科室收入排名。
- 最近 7 天床位使用率超过 90% 的科室有哪些？
- 本月药占比是多少？
- 本月耗材收入占比最高的科室有哪些？
- 本月各科室床位周转次数是多少？
- DRG/DIP支付下医院运营应关注哪些指标？
- 药占比是什么意思？
- 生成本月医院运营简报。

## 页面模块

| 页面 | 主要内容 |
|---|---|
| 运营总览 | KPI 卡片、门诊/收入趋势、收入结构、床位风险、科室绩效明细、AI 医管助手 |
| 浮窗问答 | 页面内 AI 小浮窗，输入问题后再展开表格、图表和结论 |
| 智能问答 | 自然语言查询、RAG 指标解释、报告生成 |
| 趋势分析 | 近 60 天门诊与收入趋势、费用结构、床位排名、手术级别分布 |
| 科室绩效 | 科室工作量、收入、药品/耗材占比、床位效率对比 |
| 运营简报 | 月度运营报告和管理建议 |
| 医管知识库 | 指标口径、医保控费、DRG/DIP、绩效考核文档 |
| 改动记录 | UI 和内容升级过程表 |

## 前端骨架优化

本项目根据 Vibe Coding “先定前端骨架，再让 AI 写页面”的方法做了二次整理，新增了：

- `UI_TOKENS`：集中管理颜色、圆角、文字色和图表色板。
- `PAGE_REGISTRY`：统一维护页面名称、模块名和页面用途。
- `render_current_page`：用页面渲染表替代分散的条件路由。
- `docs/frontend_skeleton.md`：记录设计风格、技术骨架、页面边界和组件复用规则。
- `skills/vibe-frontend-skeleton`：把参考视频蒸馏成可复用 Codex skill，项目下载后也能带走这套前端骨架方法。

## 公开依据与数据说明

本项目的指标口径参考了医院运营管理常见统计方式，并结合公开政策资料进行说明：

- 国家卫生健康委：《三级公立医院绩效监测操作手册（2025版）》通知：<https://www.nhc.gov.cn/yzygj/c100068/202506/6a97e937c58b413d8a0ffdcc23d325d4.shtml>
- 国务院办公厅：《关于加强三级公立医院绩效考核工作的意见》：<https://www.gov.cn/zhengce/content/2019-01/30/content_5362266.htm>
- 国家卫生健康委统计信息中心相关卫生健康统计公报入口：<https://www.nhc.gov.cn/guihuaxxs/s10748/>

由于真实 HIS、财务、医保和病案首页数据涉及隐私与机构授权，本 Demo 使用模拟数据生成器创建 `hospital.db`。模拟数据只用于展示系统逻辑，不能代表真实医院经营水平。

## 优化对比

| 对比项 | 原 Text-to-SQL 项目 | 优化后的 AI 医管智能体 |
|---|---|---|
| 项目定位 | 通用电商数据问答 | 医院管理层运营分析助手 |
| 数据库 | `ecommerce.db`，用户/商品/订单 | `hospital.db`，科室/医生/门诊/住院/收费/床位/手术 |
| 问题类型 | 销售额、订单、库存 | 门诊量、科室收入、药品收入占比、床位使用率、平均住院日、手术量 |
| 安全约束 | Prompt 中要求只查数据 | 独立 SQL Guard 强制只允许 SELECT，拦截危险 SQL，自动补 LIMIT |
| 知识问答 | 无制度知识库 | `hospital_docs` 支持指标解释、政策和绩效制度问答 |
| 分析能力 | 主要返回查询结果 | 返回数据表、异常提示和管理建议 |
| 可视化 | 命令行输出 | Streamlit 表格 + Plotly 图表 |
| 报告能力 | 无 | 自动生成医院运营月度简报 |
| 简历表达 | Text-to-SQL Demo | Text-to-SQL + RAG + Router + SQL 安全 + 医管分析智能体 |
