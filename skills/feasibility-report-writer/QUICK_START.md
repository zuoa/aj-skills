# 快速上手

把项目资料变成一份按模板成文、字数达标、信源可复核的可行性分析报告。

## 最小用法

把你的资料（文件 / 目录 / 口述）给 Claude，说「用 feasibility-report-writer 编制可研报告」。Claude 会按 5 阶段推进，每阶段产物落盘到**当前工作目录**下的 `outputs/`（不写进 skill 目录；脚本用 skill 目录的 `{baseDir}/scripts/...` 调用）。

## 五阶段一览

| 阶段 | 做什么 | 产物 |
|---|---|---|
| 0 摄取·事实底稿 | 读资料、转文本、建事实底稿、标证据状态 | `outputs/project_brief.md` |
| 1 项目信息·大纲 | 填项目画像、生成 6 章大纲、一次确认 | `outputs/outline.md` |
| 2 联网调研·证据 | 检索政策/现状/标杆/数据，每条带来源 | `outputs/research/research_dossier.md` + `sources.json` |
| 3 分章撰写 | 按 6 章模板撰写，严守字数硬限 | `outputs/sections/01..06_*.md` |
| 4 组装·校验·交付 | 组装、字数门、引用门、出 docx + 信源清单 | `outputs/可行性分析报告_*.md/.docx` + `参考文献与信源清单.md` |

## 字数硬限

一 800 / 二 500 / 三 1000 / 四 1000 / 五 2000 / 六 1000（中文字符 + 阿拉伯数字）。

## 关键命令

```bash
# 在用户当前工作目录下执行：产物落 ./outputs/，脚本用 {baseDir}/scripts/... 调用
# 摄取 Office 材料（.doc/.docx/.ppt/.pptx）
python3 {baseDir}/scripts/office_to_markdown.py <你的文件...> --output-dir outputs/intake \
  --manifest outputs/intake/office_manifest.json

# 字数校验（超限返回非零）
python3 {baseDir}/scripts/wordcount_check.py --input outputs/可行性分析报告_项目名_v1.0.md \
  --report outputs/quality_report.json

# 生成 Word + 信源清单（自动注入页脚页码）
python3 {baseDir}/scripts/generate_docx.py \
  --input outputs/可行性分析报告_项目名_v1.0.md \
  --output outputs/可行性分析报告_项目名_v1.0.docx \
  --sources outputs/research/sources.json \
  --report outputs/quality_report.json --with-markdown
```

首次生成 DOCX 前如缺依赖：
```bash
bash {baseDir}/scripts/setup_env.sh
{baseDir}/.venv/bin/python {baseDir}/scripts/generate_docx.py --input outputs/... --output outputs/...
```

## 只做一部分

- 只要某一章 / 某几章 → 直接说写哪章，复用已有事实与信源。
- 只要联网调研 / 信源核查 → 只跑阶段 2，输出调研底稿 + 信源清单。
- 只要字数校验或导出 Word → 只跑阶段 4 的两个脚本。

## 人工复核信源

打开 `outputs/参考文献与信源清单.md`，逐条看「引用要点（章节·引用内容）」→ 回正文核对数据/结论 → 点链接对照原文是否支撑。**正文不出现引用标记**，信源全部集中在本清单；清单与 `sources.json` 序号一致。

## 与 feasibility-decomposition 的区别

- 本技能：按章节模板产出**完整可研报告**（科研立项）。
- `feasibility-decomposition`：对标政策/标准做**可行性分析 + V 字模型拆解 + 四张清单**（数字化改革课题/奖项申报）。
- 二者可串联：拆解结论作为本报告输入。
