# 快速开始

本文命令以 skill 根目录为工作目录（仓库中为 `skills/aj-patent-disclosure-cn/`，不是本文所在目录）。请先将 `PATENT_CASE_DIR` 设置为 skill 外的用户项目绝对路径，例如 `export PATENT_CASE_DIR="/绝对路径/你的项目"`；材料和产物均放在该项目内。

## 完整案件：阶段化入口

让代理先设置 `SKILL_DIR`（skill 绝对路径）与 `CASE_DIR`（用户项目下案件绝对路径），然后执行：

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" init --title "案件名称"
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" status
```

你只需审阅自动生成的 `REVIEW.md` 和当前阶段确认页，并回答关键问题。代理负责填充事实、候选、检索、起草依据和交付 JSON，通过 `submit` 提交版本，依据你的真实回复运行 `confirm`。前四阶段确认后执行 `export`，自动生成 Word、Markdown、附图和质量报告。具体命令、字段和回退规则见 [五阶段工作流](../../skills/aj-patent-disclosure-cn/references/staged_workflow.md)。

中断后执行 `status` 恢复。新证据改变技术方案时重提受影响阶段，旧确认和稿件保留；不要重新初始化。单独转 Word、审校或读专利仍可直接使用下列局部命令。

## 让代理主动给方向

主动挖掘已是默认行为，也可以这样强调：

```text
我的初始方案只是起点，请主动找盲点和其他技术路线。
先查材料，给我少量有区别的选项、推荐理由、代价和最小验证办法。
区分已有事实、待核实线索和新设计建议；不要把研发建议写成已实现功能。
```

新案件的挖掘确认页自动包含机会卡与推荐。只有研发设想、尚无可采用主线时，也能先展示建议并继续调查，不能为了推进流程编造核心候选。

## 1. 直接调用

信息较完整时：

```text
使用 aj-patent-disclosure-cn，根据下面方案生成中国发明专利技术交底书草案。
请区分已确认事实、推断和待确认项；不要编造检索结果或实验数据。

技术场景：...
现有方案和不足：...
输入/处理对象：...
核心步骤或模块关系：...
输出：...
区别特征：...
技术效果及证据：...
希望保护的主题：...
```

信息很少时可以只给现有想法。skill 会先问一个关键问题，根据回答逐轮挖掘；先核对保护主线，再核对起草依据，之后完成正文、附图和 Word。已确认内容不重复问，纯格式转换不启动访谈。

默认不用额外安装 grill-me。也可以明确指定：

```text
请按发明访谈方式跟我共同挖掘：先读材料，每次问一个关键问题。不要把建议写成既有事实；选保护主线和开始写完整稿前，拿出具体内容让我核对。
```

若希望减少交互，可说“按已有材料一次成稿，代我选择主线”。必要技术事实仍不能由模型编造；材料不足时得到的是审阅草案和缺口报告。

有项目目录或材料时：

```text
请扫描这个项目中的设计文档、核心代码、Word/PPT 和测试记录，先建立“技术事实—来源定位—版本—拟保护特征”证据清单，再挖掘专利点。忽略第三方依赖、生成文件和无关资源，不要读取或回显密钥。
```

## 2. 只做某个环节

```text
只做专利点挖掘，先不要写交底书。
```

```text
请联网检索与本方案相关的现有专利：先形成必要技术特征表，查找最接近现有技术，逐项对比并提取区别特征；再围绕“区别特征 + 功能关系 + 技术效果”反向检索，筛选有事实支撑的初步创新点。每个结论都给出公开号、日期、证据位置和来源链接；没有实际检索时明确说明，不要编造结果。
```

```text
审校这份交底书的充分公开、支持性、术语一致性和AI方案披露风险。
```

```text
只制定检索式和特征对照表；没有实际检索能力时不要给专利号。
```

```text
基于已确认正文规划附图，不改动技术内容。
```

```text
请解读这份专利 PDF：核对文本版本，建立权利要求树，逐项写清从属权相对父权新增了什么，并把独立权特征映射到说明书段落和附图。只拿到摘要时明确证据不足，不要把摘要当全文。
```

```text
在上一版交底书上补充这份测试报告。保留旧稿，另存新版本；同步检查技术效果、实施例、支撑矩阵、附图和检索结论，并生成修订记录。
```

## 3. 转换 Office 材料

```bash
python3 scripts/office_to_markdown.py \
  "${PATENT_CASE_DIR}/docs/design.docx" "${PATENT_CASE_DIR}/docs/review.pptx" \
  --output-dir "${PATENT_CASE_DIR}/outputs/materials" \
  --manifest "${PATENT_CASE_DIR}/outputs/materials/office_manifest.json"
```

转换稿用于内部扫描和证据定位，不保证原版式还原。

## 4. 结构化输入校验

```bash
python3 scripts/validate_disclosure.py \
  --input assets/examples/disclosure_input.sample.json
```

独立终稿检查（先生成图片并填写 `figures.file`；示例尚未出图时不会通过。默认导出命令会自动完成出图和校验）：

```bash
python3 scripts/validate_disclosure.py \
  --input <已填写真实附图路径的输入.json> \
  --final
```

## 5. 生成 Markdown + Word

依赖可用时直接执行：

```bash
python3 scripts/generate_docx.py \
  --input assets/examples/disclosure_input.sample.json \
  --output "${PATENT_CASE_DIR}/outputs/交底书_示例_v1.0.docx" \
  --with-markdown
```

只有出现缺少依赖的错误时，才初始化本地环境：

```bash
bash scripts/setup_env.sh
./.venv/bin/python scripts/generate_docx.py \
  --input assets/examples/disclosure_input.sample.json \
  --output "${PATENT_CASE_DIR}/outputs/交底书_示例_v1.0.docx" \
  --with-markdown
```

## 6. 修订留痕

```bash
python3 scripts/revision_log.py \
  --case-dir "${PATENT_CASE_DIR}/outputs/某案件" \
  --kind supplement \
  --base "${PATENT_CASE_DIR}/outputs/某案件/交底书_v1.md" \
  --artifact "${PATENT_CASE_DIR}/outputs/某案件/交底书_v2.md" \
  --artifact "${PATENT_CASE_DIR}/outputs/某案件/交底书_v2.docx" \
  --changed-section "实施例1" \
  --summary "补充异常回退路径并同步附图"
```

## 7. 关键原则

- 专利点来自已披露技术因果链，不靠堆叠流行技术名词；
- 研发建议与已经实现的发明事实分开；
- 量化效果必须有测试条件、基线或来源；
- 新颖性不按多篇文献拼接，也不按文本相似度判断；
- 区别特征不直接等于创新点，必须经过相似专利对比、反向检索和技术效果验证；
- 项目代码、测试和 Office 材料中的关键事实应保留版本与来源定位；
- 已有专利解读必须区分全文、部分全文、仅摘要和待核验；
- 修改已有交底书默认保留旧稿并传播检查所有受影响章节；
- 脱敏不能删除使方案可实施或支撑保护范围的关键技术细节；
- AI/算法方案要披露模型/算法与具体场景的内在关系；
- DOCX、附图和检索不是每次调用都必须执行，按任务需要生成。

## 完整终稿与附图一并交付

从任意工作目录调用 `scripts/generate_docx.py --input <input.json> --output <新版本.docx> --with-markdown`（脚本路径按所在目录调整）。先按 [正式稿格式](../../skills/aj-patent-disclosure-cn/references/disclosure_format.md) 完成内容，再按 [附图输入规范](../../skills/aj-patent-disclosure-cn/references/figure_workflow.md) 登记所有附图。命令自动绘图、嵌图、执行终稿校验并导出。需要 Graphviz 的 `dot` 命令；缺图或缺依赖时失败，不用占位图冒充完成。

正式交底书不含假设、待确认项、内部证据状态、检索工作清单和摘要草案。内部材料留在 JSON 或 reports/；关键事实缺口应先补齐，不能隐藏后当作终稿。

默认模板已切换为用户提供的 `assets/templates/技术交底书模板.docx`。原模板中的机器人示例和填写提示不会进入正式稿。新增 `verification` 用于真实验证情况；`department`、`first_inventor_id` 为可选行政字段，缺失留空。

## 发明目的字段

交底输入分别填写 `invention.technical_problem`（现有技术的具体不足）和 `invention.purpose`（针对不足要达到的技术目标）。正文在技术问题之后、技术方案之前单列“发明目的”；起草依据确认页自动展示同一输入中的两项内容。旧输入缺少 purpose 时，草稿校验提示警告，起草依据确认及终稿导出会要求补齐，不再以技术问题替代。

## 最终覆盖校验与标题层级

导出默认生成 `.quality.json`，同时检查输入完整性、Markdown/Word 对应章节的内容保留和实际附图嵌入；检查失败不视为终稿。Word 主章、小节和步骤小标题分别采用 14/12/11 pt 加粗，正文保持 10.5 pt，段内“输入、处理、输出”等标签也加粗。

可用 `scripts/check_output_coverage.py --input <JSON> --markdown <MD> --docx <DOCX> --report <报告JSON>` 独立复查。完整规则见 [交底书格式与校验](../../skills/aj-patent-disclosure-cn/references/disclosure_format.md)。
