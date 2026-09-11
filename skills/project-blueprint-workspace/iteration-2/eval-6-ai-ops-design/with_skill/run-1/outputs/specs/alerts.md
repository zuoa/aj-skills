---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: alerts
source_prd: PRD-ALERT-001
---

# 告警行为规格

## SPEC-ALERT-001 — 查看与定位告警

- Source: PRD-ALERT-001
- State: provisional
- Actors: 已认证的值班开发人员
- Preconditions: 至少一个告警来源已配置；用户具备对应服务和环境的查看权限。
- Requirement: 系统必须显示用户有权查看的告警，并提供状态、严重度、服务、环境、负责人、最后更新时间和来源链接；筛选后保持可见的筛选条件和结果数。
- Acceptance method: 使用契约桩进行自动化筛选、权限和排序测试；用键盘完成手动任务测试。

### Scenario: 找到未确认的生产告警

- **GIVEN** 用户可见多个环境和状态的告警
- **WHEN** 用户筛选生产环境与未确认状态
- **THEN** 列表仅显示同时匹配的结果，并显示已应用筛选及结果数量

### Scenario: 无查看权限

- **GIVEN** 告警关联到用户无权查看的服务
- **WHEN** 用户查询告警列表或访问其直接链接
- **THEN** 系统不泄露告警内容，并返回可区分的权限拒绝结果和申请路径

## SPEC-ALERT-002 — 显示来源完整性与新鲜度

- Source: PRD-ALERT-001, PRD-UX-001
- State: pending (`TBD-SPEC-001`)
- Actors: 值班开发人员
- Preconditions: 告警来源返回成功、延迟、冲突或失败之一。
- Requirement: 系统必须把最新、陈旧、部分缺失和不可用显示为不同文字状态；不得仅用颜色表达，也不得在来源失败时显示虚假的最新状态。
- Acceptance method: 自动化状态映射测试和屏幕阅读器名称检查；人工核对绝对时间与来源链接。

### Scenario: 来源更新成功

- **GIVEN** 来源数据在已定义的新鲜度窗口内
- **WHEN** 用户查看列表或详情
- **THEN** 系统显示更新时间、来源和当前状态

### Scenario: 来源超时但缓存存在

- **GIVEN** 最新拉取超时且存在先前数据
- **WHEN** 用户查看告警
- **THEN** 系统显示该数据的实际时间与“陈旧”文字，说明刷新失败且不覆盖旧证据

## 领域不变量

| 规则 | 可观察效果 | 状态 |
|---|---|---|
| 未知严重度不自动映射为最低严重度 | 用户看到“未知”，可按未知筛选 | provisional |
| 来源对象保持可追溯 | 每个告警可打开原始来源或显示来源不可达原因 | provisional |

## 待决定事项

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 定义来源优先级、刷新方式、新鲜度阈值与冲突规则 | SRE、产品负责人 | 集成契约定稿前 | implementation-ready | pending |
