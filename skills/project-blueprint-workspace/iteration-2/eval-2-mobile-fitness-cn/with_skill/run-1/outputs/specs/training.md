---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SPEC-001
last_reviewed: 2026-09-10
domain: training
source_prd: PRD-TRAIN-001
---

# 训练与打卡规格

## SPEC-TRAIN-001 — 查看和维护训练计划
- Source: PRD-TRAIN-001
- State: provisional
- Actors: 学员、授权教练
- Requirement: 教练可维护授权学员计划；学员看到适用于当前业务日期的只读计划。
- Acceptance method: 自动化角色/关系/日期边界测试；移动端与教练 Web 人工验收。

### Scenario: 查看当前计划
- **GIVEN** 学员有生效计划
- **WHEN** 学员打开今日训练
- **THEN** 系统显示日期、动作/任务和完成状态

### Scenario: 非授权教练修改
- **GIVEN** 教练与目标学员无有效授权关系
- **WHEN** 教练尝试修改计划
- **THEN** 系统拒绝且不返回受限计划内容

## SPEC-CHECKIN-001 — 每日打卡
- Source: PRD-CHECKIN-001
- State: provisional
- Actors: 学员
- Requirement: 学员可为允许的业务日期提交打卡；离线提交须显示本地待同步与最终服务端结果。
- Acceptance method: 自动化日期、重复/幂等、离线同步与冲突测试；真机恢复测试。

### Scenario: 成功打卡
- **GIVEN** 用户已登录且当天任务允许打卡
- **WHEN** 用户提交打卡
- **THEN** 系统显示服务端确认的日期、状态和内容

### Scenario: 离线或重复提交
- **GIVEN** 设备离线或相同操作已提交
- **WHEN** 用户点击打卡
- **THEN** 系统不制造第二条完成记录，并区分待同步、已同步或冲突

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-TRAIN-001 | 确认计划版本、业务日期、补签/修改和同步冲突规则 | product-owner | 实现前 | implementation-ready | pending |
