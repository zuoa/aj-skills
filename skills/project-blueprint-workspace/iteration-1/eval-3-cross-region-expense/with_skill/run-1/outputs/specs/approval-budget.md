---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: approval-budget
source_prd: PRD-APPROVAL-001, PRD-BUDGET-001
---

# 审批与预算行为规格

## SPEC-APPROVAL-001 — 作出可追溯审批决定

- Source: PRD-APPROVAL-001
- State: provisional
- Actors: 经理
- Preconditions: 费用已提交且当前用户是该审批步骤的授权处理人。
- Requirement: 系统必须允许经理批准、退回补充或拒绝；决定包含操作者、时间、理由、费用版本与所用规则版本。
- Acceptance method: 角色权限、并发、退回重提与审计端到端测试。

### Scenario: 成功批准

- **GIVEN** 经理有权限且费用仍在其待办中
- **WHEN** 经理批准
- **THEN** 系统原子地保存决定、移出该经理待办，并显示下一状态

### Scenario: 并发决定

- **GIVEN** 同一审批步骤已被另一授权人处理
- **WHEN** 经理基于旧页面再次决定
- **THEN** 系统拒绝覆盖并展示最新状态，不产生第二个有效决定

### Scenario: 越权访问

- **GIVEN** 用户不属于该租户或无该审批权限
- **WHEN** 用户请求查看或决定费用
- **THEN** 系统拒绝操作且不泄露费用是否存在，并记录安全审计事件

## SPEC-BUDGET-001 — 发布版本化预算

- Source: PRD-BUDGET-001
- State: provisional
- Actors: 企业管理员
- Preconditions: 管理员有预算配置权限。
- Requirement: 系统必须支持按组织、期间和费用类别配置预算；发布形成不可变版本，已发生的审批保留当时采用的版本。
- Acceptance method: 规则冲突、权限、边界金额和历史回放测试。

### Scenario: 发布新版本

- **GIVEN** 配置没有重叠冲突且生效时间有效
- **WHEN** 管理员发布预算
- **THEN** 系统生成新版本并显示生效范围，不修改此前费用的预算判定证据

### Scenario: 冲突规则

- **GIVEN** 新配置与同范围同期间规则冲突
- **WHEN** 管理员尝试发布
- **THEN** 系统阻止发布并指出冲突范围

### Scenario: 预算不足

- **GIVEN** 费用会使适用预算超出限额
- **WHEN** 费用进入审批
- **THEN** 系统根据租户已发布策略阻止、升级或警告，并向审批人明确展示采用的策略；策略选择待 TBD-BUDGET-001

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 审批决定不可静默修改 | 更正产生新事件且保留原决定 | provisional |
| 预算规则按版本解释 | 历史费用可显示原规则版本 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-BUDGET-001 | 确认预算超限采用阻止、升级还是仅警告及并发占用语义 | 产品/财务负责人 | 预算模块实现前 | implementation-ready | pending |
| TBD-APPROVAL-001 | 确认单级/多级、代理、会签和升级规则的 MVP 范围 | 产品负责人 | 审批模块实现前 | implementation-ready | pending |

