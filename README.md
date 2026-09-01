# aj-skills

面向中文专业写作、研究分析、合同审查、知识产权和业务自动化场景的 AI Skills 集合。

## 安装

### 交互式安装

运行以下命令后，按提示选择需要安装的 Skill：

```bash
npx skills add https://github.com/zuoa/aj-skills
```

### 安装指定 Skill

Skill 名称以各目录 `SKILL.md` 中的 `name` 字段为准，可使用 `--skill` 精确安装。

| Skill 名称 | 功能 | 安装命令 |
| --- | --- | --- |
| `aj-patent-disclosure-cn` | 生成、审校和优化中国发明专利技术交底书，支持专利点挖掘、技术方案补全、现有技术检索、充分公开检查、附图规划和 Word 文档交付。 | `npx skills add https://github.com/zuoa/aj-skills --skill aj-patent-disclosure-cn` |
| `aj-copyright-writer` | 生成和补正中国计算机软件著作权登记材料，在操作手册与软件设计说明书中选择更能表达软件特点的文档；支持自洽技术栈、软件原型、源程序文档、申请表信息及内部独创性审计。 | `npx skills add https://github.com/zuoa/aj-skills --skill aj-copyright-writer` |
| `contract-review` | 审核 NDA、采购、服务、SaaS、合作、许可及劳动顾问等合同，输出风险分级、条款比对、红线建议、签署意见和审查报告。 | `npx skills add https://github.com/zuoa/aj-skills --skill contract-review` |
| `development-planning-writer` | 编制区域发展规划、地方专项规划及“十五五”规划文本，支持上位政策与数据检索，并输出指标表、项目清单和实施矩阵。 | `npx skills add https://github.com/zuoa/aj-skills --skill development-planning-writer` |
| `social-opinion-writer` | 撰写民主党派、政协和统战系统的社情民意、信息专报及建言材料，支持政策数据调研、多轮校验和正式文档交付。 | `npx skills add https://github.com/zuoa/aj-skills --skill social-opinion-writer` |
| `research-paper-writer` | 辅助中文学术论文写作，覆盖选题、框架、摘要、引言、方法、实验、结论及语言优化，适用于工程、农业、计算机和信息技术方向。 | `npx skills add https://github.com/zuoa/aj-skills --skill research-paper-writer` |
| `article-rewriter` | 对中文文章进行深度改写或翻译改写，支持文本、文件和 URL 输入，以及快速、标准、发布级流程和标题候选生成。 | `npx skills add https://github.com/zuoa/aj-skills --skill article-rewriter` |
| `feasibility-decomposition` | 对照政策、标准或规划开展可行性分析与结构化拆解，输出匹配矩阵、多维可行性、价值亮点和 V 字模型任务清单。 | `npx skills add https://github.com/zuoa/aj-skills --skill feasibility-decomposition` |
| `weekly-monthly-report` | 汇总部门材料并生成周报或月报，分析计划偏差、遗留事项、下期安排和风险，同时列出需要人工补充的信息。 | `npx skills add https://github.com/zuoa/aj-skills --skill weekly-monthly-report` |
| `activity-push` | 从微信公众号文章源提取和判定活动，生成结构化数据、审核材料及推送文本，并可通过企业微信 Webhook 推送。 | `npx skills add https://github.com/zuoa/aj-skills --skill activity-push` |
| `aj-stock-analysis` | 基于 Tushare 开展 A 股价值投资分析，支持股票筛选、个股深度分析、行业对比和估值研究。 | `npx skills add https://github.com/zuoa/aj-skills --skill aj-stock-analysis` |
| `stock-sector-monitoring` | 基于 Tushare 监测 A 股概念板块和龙虎榜，支持剔除 ST、板块排行及结构化 Markdown 报告生成。 | `npx skills add https://github.com/zuoa/aj-skills --skill stock-sector-monitoring` |
