# outputs/（说明）

**运行时产物不写在这里。** 本目录只是结构占位，不要把报告产物写进 skill 目录。

- 所有产物写入**用户当前工作目录**下的 `outputs/`（即运行命令时所在的目录）。
- 脚本用 `{baseDir}/scripts/...` 调用；`--input/--output/--sources/--output-dir/--report/--manifest` 等参数相对当前工作目录解析。
- 完整产物树见 `SKILL.md` 的「输出契约」。

典型结构（在工作目录下生成）：

```text
outputs/
├── project_brief.md                 # Stage 0 事实底稿
├── outline.md                       # Stage 1 大纲
├── intake/                          # Stage 0 Office 转换稿（office_manifest.json + *.md）
├── research/
│   ├── research_dossier.md          # Stage 2 调研底稿
│   └── sources.json                 # 机读信源
├── sections/                        # Stage 3 分章（01..06）
├── 可行性分析报告_[项目名]_v1.0.md/.docx/.sha256
├── 参考文献与信源清单.md             # ★ 独立信源清单（人工复核）
└── quality_report.json              # 五道门校验结果
```
