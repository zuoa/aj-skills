# 数据契约与分析规则

## 输入与目录

由 agent 阅读材料并生成 JSON，脚本不直接理解 DOCX/PDF。所有日期使用业务当地日历日 `YYYY-MM-DD`；记录时间使用 UTC。Python 3.10+，仅标准库。

```json
{
  "period": {"id": "2026-W42", "type": "weekly", "start": "2026-10-12", "end": "2026-10-18", "as_of": "2026-10-18"},
  "goals": [
    {"id": "G-product-acceptance", "title": "完成产品验收", "department": "研发部", "owner": "张工", "criteria": "验收单签署", "deadline": "2026-10-16", "metric": null}
  ],
  "observations": {
    "G-product-acceptance": {"status": "in_progress", "progress": "已完成联调，客户验收未结束", "forecast_date": "2026-10-20", "reason": "客户测试环境未开放", "action": "协调开放测试环境", "action_owner": "李经理", "action_deadline": "2026-10-19"}
  },
  "questions": [
    {"id": "Q-customer-risk", "title": "客户测试环境阻碍", "group": "风险与阻碍", "question": "环境开放是否已取得客户确认？对下期交付有何影响？用于判断下期风险。", "context": "上期提及需要客户配合，本期未说明协调结果", "priority": "高"}
  ],
  "sources": [{"file": "研发部总结.md", "location": "客户验收", "goal_ids": ["G-product-acceptance"]}],
  "notes": {"unplanned": [], "next_plans": [], "risks": [], "decisions": []}
}
```

- `period.type` 为 `weekly` 或 `monthly`。ID 由字母、数字、`-`、`_` 组成，最长 80 字符；范围必须包含统计截止日。含糊周范围先确认。
- `goals` 可只提供新增/变化的目标，已有活跃目标自动继承。`observations` 是本期事实，不能复制上期数值当作本期更新。完成和取消的目标可通过 ID 显式带入本期进行复查。
- 缺失值留空或使用 `null`，不要用“待确认”冒充负责人或日期；数值 0 是有效答案。
- 可选目标字段：`start_date`、`parent_id`。目标必须有 ID 和名称，负责人、部门、验收标准、日期缺少时进入表单。
- `status`：`not_started`、`in_progress`、`completed`、`paused`、`cancelled`。完成后须确认 `actual_date`；延期、预计超期、暂停或取消后须确认原因、纠偏动作及责任人/日期，或明确未知。`forecast_date` 是预测，不改变基线。
- 风险、下期计划、专题、资料异常、冲突都要逐项提问。`questions` 的回答保存为 `extra_answers` 交给 agent 理解；需要数字计算的字段必须放入对应 `observations`，不能只用额外文字答案替代。
- `sources` 仅作内部核对；主报告与确认记录不列材料来源。`notes` 是 agent 提取的业务上下文，脚本不推断其完整性。

工作目录结构：

```text
.weekly-report/
  ledger.json                       已确认目标、待确认目标、变更历史、revision
  periods/<period-id>/
    session.json                    本期输入、问题、草稿、提交状态
    runtime.json                    本次服务链接和 PID，停服时移除
    snapshot.json                   本次合并输入及合并后的目标台账
    analysis.json                   数量、状态、目标/时间偏差及可比历史
    confirmation.md                 单独的补充与确认记录
    report.md                       最终 Markdown 的归档副本
```

会话状态：`draft → submitted → merged → generated`；材料完整时 `ready → merged → generated`。同 ID 不覆盖；修订使用新 ID。台账与草稿采用文件锁和版本号，避免多个页面或两个周期静默覆盖；合并可重复执行并支持提交中断恢复。

## 指标契约

目标中 `metric` 示例：

```json
{"target": 100, "unit": "万元", "definition": "客户已签署验收单金额，含税", "direction": "at_least", "aggregation": "incremental", "period_start": "2026-10-01", "period_end": "2026-10-31"}
```

本期指标实际值在对应 `observation` 中记录 `actual`，并显式提供 `unit`、`definition`、`aggregation`、`period_start`、`period_end`。

- `direction`：`at_least` 越大越好，`at_most` 越小越好。
- `aggregation`：`incremental` 统计期新增；`cumulative` 某起点至截止日累计；`snapshot` 截止日存量/比率快照。
- 只有五个口径字段完全匹配、基线已确认，才计算目标差额；不同口径允许如实提交，但输出 `metric_comparison=null`，不能将其改写为可比数据。
- 默认差额为 `实际 - 目标`。越大越好且目标大于 0 时，完成率为 `实际 / 目标 × 100%`；0 或负目标、越小越好指标不生成机械完成率。
- 实际数据的统计截止不能晚于报告截止。月底目标与月中实际不在同一统计窗口时，不计算“本月已失败”；有明确阶段目标则另建阶段指标。
- 月报优先读取月度结果；确需由周数据组成月度新增时，由 agent 核对去重、完整覆盖和不重叠后建立明确月度实际数，脚本不会自动求和。
- 环比只取之前已结束、不重叠、同类型报告中最近一期；指标口径、方向和数值类型须一致。新增型统计天数须一致，两个完整自然月可按月比较，不要求月份天数相等。累计型默认不算环比，零历史基数不算增长率。无可比数据不输出趋势结论。

## 基线与时间分析

首次、验收标准/目标值/负责人/日期变更均需确认。变更基线需说明原因；“暂无法确认”保留原已确认基线及待确认方案，后续周期继续询问，不以待确认方案计算达成。

台账保存 `original_deadline`、当前 `deadline` 和每次变更的前后值、原因、周期。目标开始后延期不重置原日期。

- 完成日期比承诺早/同日/晚分别为 `early`、`on_time`、`late`。
- 尚未完成且截止日早于统计截止日为 `overdue`；尚未到期但预测晚于截止为 `at_risk`；其余有事实支持的在途事项为 `not_due`，不等同于按计划。
- 没有基线或实际/预计日期时相应时间结论为 `unknown`，不虚构具体天数。
- `delay_days` 相对当前承诺；`original_delay_days` 相对原始承诺。原始日期未明时不计算。
- 摘要互斥分类：`achieved`、`deviation`、`in_progress`、`cancelled`、`unknown`，合计等于 `tracked`。已完成但晚交的事项归偏差；事实不足的事项归未知。
- `unresolved` 按字段保存用户的未知原因。一个目标可以已有确定业务偏差，同时存在未知原因；报告需同时表达偏差和判断限制，不能只看计数就忽略字段级未知。

任务字段的 `when` 表示条件问题。只有当前状态/日期触发时才需要回应；改选已完成、调整日期后须重新计算条件。材料已充分的事实无需重复填写。

## 人工答案接口

每个问题按任务 ID、字段名存储：

```json
{"revision": 0, "answers": {"baseline-G-product-acceptance": {"confirmation": {"mode": "value", "value": true}}, "progress-G-product-acceptance": {"reason": {"mode": "unknown", "reason": "客户尚未反馈，周一跟进"}}}, "new_goals": []}
```

只接受具体值或有原因的未知；不会默认选中确认。浏览器添加的交付目标和下期计划需填写部门、负责人、验收标准、日期、状态与进展并单独确认。复杂指标在材料提取时按上述 metric 结构建立；界面新增交付目标可将量化要求写入验收标准，下期由 agent 识别为结构化指标后重新确认。
