---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-ROLLBACK-001
last_reviewed: 2026-09-10
domain: rollback
source_prd: PRD-ROLLBACK-001
---

# 回滚领域行为规格

## SPEC-ROLLBACK-001 — 回滚资格与预检

- Source: PRD-ROLLBACK-001
- State: pending（TBD-ROLLBACK-001）
- Actors: 获授权发布人员
- Preconditions: 告警关联到一个部署；发布系统可查询能力。
- Requirement: 系统必须在允许提交前，从权威发布系统确认目标仍存在且可回滚，并显示环境、服务、当前版本、目标版本、变更时间、预检结果及审批要求；任一关键项未知时默认禁止提交。
- 验收方法：发布适配器契约测试和端到端演练覆盖可用、不可用、无目标、目标变化与预检失败。

### Scenario: 预检通过

- **GIVEN** 用户有权限，发布系统确认部署可回滚且返回目标版本
- **WHEN** 用户打开回滚预览
- **THEN** 系统显示全部关键字段和预检时间，并仅在审批规则满足后启用最终确认入口

### Scenario: 目标在预览后变化

- **GIVEN** 用户打开预览后当前部署版本发生变化
- **WHEN** 用户进入最终确认或提交
- **THEN** 系统使旧预检失效、禁止提交并要求基于新状态重新预检

## SPEC-ROLLBACK-002 — 明确确认与幂等提交

- Source: PRD-ROLLBACK-001
- State: pending（TBD-ROLLBACK-001, TBD-IDENTITY-001）
- Actors: 获授权发布人员；批准者是否独立待定
- Preconditions: 最新预检有效；审批条件满足。
- Requirement: 系统必须通过独立确认步骤显示不可省略的目标摘要；提交使用唯一操作标识，重复操作不得创建第二个回滚；AI 不得触发或代替确认。
- 验收方法：权限、并发、重复点击、网络超时与重放的自动化测试；破坏性动作人工可用性检查。

### Scenario: 用户确认生产回滚

- **GIVEN** 最新预检有效、权限与审批满足
- **WHEN** 用户在确认页核对环境和版本并提交
- **THEN** 系统创建一个带唯一标识的回滚操作，立即显示“已受理”而非“成功”，并进入进度页

### Scenario: 提交响应超时后重试

- **GIVEN** 首次提交可能已被发布系统接受但响应超时
- **WHEN** 客户端以相同操作标识重试
- **THEN** 系统返回同一操作状态，不创建第二个回滚，并提示结果仍在确认

## SPEC-ROLLBACK-003 — 进度、终态与恢复路径

- Source: PRD-ROLLBACK-001
- State: pending（TBD-ROLLBACK-001）
- Actors: 值班工程师、发布人员、事件指挥者
- Preconditions: 回滚请求已被受理。
- Requirement: 系统必须显示发布系统返回的阶段、最近更新时间和终态；无法确认结果时显示“状态未知”，提供刷新、打开权威发布系统和升级响应路径，不得将请求已发送等同于成功。
- 验收方法：适配器状态机与故障注入测试；运行手册演练。

### Scenario: 回滚成功

- **GIVEN** 发布系统接收回滚并最终报告成功
- **WHEN** 控制台获取终态
- **THEN** 系统显示成功、完成时间、实际版本和权威执行链接，并记录审计事件

### Scenario: 发布系统状态不可达

- **GIVEN** 回滚已受理但发布系统状态查询失败
- **WHEN** 超过待定的状态新鲜度预算
- **THEN** 系统显示“状态未知”而非失败或成功，停止自动重复提交，并显示人工核验与升级路径

## 领域不变量

| 规则 | 可观察结果 | 状态 |
|---|---|---|
| 默认拒绝未知条件下的生产写操作 | 权限、目标、预检或审批未知时不能提交 | provisional |
| 请求与结果分离 | “已受理”不显示成“成功” | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ROLLBACK-001 | 定义各发布系统的回滚状态机、资格、审批、停止和补救 | 发布负责人 | 领域规格冻结前 | implementation-ready | pending |
| TBD-IDENTITY-001 | 定义生产动作授权与双人复核规则 | 安全/发布负责人 | 安全设计评审前 | implementation-ready | pending |
