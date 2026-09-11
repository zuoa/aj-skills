---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: rollback
source_prd: PRD-ROLLBACK-001, PRD-SAFETY-001
---

# 回滚行为规格

## SPEC-ROLLBACK-001 — 预检并发起回滚

- Source: PRD-ROLLBACK-001
- State: pending (`TBD-SPEC-003`)
- Actors: 有回滚权限的执行者；需要时为独立批准者
- Preconditions: 目标服务、环境、当前版本和候选版本可明确识别；影响范围处于策略允许的确认状态。
- Requirement: 系统必须在提交前显示不可编辑的目标摘要并重新校验版本、权限、审批和前置条件；仅在全部通过时创建一次可追踪的回滚执行。
- Acceptance method: 适配器契约测试、权限集成测试、并发/幂等自动化测试和非生产演练。

### Scenario: 前置条件满足

- **GIVEN** 影响范围已按策略确认、用户有权限且目标版本未变化
- **WHEN** 用户输入要求的确认文本并提交回滚
- **THEN** 系统创建唯一执行记录，显示执行 ID、目标和“已受理”，且审计记录可查询

### Scenario: 当前版本已变化

- **GIVEN** 确认页显示的当前版本已被另一发布改变
- **WHEN** 用户提交回滚
- **THEN** 系统不发起动作，显示旧值与新值，并要求重新评估候选版本

## SPEC-ROLLBACK-002 — 查看进度、取消与结果

- Source: PRD-ROLLBACK-001, PRD-UX-001
- State: provisional
- Actors: 执行者、批准者、具备查看权限的值班人员
- Preconditions: 回滚执行已创建。
- Requirement: 系统必须区分排队、执行中、取消请求中、成功、失败、部分成功和状态未知；仅在下游支持且状态允许时提供取消，不把超时当作失败或成功。
- Acceptance method: 自动化状态机与恢复测试；注入超时、断连、重复回调和部分成功进行演练。

### Scenario: 回滚成功

- **GIVEN** 下游接受执行并返回可验证成功结果
- **WHEN** 用户查看执行详情
- **THEN** 系统显示最终状态、完成时间、实际版本、验证证据和审计链接

### Scenario: 下游状态未知

- **GIVEN** 下游已受理但查询超时
- **WHEN** 控制台无法确认结果
- **THEN** 系统显示“状态未知”，禁止重复一键执行，并提供刷新、来源链接和升级路径

## SPEC-ROLLBACK-003 — 权限、审批与审计不可绕过

- Source: PRD-SAFETY-001
- State: pending (`TBD-SECURITY-002`, `TBD-SPEC-003`)
- Actors: 执行者、批准者、审计人员
- Preconditions: 身份提供方和授权策略可用。
- Requirement: 系统必须在服务端校验查看、确认、批准和执行权限；生产回滚的职责分离策略由 `TBD-SECURITY-002` 决定；任何拒绝或执行尝试均产生审计事件。
- Acceptance method: 授权矩阵自动化测试、审计完整性测试和绕过路径安全评审。

### Scenario: 无权用户尝试执行

- **GIVEN** 用户可查看告警但没有目标环境的回滚权限
- **WHEN** 用户访问回滚入口或直接提交请求
- **THEN** 系统不创建下游动作，说明缺少的权限范围，并记录拒绝事件

### Scenario: 审计持久化失败

- **GIVEN** 系统无法可靠写入必需的执行审计事件
- **WHEN** 用户尝试发起回滚
- **THEN** 系统拒绝发起高风险动作，显示未执行并给出升级路径

## 领域不变量

| 规则 | 可观察效果 | 状态 |
|---|---|---|
| 建议与执行解耦 | 建议不能直接改变执行目标或跳过确认 | provisional |
| 重复提交不产生重复动作 | 同一幂等请求返回同一执行记录 | provisional |

## 待决定事项

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-003 | 定义部署目标类型、候选版本规则、审批、取消、超时和部分失败行为 | SRE、安全负责人 | 回滚实现前 | implementation-ready | pending |
| TBD-SECURITY-002 | 定义身份提供方、角色、环境/服务级授权与生产职责分离 | 安全负责人、SRE | 回滚实现前 | implementation-ready | pending |
