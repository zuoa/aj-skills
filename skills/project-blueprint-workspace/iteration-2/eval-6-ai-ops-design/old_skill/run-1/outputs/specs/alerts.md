---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: alerts
source_prd: PRD-ALERT-001
---

# 告警领域行为规格

## SPEC-ALERT-001 — 浏览与筛选告警

- Source: PRD-ALERT-001
- State: provisional
- Actors: 已认证的值班工程师
- Preconditions: 至少一个告警来源已连接；来源与字段契约待 TBD-INTEGRATION-001。
- Requirement: 系统必须以可排序列表显示告警的来源、严重度、生命周期状态、服务、环境、首次/最近发生时间与新鲜度，并允许组合筛选；当前筛选始终可见且可清除。
- 验收方法：使用固定告警样本做自动化筛选/排序测试，并做键盘与屏幕阅读器人工走查。

### Scenario: 找到生产中的活跃高严重度告警

- **GIVEN** 样本包含多个环境、严重度和状态的告警
- **WHEN** 用户选择生产环境、活跃状态和目标严重度
- **THEN** 列表只显示同时满足条件的告警，结果数和当前筛选可见，刷新页面后筛选按已定义策略恢复

### Scenario: 没有匹配结果

- **GIVEN** 当前筛选没有匹配告警且来源查询成功
- **WHEN** 查询完成
- **THEN** 系统显示“无匹配结果”而非“无告警”，并提供清除筛选入口

## SPEC-ALERT-002 — 告警来源与新鲜度透明

- Source: PRD-ALERT-001
- State: provisional；新鲜度阈值 pending（TBD-NFR-001）
- Actors: 值班工程师
- Preconditions: 系统保存最后成功同步时间和来源状态。
- Requirement: 系统必须区分“当前来源无告警”“来源不可用”和“仅有陈旧数据”，并在告警详情中提供可定位的来源链接或来源标识。
- 验收方法：集成契约测试模拟成功、超时、部分失败和陈旧响应；人工核对文案不混淆状态。

### Scenario: 来源部分中断

- **GIVEN** 一个告警来源失败而其他来源成功
- **WHEN** 用户打开告警工作台
- **THEN** 可用来源的结果仍显示，失败来源及最后成功时间被明确标注，系统不声称列表完整

### Scenario: 刷新时保留最后已知数据

- **GIVEN** 用户正在查看告警且下一次刷新失败
- **WHEN** 刷新完成
- **THEN** 最后已知数据保留并标记为陈旧，页面提供重试与打开源系统的路径

## 领域不变量

| 规则 | 可观察结果 | 状态 |
|---|---|---|
| 不以缺失数据推断“正常” | 来源失败时显示未知/不完整 | provisional |
| 时间可判读 | 绝对时间含时区，相对时间仅辅助 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-INTEGRATION-001 | 确认告警来源、字段映射、深链与速率限制 | 平台负责人 | 架构评审前 | implementation-ready | pending |
| TBD-NFR-001 | 确认来源新鲜度及查询响应预算 | SRE 负责人 | 性能方案冻结前 | implementation-ready | pending |
