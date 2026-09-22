# 专利撰写 skills 调研与本轮迭代

调研日期：2026-09-22。范围：公开 GitHub 项目的实际 SKILL.md、相关仓库说明及 CNIPA 官方规则。以下评价是本地适配判断，不是这些项目的运行效果排名。未安装或执行第三方 skill；没有用星标、目录收录或作者自评代替质量证据。链接指向本次读取的分支文本，远端后续可能变化。

## 现状与选择

本地版本已经具备分轮访谈、主动挖掘、事实状态、单文献对比、区别特征反向检索、五阶段状态、附图与 Word 导出、覆盖校验及非破坏性修订。继续增加全流程清单的收益有限。本轮优先补齐保护结构与文献/申请状态边界，保留当前工作区已有改动。

## 六个直接来源

| 来源 | 观察到的做法 | 本地差距与取舍 |
|---|---|---|
| [Yulivu/debuffer-skills：claims-drafting](https://github.com/Yulivu/debuffer-skills/blob/master/skills/library/patent/claims-drafting/SKILL.md) | 独立与从属权项、退守位置、说明书映射、审阅修正循环 | 采用有证据的保护骨架、退守路径及逐项反查；不采用固定数量、跨法域格式硬套、专利性评分或指定外部模型依赖。 |
| [snipp-zha/Paper-to-patent-Skill](https://github.com/snipp-zha/Paper-to-patent-Skill/blob/main/SKILL.md) | 论文正文、公式、图和代码分源编号；特征映射；关注公式表达与图文一致 | 采用论文证据清单、公式/图表核对；复用本地证据 ID，不复制其状态系统。可编辑公式要求仅在实际工具验证后承诺。 |
| [VinceZcrikl/vinceZcrikl-skills：patent-builder](https://github.com/VinceZcrikl/vinceZcrikl-skills/blob/main/skills/patent-builder/SKILL.md) | 既有实现、初始构思、开放挖掘、已有交底反查四类入口 | 挖掘已有覆盖；新增需求对旧案反查，但明确“有披露”不等于“有授权保护”，已提交案件不能随意补充。 |
| [yjmm10/patent-skills](https://github.com/yjmm10/patent-skills/blob/master/SKILL.md) | 分模式组织审核、转换、检索、起草、迭代、导出及可选升级 | 按需加载与本地结构一致。保持交底书默认边界，不因输入论文自动升级整套申请书，不增加爬虫依赖。 |
| [sunjixin2023/patent-writing](https://github.com/sunjixin2023/patent-writing/blob/main/SKILL.md) | 强调公式解释、参数依据、步骤衔接与实施细节 | 本地已具备大部分质量要求；不采用约 800 行、固定章节比例、固定权项和实施例数量。 |
| [ichen-dev/patent-writing-skill](https://github.com/ichen-dev/patent-writing-skill/blob/main/SKILL.md) | 企业模板、实际流程图及自动 Word 交付 | 本地已有对应能力；保留用户现有模板，不移植其企业格式、安装流程或要求所有任务走完全部阶段。 |

上述内容仅用于设计比较，新增指令均按本地流程自行编写；本轮未复制第三方脚本、模板或大段指令。既有第三方许可声明保持不变。

## 官方规则交叉核对

外部 skill 的规则不能直接作为法律依据。本轮特别核对：

- [专利法第二十二、二十四、二十六、三十三条](https://www.cnipa.gov.cn/art/2020/11/23/art_97_155167.html)：文献时间、特殊公开情形、披露支持与申请修改边界。
- [2023 年修订实施细则第二十三至二十五条](https://www.cnipa.gov.cn/art/2023/12/21/art_98_189197.html)：必要特征、独立权项表达与从属引用。两部式存在适用例外；中国多项从属的引用规则不能遗漏。
- [第 84 号局令](https://www.cnipa.gov.cn/art/2025/11/13/art_99_202568.html)及[官方修改说明](https://www.cnipa.gov.cn/art/2025/11/13/art_66_202561.html)：2026-01-01 起施行的修改；本地已有 AI 充分公开与技术贡献规则，不重复堆叠。

此次核验针对上述具体条款，不宣称全面排查了所有程序规则及地方实践。

## 已落实的改进

| 改进 | 具体行为 | 文件 |
|---|---|---|
| 保护骨架与退守 | 必要限定删除检查、从属继承、互斥方案、实施主体、引用基础和范围代价 | [claim_strategy.md](../../skills/aj-patent-disclosure-cn/references/claim_strategy.md) |
| 论文证据化转换 | 正文/公式/图表定位，公开时间、实现和实验状态分开 | [paper_to_disclosure.md](../../skills/aj-patent-disclosure-cn/references/paper_to_disclosure.md) |
| 新需求覆盖反查 | 逐案检查完整组合；披露、权项、授权版本分开，禁止跨案拼接覆盖结论 | [disclosure_coverage.md](../../skills/aj-patent-disclosure-cn/references/disclosure_coverage.md) |
| 申请后修改边界 | 工作副本基线与原始提交基线分开；新增内容查原始依据 | [revision_and_redaction.md](../../skills/aj-patent-disclosure-cn/references/revision_and_redaction.md) |
| 检索时间线 | 实际公开、申请与优先权分开；抵触申请单列，自有公开不自动排除 | [search_and_evidence.md](../../skills/aj-patent-disclosure-cn/references/search_and_evidence.md) |
| 访谈一致性 | 移除材料扫描参考中一次提问 3–5 组的旧指令，统一分轮推进 | [project_material_intake.md](../../skills/aj-patent-disclosure-cn/references/project_material_intake.md) |

入口新增按需路由，质量标准链接专项参考；不增加工作流阶段、强制确认、JSON 必填字段或软件依赖。新专项报告使用既有 `reports/` 约定。

## 验证方法与边界

在 [evals.json](../../skills/aj-patent-disclosure-cn/evals/evals.json) 增加可独立阅读的情景：已提交后补技术、六个月内自有论文、跨案覆盖、从属引用错误、抵触申请、保护骨架和论文公式缺口。每项都给出具体输入与可观察的预期行为，不以出现某个标题或关键词作为通过条件。

结构校验、引用检查与已有 Python 回归测试用于确认资源完整性及现有工具兼容。新增情景需要另行实际模型执行；本轮不把新增用例数量或静态审阅称为行为通过率，也不报告质量提升百分比。

本次实际执行结果：

- `quick_validate.py skills/aj-patent-disclosure-cn`：通过。
- `python3 -m unittest discover -s skills/aj-patent-disclosure-cn/tests -v`：37 项全部通过，含工作流、附图及 DOCX 导出回归。
- `git diff --check`、主入口/参考文件/本报告的本地链接检查、评估 JSON 与 ID 唯一性检查：通过。
- 新增行为情景 7 项，总计 26 项；未运行模型行为评估。

## 暂缓项

- 可编辑公式批量转换：需要公式提取、Office Math 生成与实际页面视觉验证，本轮未实现转换器。
- 完整申请书五件套与提交：与当前交底书默认范围不同，未借本轮调研扩大交付承诺。
- FTO、侵权及授权后修改程序：只明确边界，没有冒充完成专项法律审查。
- 外部模型评分和爬虫：未引入，避免把模型打分包装成授权概率或增加无关运行依赖。
