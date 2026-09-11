---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: scheduling
source_prd: PRD-SCHED-001
---

# Scheduling 行为规格

## SPEC-SCHED-001 — 教练维护公开可预约时段

- Source: PRD-SCHED-001
- State: provisional
- Actors: 已认证且获工作区授权的教练
- Preconditions: 教练进入自己的管理端；排班模型仍待 TBD-BOOK-001。
- Requirement: 系统必须允许教练查看当前可预约时段，并创建、修改或撤下时段；保存结果必须反映到对应公开预约页。
- Acceptance method: 自动化领域/API 测试加管理端与手机网页手动任务测试。

### Scenario: 成功发布时段

- **GIVEN** 教练已进入自己的工作区，且输入符合最终确认的排班规则
- **WHEN** 教练保存一个可预约时段
- **THEN** 管理端显示保存成功，且该教练的公开预约页显示该时段可预约

### Scenario: 无效或冲突设置

- **GIVEN** 教练输入不符合最终确认的时间、容量或冲突规则
- **WHEN** 教练尝试保存
- **THEN** 系统不发布该设置，并在可修正的位置说明问题

### Scenario: 撤下时段

- **GIVEN** 一个尚未被预约的时段正在公开显示
- **WHEN** 教练撤下该时段
- **THEN** 学员端不再将其显示为可预约；已预约时段如何处理由 TBD-BOOK-002 决定

## 领域不变量

| Rule | 可观察效果 | State |
|---|---|---|
| 发布状态一致 | 管理端标记为未发布的时段不会在学员页显示为可预约 | provisional |
| 规则错误可恢复 | 无效设置不会部分生效，教练可保留上下文后修正 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-BOOK-001 | 确认课程/排班模型、时长、容量、时区和冲突规则 | 产品负责人（未指定） | 预约交互与数据模型定稿前 | implementation-ready | pending |
| TBD-BOOK-002 | 确认改期、取消、爽约、截止时间及支付是否属于 MVP | 产品负责人（未指定） | 行为规格签署前 | implementation-ready | pending |

