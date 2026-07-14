# aj-patent-disclosure-cn

面向软件、互联网、人工智能、大数据、区块链、物联网和网络安全方案的中国发明专利技术交底书 skill。

它把输出质量放在“候选点数量”和“稿件长度”之前，重点控制：

- 事实、推断、待确认项和研发建议不混写；
- 技术问题—技术手段—技术效果形成因果闭环；
- 方案达到本领域技术人员可以实施的披露程度；
- 检索结果和法律判断有可追溯证据，不使用虚假相似度或授权概率；
- AI/算法方案写清结构、训练、参数及输入输出与具体场景的内在关系；
- 正文、实施例、附图和拟保护主题保持一致。

## 目录

```text
aj-patent-disclosure-cn/
├── SKILL.md
├── QUICK_START.md
├── templates/
│   ├── drafting_quality_standard.md
│   ├── patent_mining_strategy.md
│   ├── search_and_evidence.md
│   ├── tech_field_config.md
│   └── cnipa-reference.docx
├── scripts/
│   ├── validate_disclosure.py
│   ├── generate_docx.py
│   ├── generate_figures.py
│   ├── check_dependencies.py
│   └── setup_env.sh
├── examples/
│   └── disclosure_input.sample.json
└── evals/
    └── evals.json
```

## 典型任务

- 从访谈或需求文档挖掘核心专利构思；
- 生成完整技术交底书草案；
- 审校现有交底书的充分公开、支持性和一致性；
- 制定检索式并完成特征对照和创造性初步分析；
- 规划专利附图和拟保护主题；
- 将结构化 JSON 校验并导出为 DOCX。

skill 会先路由任务。纯文本起草、审校或检索方案不需要初始化 Python 环境；只有实际运行脚本且依赖缺失时才创建本地 `.venv`。

## 高质量工作流

1. 提取已知事实并标注证据状态；
2. 建立“问题 → 输入 → 处理 → 输出 → 效果”技术链；
3. 区分核心构思、从属特征、分案候选和研发建议；
4. 需要时执行现有技术检索和单文献特征对照；
5. 按充分公开标准起草正文和端到端实施例；
6. 建立拟保护主题—正文—实施例—附图支撑矩阵；
7. 运行结构化校验，再生成 DOCX；
8. 复核事实、技术性、充分公开、支持性和全文一致性。

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
  --word-only
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

## 检索边界

- 不把“最近 10 年”当成法定现有技术范围；
- 不用文本相似度百分比判断新颖性或创造性；
- 没有实际检索时明确写“未执行外部检索”；
- 不编造公开号、申请人、日期、引文或授权概率；
- 新颖性按单一文献逐项对照，创造性按最接近现有技术、区别特征、实际技术问题和技术启示分析。

## 说明

本 skill 生成的是技术交底书或申请文件草案，不是法律意见，也不保证授权。正式申请前请注意保密，并由专利代理师结合完整检索、申请策略和最新规则复核。
