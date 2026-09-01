# feasibility-report-writer

按章节模板把项目资料编制成完整的**科研立项可行性分析报告**（如宁波市公益类科技计划项目可行性分析报告）。分 5 阶段执行，每阶段产物落盘，并单独输出「参考文献与信源清单」供人工复核。

它把质量放在「篇幅」和「口号」之前，重点控制：

- 事实、推断、待确认项与研发建议不混写，关键信息标注证据状态；
- 严格按模板 6 章结构，每章不突破字数硬限（800/500/1000/1000/2000/1000）；
- 政策、现状、产业数据均有信源，统一在独立信源清单（**正文不出现引用标记**）；
- 研究内容↔关键技术↔技术路线↔进度↔预期目标前后呼应、指标互不矛盾；
- 量化效益/指标必有测算依据，否则改定性并标注；
- 无网络检索时显式声明「未执行外部检索」，绝不编造文号/数据/链接；
- 输出 Markdown + 可直接交付的 Word：pandoc 转换后由 python-docx 精细套版，严格对齐 `可行性分析报告.doc` 的字号（小一/三号/小三/四号）、字体（黑体/宋体）、首行缩进2字符、封面、页眉与「第 X 页」页脚。

## 目录

```text
feasibility-report-writer/
├── SKILL.md                          # 主指令：路由 + 5 阶段工作流 + 输出契约
├── QUICK_START.md                    # 快速上手
├── README.md
├── requirements.txt                  # pypandoc / python-docx / matplotlib
├── templates/
│   └── research-report-reference.docx # pandoc 样式参考（由用户 .doc 转换）
├── references/
│   ├── report-template.md            # ★ 拆解后的真模板（6 章 + 封面 + 字数限 + 写作指引）
│   ├── section-writing-guide.md      # 分章深度写作指引 + 范例 + 字数策略
│   ├── intake-and-facts.md           # 材料摄取 + 事实底稿 + 证据状态
│   ├── research-and-evidence.md      # 联网调研 + 信源清单规范
│   └── quality-checklist.md          # 五道质量门
├── scripts/
│   ├── office_to_markdown.py         # 摄取 .doc/.docx/.ppt/.pptx
│   ├── wordcount_check.py            # 按章字数对照硬限
│   ├── generate_docx.py              # Markdown→Word + 信源清单 + 引用门 + 页脚
│   └── setup_env.sh                  # venv 依赖
├── examples/
│   └── project_brief.sample.json     # 结构化项目画像样例
└── evals/
    └── evals.json
```

## 模板来源

`references/report-template.md` 由用户提供的 `可行性分析报告.doc`（宁波市公益类科技计划项目可行性分析报告）拆解而来。原 .doc 中保留的「概述…」官方写作指引已原样保存在各节，作为评审规范。

## 与 feasibility-decomposition 的区别

- **本技能**：按章节模板产出**完整可研报告**（科研立项 / 科技计划项目）。
- **feasibility-decomposition**：对标政策/标准做**可行性分析 + V 字模型拆解 + 四张清单**（数字化改革课题/奖项申报）。
- 二者可串联：拆解结论可作为本报告的输入。

## 安装

本项目作为 aj-skills 仓库的一个 skill，按仓库根目录 README 的方式安装；单独使用时直接进入本目录，依赖见 `requirements.txt`，首次出 Word 前运行 `bash scripts/setup_env.sh`。

## 风险说明

产物为可行性分析报告草案，非立项通过保证。效益测算、技术指标须由申报单位结合实际财务、研发能力与最新政策复核。
