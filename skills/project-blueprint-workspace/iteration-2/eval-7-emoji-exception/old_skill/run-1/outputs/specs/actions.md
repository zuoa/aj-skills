---
blueprint_kind: domain-spec
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
domain: actions
source_prd: PRD-ACTION-001; PRD-ACTION-002
---

# 行动行为规格

## SPEC-ACTION-001 — 报名状态

- Source: PRD-ACTION-001
- State: confirmed
- Actors: 已登录参与者
- Preconditions: 行动开放报名。
- Requirement: 系统显示报名结果和当前状态，重复请求只产生一个报名。
- Acceptance method: 自动化状态测试及键盘/屏幕阅读器人工测试。

### Scenario: 报名成功

- **GIVEN** 用户未报名且仍有名额
- **WHEN** 用户激活“报名参加”
- **THEN** 系统显示并公告“已报名”，刷新后状态不变

### Scenario: 满员

- **GIVEN** 提交报名时名额已满
- **WHEN** 用户提交报名
- **THEN** 系统不创建报名，以文字说明满员并提供返回行动列表的操作

## SPEC-ACTION-002 — 提交完成记录

- Source: PRD-ACTION-002
- State: confirmed
- Actors: 已报名参与者
- Preconditions: 行动已开始，输入满足已公布要求。
- Requirement: 系统保存一条完成记录，并用完整文字告知结果。
- Acceptance method: 幂等与失败恢复自动测试；屏幕阅读器公告人工测试。

### Scenario: 提交成功

- **GIVEN** 用户填写有效完成记录
- **WHEN** 用户选择“提交完成记录”
- **THEN** 系统创建一条记录，显示并公告“行动已记录，感谢你的参与。”

### Scenario: 网络失败

- **GIVEN** 用户已填写记录但网络不可用
- **WHEN** 用户尝试提交
- **THEN** 系统保留输入，不显示成功状态，并说明如何重试

## SPEC-ACTION-003 — 组织者核验

- Source: PRD-ACTION-002
- State: provisional
- Actors: 授权组织者
- Requirement: 组织者可把记录从待核验改为已通过或需补充，参与者看到文字结果。
- Acceptance method: 授权和状态转换自动测试。

### Scenario: 核验通过

- **GIVEN** 记录待核验且组织者有权限
- **WHEN** 组织者选择通过
- **THEN** 参与者看到“已通过”和更新时间

### Scenario: 无权限

- **GIVEN** 用户不是对应行动的组织者
- **WHEN** 用户尝试核验
- **THEN** 系统拒绝操作且不泄露记录详情

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ACTION-001 | 确认证据格式、上限和核验时效 | product/safety | 设计定稿前 | implementation-ready | pending |
