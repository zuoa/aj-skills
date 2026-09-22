# 五阶段案件工作流

## 何时使用

完整的“材料 → 挖掘 → 检索 → 起草 → 交付”任务默认使用本工作流。单独读专利、审校、已有正文转 Word 等局部任务复用已有材料，不要求补跑全部阶段。已有案件先执行 `status` 恢复，不重新初始化。

主动挖掘同时遵循 [主动发散与推荐](proactive_mining.md)。新案件的 mining 阶段默认生成问题重述、前提检查、机会卡和推荐；用户只核对事实和选择，不负责独自想出创新点。未确认阶段也可以先提交并讨论机会卡，blocked 仅阻止正式采用与导出。

阶段 JSON 是每阶段内容的唯一编辑来源；确认页、总览和版本快照由脚本生成，不能手工维护第二套事实表。代理填写 JSON、展示确认页并归纳当前一问，用户不需要理解 JSON 或自行对照多份文档。

## 目录与入口

案件必须位于 skill 安装目录之外，例如用户项目中的 `outputs/某案件/`。以下 `SKILL_DIR` 和 `CASE_DIR` 应设为实际绝对路径；命令可从任何目录调用。

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" init --title "案件名称"
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" status
```

初始化产生：

```text
某案件/
├── REVIEW.md                  # 用户入口：进度、当前阶段、确认页链接
├── drafts/                    # 代理编辑各阶段内容；不写用户确认结果
│   ├── facts.json
│   ├── mining.json
│   ├── search.json
│   ├── basis.json
│   └── delivery.json
├── reviews/                   # 自动生成的中文确认页，不要求用户读 JSON
├── workflow/
│   ├── state.json             # 版本、确认依据和事件历史
│   └── revisions/             # 提交时创建的各版本不可覆盖快照
├── materials/                 # 本案使用的必要材料副本，按需建立
└── deliverables/              # 正文、Word、附图与质量报告，导出时建立
```

不自动复制全部项目、密钥或第三方目录。将本案真正使用的文件放到 `materials/` 并记录原项目路径与版本。`file` 来源按内容哈希追踪；URL 和对话来源保存定位及版本说明，不声称脚本已核验网页或发言人身份。

## 阶段契约

每阶段都有 `summary`（本轮结论）、`decision`（具体待核对取舍）、`next_question`（当前一问）、`gaps`（缺口与处置）。每个缺口包括 `id/question/status/blocking`；`status` 为 `open/resolved/excluded`，后两者需 `resolution`。开放的阻断缺口会阻止确认；仍有非阻断问题时填写下一问。

| 阶段 | 标准内容 | 进入下一阶段的条件 |
|---|---|---|
| facts | 来源、带状态的事实、问题—输入—处理—输出—效果链 | 来源定位完整，关键事实冲突有处置，用户具体事实或既有材料已核对 |
| mining | 候选卡、必要特征及事实引用、机理、效果、取舍、选定主线 | 主线有可采用事实支撑，认可建议不能冒充已实现 |
| search | 检索记录、文献、单一文献逐项对比、区别、反向检索、结论边界 | 关键特征对照完整；无能力检索时仅允许待检索候选并说明原因 |
| basis | 选定主线、技术问题与发明目的、效果依据、实施例、保护点支撑矩阵、结构化交底输入文件 | 与检索阶段一致、必要特征全部有支撑、输入无未解决假设 |
| delivery | Word、Markdown、附图、质量报告及起草依据版本 | 文件齐全且内容哈希对应、质量校验通过，随后审阅具体文件 |

材料可以先探索或准备，不需要等待无关问题；但正式确认不能跳过前置阶段。阶段不等于固定聊天轮数：每轮仍按访谈协议问一个关键问题。同一回复明确核对了多个阶段，可以依次记录同一会话依据，无需重复问。

## 字段填写

初始化从 `assets/workflow/` 复制空模板；空模板不能通过。阶段编号与字段见各 JSON；额外约束如下：

- `facts.sources[]`：`id/kind/locator/version`；`kind=file` 还需案件相对 `path`，`conversation/url` 需在 locator 给具体会话轮次或 URL/段落，不伪造定位。`facts[]` 的 `source_ids` 引用来源 ID，状态为 `source-backed/user-confirmed/inferred/proposal/unknown`。
- `mining.candidates[]`：`id/problem/mechanism/effect/tradeoff/status/features`；特征为 `id/description/fact_ids`。`core/dependent` 只能引用 `source-backed/user-confirmed` 事实；其他状态为 `rejected/proposal`。选定候选必须为 core。新案件还需填写 `exploration`，字段及 evidence/hypothesis/proposal 的转换规则见 [主动挖掘字段](proactive_mining.md)。只讨论设想时可以先提交被阻断的探索版本，不制造 core 候选通过检查。
- `search` 的 `mode=executed` 时：`queries[]` 为 `query/database/searched_at/result`；`documents[]` 为 `id/publication/date/url/scope`；核心文献 scope 必须为 `full-text/claims`；`comparisons[]` 为 `document_id/feature_id/finding/locator`，至少一个文献覆盖全部必要特征；`reverse_queries[]` 为 `query/result/implication`。`differences` 写具体区别，`conclusion` 为 `preliminary-candidate/high-risk/rejected`。记录真实检索，不为填表制造文献。
- 无检索能力时用 `mode=unavailable`，补 `reason`，结论只能为 `pending-search`，并写 `limitations`。这是明确保留证据缺口，不等于查新通过；有能力且任务要求检索时不能使用此例外偷跳流程。
- `basis.effects[]` 状态为 `measured/mechanism`；`embodiments[]` 为 `id/input/steps/output`；`support[]` 为 `feature_id/section/embodiment_id/source_ids`。`disclosure_file` 是案件内的 JSON 路径，字段格式沿用 `assets/examples/disclosure_input.sample.json`，不能复制示例的事实和数字到真实案件。其中 `invention.technical_problem` 和 `invention.purpose` 分别填写技术不足与要达到的技术目标，不能用一个替代另一个。起草依据提交会从已绑定的交底输入提取两者，保存为该版本的确认页预览，无需在 basis JSON 重复填写。目的变化后需重提起草依据、核对新版本。模型需核对实际正文与支撑矩阵的含义对应，脚本不能替代语义审查。
- `delivery` 正常由 `export` 自动生成。手动提交也必须提供文件、对应输入/输出哈希的质量报告和当前 `basis_digest`，不能把其他案件的报告套过来。

## 提交、展示、确认

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" submit facts
# 默认读取 drafts/facts.json；其他阶段同理，可用 --input 指定 JSON。
```

提交后打开 `REVIEW.md` 或当前 `reviews/facts.md`，直接给用户简短结论、取舍、当前一问和可点击文件链接。详情是中文条目，不让用户处理 JSON。提交有错误时仍保留快照和阻断原因，命令返回 2；修复后重新提交形成新版本。

只有用户已实际确认所展示内容，或本会话已有明确适用的授权，才运行：

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" confirm facts \
  --digest "确认页展示的完整摘要" \
  --actor "实际确认人" \
  --quote "用户明确核对该内容的原话" \
  --reference "实际会话轮次或记录定位" \
  --mode user
```

用户明确授权代选或一次成稿时，可用 `--mode delegated` 记录其授权原话与范围，不强迫额外仪式性确认。不得自行编造确认人、回答或会话定位，不能用本 skill 的规则代替用户授权。脚本检查确认信息齐全并绑定版本，不能证明是谁说的，也不能验证发明事实真假。

事实澄清采用开放追问，策略选择提供有依据的推荐。确认可以针对已逐项核对的内容复用既有回答；“继续分析”或沉默不能当成承认新的技术事实。存在关键缺口时可继续调查或提供审阅草案，不能靠 delegated 绕过机器阻断。

## 导出与最终审阅

确认前四阶段后：

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --case-dir "$CASE_DIR" export \
  --output deliverables/交底书_v1.docx
```

命令复用现有 Word/附图生成器，生成 Markdown、DOCX、全部附图、含输入与导出内容覆盖矩阵的 `.quality.json`，自动提交 delivery 阶段并产生交付确认页。工具成功只表示可供审阅，不自动宣称用户已验收。已确认依据后直接出图、导出，无需再询问工具执行许可。

`generate_docx.py` 增加 `--workflow-case`；即使省略该参数，输入文件位于含 `workflow/state.json` 的案件下时也自动核对阶段。单独转 Word 且未建立本工作流的既有输入保持兼容。工作流不提供任意跳过确认或无视错误的开关。

## 修改与恢复

- 每次恢复或交付前执行 `status`，检查文件哈希和上游状态，同时刷新确认页。
- 编辑 `drafts/<stage>.json` 后重新 submit；先前快照和确认事件保留。下游标为过期，不能沿用旧确认直接导出。按新证据更新并重新提交受影响阶段，再核对变化；不要删除旧版本。
- 只改起草标题或措辞：更新起草输入并重提 basis，只影响 basis/delivery，不要求重做事实和检索。
- 改核心机制：从 facts 或 mining 中最早受影响处更新，重评后续内容；脚本保守地使该阶段所有下游失效，不擅自猜哪些科学结论仍有效。
- 原始材料、起草输入、已交付文件或快照被外部改写时，状态变为 tampered；含义是哈希变化/不可用，未必是恶意。查明变化后重新提交相应阶段，不能只手改 state 清除状态。
- 版本快照不覆盖，输出不覆盖；新稿使用新版本文件名。正在进行的修改有本地锁，不支持多个进程同时更新同一案件。

## 工具检查的边界

结构化完整、引用成立、版本确认和产物哈希匹配，可以自动检查。材料是否真实、技术链是否可实施、文献是否真的披露该特征以及法律判断，仍需代理与用户逐项核验。所有中文确认页都应表达这些边界；不能将“confirmed”解释为专利可授权。
