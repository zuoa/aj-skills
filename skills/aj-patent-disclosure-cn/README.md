# aj-patent-disclosure-cn

面向软件、互联网、人工智能、大数据、区块链、物联网和网络安全方案的证据驱动型中国发明专利 skill。它能从项目文档、代码和 Office 材料挖掘专利点，也能解读已有专利、检索现有技术、生成交底书并维护修订历史。

它把输出质量放在“候选点数量”和“稿件长度”之前，重点控制：

- 事实、推断、待确认项和研发建议不混写；
- 项目文档、代码、Word/PPT 和测试记录均保留来源定位与版本；
- 技术问题—技术手段—技术效果形成因果闭环；
- 方案达到本领域技术人员可以实施的披露程度；
- 已有专利按权利要求树、说明书段落和附图做证据化解读；
- 联网检索相似专利，通过特征对比和区别特征反向检索筛选创新点；
- 检索结果和法律判断有可追溯证据，不使用虚假相似度或授权概率；
- AI/算法方案写清结构、训练、参数及输入输出与具体场景的内在关系；
- 正文、实施例、附图和拟保护主题保持一致；
- 已有交底书采用非破坏性修订，旧稿、哈希和影响分析可追溯；
- 脱敏不以牺牲技术可实施性为代价。

## 目录

```text
aj-patent-disclosure-cn/
├── SKILL.md
├── QUICK_START.md
├── THIRD_PARTY_NOTICES.md
├── docs/
│   └── upstream_fusion_analysis.md
├── templates/
│   ├── drafting_quality_standard.md
│   ├── patent_mining_strategy.md
│   ├── patent_reading_and_claim_mapping.md
│   ├── project_material_intake.md
│   ├── revision_and_redaction.md
│   ├── search_and_evidence.md
│   ├── tech_field_config.md
│   └── cnipa-reference.docx
├── scripts/
│   ├── validate_disclosure.py
│   ├── generate_docx.py
│   ├── generate_figures.py
│   ├── office_to_markdown.py
│   ├── revision_log.py
│   ├── check_dependencies.py
│   └── setup_env.sh
├── examples/
│   └── disclosure_input.sample.json
└── evals/
    └── evals.json
```

## 典型任务

- 从访谈或需求文档挖掘核心专利构思；
- 扫描项目目录、实现代码、Word/PPT 和测试记录并建立证据清单；
- 把已有专利读成权利要求树、独立权特征表和说明书—附图支撑表；
- 生成完整技术交底书草案；
- 审校现有交底书的充分公开、支持性和一致性；
- 在旧稿上补材料或纠错，另存新版本并记录修订影响；
- 制定检索式并完成特征对照和创造性初步分析；
- 规划专利附图和拟保护主题；
- 将结构化 JSON 校验并导出为 DOCX。

skill 会先路由任务。纯文本起草、审校或检索方案不需要初始化 Python 环境；只有实际运行脚本且依赖缺失时才创建本地 `.venv`。

## 高质量工作流

1. 固定项目/材料版本并建立来源清单；
2. 提取已知事实，标注证据状态和定位；
3. 必要时对已有专利建立权利要求树和全文证据映射；
4. 建立“问题 → 输入 → 处理 → 输出 → 效果”技术链；
5. 形成核心构思、从属特征和分案方向的待检索候选；
6. 联网查找相似专利，完成单一文献特征对照；
7. 提取区别特征，围绕“区别特征 + 功能关系 + 技术效果”反向检索；
8. 淘汰、收缩或重组候选，形成有证据边界的初步创新点；
9. 按充分公开标准起草正文和端到端实施例；
10. 建立拟保护主题—正文—实施例—附图支撑矩阵；
11. 运行结构化校验，生成 Markdown、DOCX 和附图；
12. 修订时保留旧稿，记录哈希、影响范围和新版本。

## 项目与 Office 材料

`.docx`、`.pptx` 和 `.ppsx` 可用零新增依赖的转换器提取为 Markdown：

```bash
python3 scripts/office_to_markdown.py \
  docs/design.docx docs/review.pptx \
  --output-dir outputs/materials \
  --manifest outputs/materials/office_manifest.json
```

转换稿用于扫描和证据定位，不保证版式还原，也不会执行宏、外部链接或嵌入对象。

## 结构化校验

从本目录执行：

```bash
python3 scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json
```

终稿检查会拒绝未解决占位符、缺少步骤级方案或缺少结构化实施例的输入；量化效果没有测试条件、基线或来源时也会报错：

```bash
python3 scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json \
  --final
```

机器可读报告：

```bash
python3 scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json \
  --final \
  --json
```

## DOCX 生成

依赖已满足时直接运行：

```bash
python3 scripts/generate_docx.py \
  --input examples/disclosure_input.sample.json \
  --output outputs/交底书_示例_v1.0.docx \
  --with-markdown
```

同一输入和模板对应的哈希未变化时会跳过重复生成。内容变化时使用新版本文件名，或在明确需要覆盖时增加 `--overwrite`。

若 Python 依赖缺失，再执行：

```bash
bash scripts/setup_env.sh
./.venv/bin/python scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json \
  --final
```

`setup_env.sh` 默认使用清华 PyPI 镜像，可通过 `PIP_INDEX_URL` 覆盖。系统仍需安装 `pandoc` 才能生成 Word。严格模式默认使用 `templates/cnipa-reference.docx`；该文件是固定参考模板，不代表已满足某个代理机构的全部版式要求。

## 附图

先确认附图清单、图元和术语，再运行程序化脚本：

```bash
python3 scripts/generate_figures.py \
  --input-json examples/disclosure_input.sample.json \
  --output-dir outputs/figures \
  --timeout-sec 90
```

`--input-json` 必须包含已确认的 `figure_plan`，或至少包含可转换为顺序流程图的 `invention.solution_steps`。只有显式使用 `--demo` 才会生成通用示意图，通用示意图不得用于真实交底书。程序化框图/流程图是默认路径，便于复现和核对；脚本同时保留 Mermaid 或 PlantUML 源文件。生成失败时保留源文件和错误说明。生成式图片仅适合经人工逐项核对的概念图，不应作为自动默认值。

## 修订与版本留痕

已有交底书补充或纠错时，默认另存新版本。交付后可记录基线和新文件哈希：

```bash
python3 scripts/revision_log.py \
  --case-dir outputs/某案件 \
  --kind correction \
  --base outputs/某案件/交底书_v1.md \
  --artifact outputs/某案件/交底书_v2.md \
  --artifact outputs/某案件/交底书_v2.docx \
  --changed-section "具体实施方式" \
  --summary "纠正阈值来源并同步支撑矩阵"
```

脚本追加 `revision_history.md` 和 `revision_history.jsonl`，不覆盖旧记录。

## 检索边界

- 不把“最近 10 年”当成法定现有技术范围；
- 不用文本相似度百分比判断新颖性或创造性；
- 没有实际检索时明确写“未执行外部检索”；
- 不编造公开号、申请人、日期、引文或授权概率；
- 新颖性按单一文献逐项对照，创造性按最接近现有技术、区别特征、实际技术问题和技术启示分析。
- 区别特征不自动等于创新点；需要继续反向检索其功能关系和技术效果，并记录方案支撑、命中文献、风险与置信度。
- 没有实际联网检索时，只能输出“待检索创新候选”，不能宣称已经找到具有新颖性或创造性的创新点。

## 说明

本 skill 生成的是技术交底书或申请文件草案，不是法律意见，也不保证授权。正式申请前请注意保密，并由专利代理师结合完整检索、申请策略和最新规则复核。

本次增强参考并重构了 MIT 许可项目 [`handsomestWei/patent-disclosure-skill`](https://github.com/handsomestWei/patent-disclosure-skill) 的项目扫描、迭代和专利解读思路。具体取舍见 [docs/upstream_fusion_analysis.md](docs/upstream_fusion_analysis.md)，许可与来源见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
