---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
domain: audit
source_prd: PRD-AUDIT-001
---

# 审计领域行为规格

## SPEC-AUDIT-001 — 可追责的事件与回滚时间线

- Source: PRD-AUDIT-001
- State: pending（TBD-SECURITY-001）
- Actors: 安全审计员、事件指挥者；查看权限待定
- Preconditions: 发生影响确认/纠正、回滚预检/审批/提交/状态变化或敏感操作拒绝。
- Requirement: 系统必须形成按事件关联的审计时间线，至少区分操作者或机器身份、动作、目标、时间、结果、理由、关联证据和相关操作标识；普通用户不能修改或删除审计记录。
- 验收方法：自动化完整性、授权和事件关联测试；保留/导出策略人工审核。

### Scenario: 复盘一次回滚

- **GIVEN** 一次回滚经历预检、审批、提交和终态
- **WHEN** 有权限的审计员打开事件时间线
- **THEN** 各阶段按明确时间与身份展示，可关联原证据和权威发布记录，且“请求”“批准”“执行结果”互不混淆

### Scenario: 未授权访问审计详情

- **GIVEN** 用户没有审计详情权限
- **WHEN** 用户请求时间线或导出
- **THEN** 系统拒绝访问、显示安全的权限说明，并记录该访问尝试而不泄露审计内容

## 领域不变量

| 规则 | 可观察结果 | 状态 |
|---|---|---|
| 审计记录不可由普通产品操作修改 | UI 无编辑/删除入口，篡改测试失败 | provisional |
| 机器与人类身份分开 | 时间线明确标识动作主体类型 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 定义审计事件、访问、保留、导出和证据完整性要求 | 安全负责人 | 生产安全评审前 | production-ready | pending |
