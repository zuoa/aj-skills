---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: impact
source_prd: PRD-IMPACT-001
---

# 影响范围行为规格

## SPEC-IMPACT-001 — 查看可追溯的影响范围

- Source: PRD-IMPACT-001
- State: provisional
- Actors: 值班开发人员、事件负责人
- Preconditions: 用户已打开一个可见告警；至少一种服务或发布关系来源已配置。
- Requirement: 系统必须按服务、环境、版本和依赖列出受影响对象；每条关系标明事实/推断类型、来源、时间和可用性，不把缺失关系解释为“无影响”。
- Acceptance method: 用固定关系图样例进行自动化映射测试；人工核对来源、长名称和冲突呈现。

### Scenario: 多来源证据一致

- **GIVEN** 监控、服务目录和部署记录指向同一服务版本
- **WHEN** 用户打开影响范围
- **THEN** 系统将证据按对象归组，同时保留每个来源和时间

### Scenario: 证据冲突

- **GIVEN** 两个来源对当前版本或环境给出不同值
- **WHEN** 用户查看影响范围
- **THEN** 系统明确标记冲突值与来源，不自动选择其中一个作为已确认事实

## SPEC-IMPACT-002 — 记录影响确认结论

- Source: PRD-IMPACT-001, PRD-UX-001
- State: pending (`TBD-SPEC-002`)
- Actors: 具备影响确认权限的人员
- Preconditions: 影响证据已加载到成功、部分或失败状态。
- Requirement: 系统必须允许授权用户将影响项标记为已确认、已驳回或待补证据，并记录操作者、时间和理由；证据不完整时不得把整体状态标为“影响已完整确认”。
- Acceptance method: 自动化权限与状态转换测试；人工验证部分数据、离线和并发冲突。

### Scenario: 确认完整证据集

- **GIVEN** 必需证据均可用且无未处理冲突
- **WHEN** 授权用户确认影响范围并填写必要说明
- **THEN** 系统保存确认人、确认时间、证据版本和结论，并使回滚前置条件可见

### Scenario: 确认期间证据已变化

- **GIVEN** 用户打开页面后关键版本或依赖证据发生变化
- **WHEN** 用户提交确认
- **THEN** 系统拒绝基于旧证据的提交，展示变化并要求重新核对

## 领域不变量

| 规则 | 可观察效果 | 状态 |
|---|---|---|
| “未发现”与“未采集”分开 | 用户能看到缺失来源，不会误判为零影响 | provisional |
| 推断不升级为人工确认 | 推断标签始终保留，直到具名用户确认 | provisional |

## 待决定事项

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-002 | 定义各工作负载必需证据、整体完整性规则和确认权限 | SRE、服务负责人 | 影响原型验收前 | implementation-ready | pending |
