---
name: contract-review
description: 合同审核与审查报告技能。用户提到“审合同”“合同审核”“法务审查”“条款风险”“帮我看 NDA/保密协议/采购合同/服务协议/SaaS 协议/合作协议/授权许可/劳动或顾问合同”“按公司规定或模板比对”“输出红线、修改建议、签署意见、审查报告”时必须触发。支持整份合同、节选条款、条款比对、审查清单、风险台账和审查报告输出。凡是需要结合法律法规、监管要求、公司制度、审批权限、风险分级或签署建议来判断合同是否可签时，也应使用本技能。
---

# Contract Review

面向企业法务、采购、销售、运营、HR 与业务负责人场景的合同审核技能。

目标不是只做“找几个风险点”的泛泛点评，而是形成一套可复核的审查链路：
- 先定审查目标和适用标准
- 再拆条款和缺失项
- 再核对法律法规与公司规则
- 再形成风险分类、修改建议与签署意见

## 先读什么

- 用户未明确法域，且合同和沟通语言明显是中文商事场景时，先读 [references/prc-defaults.md](references/prc-defaults.md)。
- 先读 [references/source-hierarchy.md](references/source-hierarchy.md)，明确法源、监管、公司制度和市场惯例的层级。
- 再按合同类型读取 [references/clause-checklists.md](references/clause-checklists.md)，补齐常见条款检查点。
- 若为 NDA，追加读取 [references/prc-nda-redlines.md](references/prc-nda-redlines.md)。
- 若为采购合同，追加读取 [references/prc-procurement-redlines.md](references/prc-procurement-redlines.md)。
- 若为 SaaS 协议，追加读取 [references/prc-saas-redlines.md](references/prc-saas-redlines.md)。
- 若为服务协议，追加读取 [references/prc-service-redlines.md](references/prc-service-redlines.md)。
- 需要生成红线、替代条款或谈判口径时，读取 [references/standard-redlines.md](references/standard-redlines.md)。
- 需要直接产出可粘贴条款时，读取 [references/clause-templates.md](references/clause-templates.md)。
- 用户没有公司规则但希望建立内部红线时，读取 [references/company-redline-template.md](references/company-redline-template.md)。
- 进入风险识别时读取 [references/risk-taxonomy.md](references/risk-taxonomy.md)。
- 出最终报告前必须读取 [references/report-template.md](references/report-template.md)。

## 适用输入

- 合同全文或节选，直接粘贴到对话
- 本地文件路径，优先 `md`、`txt`、`html`
- 已提取文本的 `docx` / `pdf`
- 对比场景：用户给出“对方版本”和“我方模板/红线”
- 审查标准：公司制度、审批矩阵、交易政策、法务 playbook、标准模板

如果用户只给图片扫描件、不可复制 PDF 或零散截图：
- 先尽量提取结构化文本
- 提取失败时，明确说明无法可靠逐条审查，并要求可复制文本或关键条款摘录

## 默认设置

- 默认输出语言：`zh-CN`
- 默认模式：`standard`
- 默认风险口径：`balanced`
- 默认法域：`中国大陆`
- 默认输出目录：`contract-reviews/{slug}-{timestamp}/`
- 默认签署建议：只有在证据和关键条款足够时才给出；否则输出“需补充信息后判断”
- 默认审查标准顺序：
  1. 强制性法律法规与监管要求
  2. 用户提供的公司制度、审批规则、合同模板、红线清单
  3. 行业惯例与交易常识
  4. 本技能内置的通用检查清单

如果用户没有提供公司制度或模板：
- 继续完成通用审查
- 但必须明确标记“未按贵司内部制度校验”
- 可以使用内置标准红线作为通用企业立场起点
- 不得虚构内部政策、审批权限或红线

如果用户未说明法域，且合同属于中文企业交易场景：
- 默认按中国大陆商事合同口径审查
- 涉及数据、个人信息、跨境传输、商业秘密、劳动或顾问安排时，优先读取 [references/prc-defaults.md](references/prc-defaults.md)
- 最终报告里明确标记“本次默认以中国大陆法语境审查；如合同约定境外法或境外争议解决，需进一步复核”

## 审查模式

| 模式 | 适用场景 | 输出深度 |
|------|----------|----------|
| `quick` | 快速扫雷、只看显著问题、时间紧 | 高风险问题 + 关键修改建议 |
| `standard` | 默认模式，大多数合同审查 | 条款拆解 + 风险台账 + 审查报告 |
| `signing-gate` | 高金额、高监管、高争议风险或临近签署 | 强制核源 + 缺失项检查 + 签署建议 + 待确认问题 |

自动判断规则：
- 用户说“快速看一下”“先扫雷”“不用太细”时，用 `quick`
- 用户提到“马上签”“请给能不能签的结论”“按公司规定过一遍”时，至少用 `standard`
- 涉及数据出境、知识产权独占、排他、巨额违约责任、监管牌照、劳动用工、高金额采购、长期 SaaS 或重大合作时，升级到 `signing-gate`

## 五个 Agent 的职责

不要真的把它们写成互相脱节的五份答案，而是按这个顺序串行工作并把中间产物落盘。

### 1. Planner Agent

负责定义任务边界和审查口径。

至少确认：
- 合同类型
- 审查目标：合规、商业、采购、销售、交付、数据、IP、用工、签署把关
- 交易角色：我方 / 对方 / 中立
- 是否有我方模板、公司政策、审批矩阵、红线
- 是否要求出修改建议、替代条款、签署结论
- 时效要求与版本信息

输出到 `00-brief.md`。

### 2. Clause Agent

负责把合同拆成“可审查单元”，不要直接在大段正文里混着点评。

任务：
- 建立条款目录和 clause id
- 识别关键定义、权利义务、金额、期限、触发条件、例外、责任分配
- 标记缺失条款、冲突条款、模糊表述和空白变量
- 必要时把无编号合同切成 `C1`、`C2`、`C3` 形式

输出到 `01-document-map.md` 和 `02-clause-register.md`。

### 3. Law Agent

负责核对“依据”而不是凭经验下结论。

任务：
- 识别适用法域、行业监管、数据合规、反商业贿赂、出口管制、劳动用工等问题
- 检索并记录法律法规、监管规则、司法解释、用户提供的公司制度
- 对每条依据写清：来源级别、标题、发布日期/生效日期、与你的审查结论的关系
- 区分：
  - `违法/违规风险`
  - `违反公司制度或审批要求`
  - `市场惯例偏离`

在中国大陆法默认场景下：
- 先读 [references/prc-defaults.md](references/prc-defaults.md)
- 合同通用问题优先从《中华人民共和国民法典》合同编口径出发
- 涉及个人信息、数据处理、跨境传输时，优先核对 PIPL、DSL、现行网安法及国家网信办规则
- 涉及保密、竞业、技术资料、源码、客户名单时，额外注意商业秘密和反不正当竞争风险
- 涉及顾问、驻场、灵活用工时，额外注意被重定性为劳动关系或产生用工合规义务的风险

输出到 `03-authority-log.md`。

### 4. Risk Agent

负责把问题归类、定级、解释后果，并形成可执行的处理建议。

任务：
- 使用 [references/risk-taxonomy.md](references/risk-taxonomy.md) 的分类与级别
- 合并重复问题，避免同一风险在多个条款里重复记账
- 判断是“必须修改”“可谈判”“可接受但需知悉”“信息不足”
- 对每个问题给出：
  - 风险等级
  - 风险类别
  - 触发条款
  - 依据
  - 影响
  - 建议动作

输出到 `04-risk-register.md`。

### 5. Report Agent

负责把审查结论变成业务能直接使用的交付物。

任务：
- 用 [references/report-template.md](references/report-template.md) 生成终稿
- 输出执行摘要、关键风险、建议红线、待确认问题、签署建议
- 如果用户需要，额外生成“给业务的非法律语言摘要”

输出到 `05-redlines.md` 和 `06-review-report.md`。

## 输出文件

为每次任务创建目录：`contract-reviews/{slug}-{timestamp}/`

- `source.md`：统一落盘的合同文本或摘录
- `00-brief.md`：任务边界、合同类型、审查标准、版本信息
- `01-document-map.md`：合同元数据、结构总览、缺失项初筛
- `02-clause-register.md`：条款台账
- `03-authority-log.md`：法律法规、监管规则、公司制度、模板比对依据
- `04-risk-register.md`：风险台账
- `05-redlines.md`：建议修改方案或替代条款
- `06-review-report.md`：最终审查报告
- `07-open-questions.md`：信息不足或需业务确认的问题；只有在需要时生成

如果用户只要聊天窗口里的答案，仍然默认保存 `06-review-report.md`，并在回复里给出路径。

## 工作流

### Step 1: 建立审查任务，写入 `00-brief.md`

优先从当前对话中提取，不要为了默认项反复追问。至少写清：
- 合同名称与版本
- 合同类型
- 我方角色
- 目标法域或争议解决地
- 审查模式
- 是否有公司制度/模板/红线
- 是否要求替代条款
- 是否要求签署结论
- 当前资料缺口

如果用户没有说清合同类型，先根据条款内容推断为以下之一：
- `nda`
- `service`
- `procurement`
- `saas`
- `license-ip`
- `employment-consulting`
- `data-processing`
- `other`

### Step 2: 落盘正文并建立文档地图

1. 将用户提供的正文统一写入 `source.md`
2. 提取：
   - 合同名称
   - 签约主体
   - 定义条款
   - 商业条款
   - 责任条款
   - 争议解决条款
3. 写 `01-document-map.md`
4. 没有条款编号时，为每个可审查单元分配 `C1`、`C2` 等标识
5. 生成 `02-clause-register.md`

`02-clause-register.md` 建议列：

| Clause ID | 条款标题 | 摘要 | 问题类型 | 初步备注 |
|-----------|----------|------|----------|----------|

### Step 3: 依据检索与标准比对，写入 `03-authority-log.md`

执行原则：
- 先读 [references/source-hierarchy.md](references/source-hierarchy.md)
- 凡是和法律责任、合规义务、数据处理、牌照、劳动、知识产权归属、违约责任、争议解决直接相关的结论，都要给出处
- 时效敏感内容必须核对发布日期和生效日期
- 不能把“市场常见做法”写成“法律要求”
- 用户提供的公司制度、模板、审批权限表属于内部约束，必须单独标明

`03-authority-log.md` 建议列：

| Authority ID | 层级 | 名称 | 日期 | 适用点 | 备注 |
|--------------|------|------|------|--------|------|

### Step 4: 识别风险并写入 `04-risk-register.md`

执行顺序：
1. 逐条扫描 clause register
2. 用合同类型检查清单补查缺失项
3. 在中国大陆场景下，再读取对应合同类型的 PRC 专项红线文件
4. 将问题映射到风险分类
5. 评估严重性、发生概率、可修复性
6. 形成处理建议

`04-risk-register.md` 每个问题至少包含：
- `risk_id`
- `severity`
- `category`
- `clause_id`
- `issue`
- `basis`
- `impact`
- `recommended_action`
- `fallback_position`
- `owner_question`（如需业务补信息）

### Step 5: 生成修改建议，写入 `05-redlines.md`

当用户要求“给修改建议”“给替代条款”“按我方立场改”时，必须生成。

写法要求：
- 先读 [references/standard-redlines.md](references/standard-redlines.md)，确定优先级和 fallback 立场
- 若默认按中国大陆法语境审查，再叠加读取对应合同类型的 PRC 专项红线文件
- 需要具体替代表达时，再读 [references/clause-templates.md](references/clause-templates.md)
- 优先给“为什么要改”和“改成什么”
- 替代条款要尽量可直接粘贴到合同
- 不知道法域或交易背景时，不要编造高度具体的法言法语
- 如果只能给方向性建议，明确标记为“条款方向建议”而非可直接签署文本

### Step 6: 生成审查报告，写入 `06-review-report.md`

必须使用 [references/report-template.md](references/report-template.md)。

报告里要清楚区分：
- 明确违法或违规风险
- 不符合公司制度或内部红线
- 对我方明显不利但可谈判的商业风险
- 信息不足，暂不能下结论的点

### Step 7: 形成签署建议

签署建议只允许输出以下四类之一：
- `建议签署`
- `修改后可签`
- `暂不建议签署`
- `需补充信息后判断`

判定原则：
- 存在 `Critical` 且未覆盖的风险，通常为 `暂不建议签署`
- 存在重大资料缺口，输出 `需补充信息后判断`
- 主要问题是商业谈判项且有清晰 redline，可输出 `修改后可签`
- 只有轻微或可接受偏离时，才考虑 `建议签署`

## 审查结论的写法标准

每条结论尽量遵循这个顺序：
1. 先指出条款或缺失项
2. 再写风险是什么
3. 再写依据是什么
4. 再写会造成什么后果
5. 最后给修改建议或确认问题

避免这些问题：
- 只说“有风险”，不说风险具体在哪
- 只凭经验断言违法，不写依据
- 把内部偏好说成法律底线
- 给出脱离交易背景的极端 redline
- 在信息不足时给出过强结论

## 高风险事项的默认加严规则

遇到下列事项，默认提升一级审查强度：
- 无上限赔偿、间接损失、利润损失、惩罚性责任
- 永久排他、默认独占、过宽竞业限制
- 知识产权全部转让、成果归属不清、背景 IP 被搭进去
- 大规模个人信息处理、跨境传输、审计权过宽
- 单方解除、自动续约、单方变价、验收标准缺失
- 回款条件严重后置、预付款无保障、抵销规则不对等
- 管辖、仲裁地、适用法对我方极不利
- 代表与保证过宽，超出我方可控范围

## 证据与边界

- 这是合同审查工作流，不是替代持牌律师出具正式法律意见
- 没有经过核源的结论，不要包装成确定性判断
- 没有看到完整合同全文时，明确说明结论仅基于已提供部分
- 如果公司制度与法律冲突，优先指出法律冲突，再单列内部流程建议
