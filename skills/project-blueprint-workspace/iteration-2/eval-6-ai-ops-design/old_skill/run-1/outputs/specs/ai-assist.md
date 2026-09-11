---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-AI-001
last_reviewed: 2026-09-10
domain: ai-assist
source_prd: PRD-AI-001
---

# AI 辅助领域行为规格

## SPEC-AI-001 — 有证据边界的事件摘要

- Source: PRD-AI-001, PRD-IMPACT-001
- State: pending（TBD-AI-001）
- Actors: 已认证的控制台用户
- Preconditions: 系统有允许提供给模型的事件上下文；数据政策待确认。
- Requirement: AI 摘要必须把每条结论关联到可见证据，显示生成时间、模型/提示版本的可追踪标识和不确定性；无证据或证据冲突时必须明确标记未知/冲突，关键事实由确定性应用逻辑呈现。
- 验收方法：版本化离线评测、引用完整性自动检查、人工红队和无证据样本测试；发布阈值由 TBD-AI-001 决定。

### Scenario: 生成带引用的摘要

- **GIVEN** 事件包含允许使用的告警、部署和服务关系证据
- **WHEN** 用户请求或系统刷新 AI 摘要
- **THEN** 每条摘要陈述可定位到输入证据并显示生成时间，推断与事实有不同标签，界面不暗示 AI 已确认影响

### Scenario: 证据冲突或不足

- **GIVEN** 两个来源冲突或无法支持影响结论
- **WHEN** AI 生成摘要
- **THEN** 输出明确呈现冲突/未知及缺失证据，不补造服务、指标、原因或建议动作

## SPEC-AI-002 — AI 失败与人工纠正

- Source: PRD-AI-001
- State: pending（TBD-AI-001）
- Actors: 值班工程师、AI 质量负责人
- Preconditions: AI 功能已启用。
- Requirement: AI 超时、拒答、供应商中断或被策略禁用时，系统必须给出确定性降级；授权用户可反馈结论不正确并记录理由，反馈不得自动成为生产事实或训练数据。
- 验收方法：故障注入、策略禁用和反馈权限测试；核对训练使用需独立同意/政策证据。

### Scenario: AI 超时

- **GIVEN** 模型请求超过待定超时预算
- **WHEN** 用户打开影响工作区
- **THEN** 页面仍显示来源事实和确定性关系，AI 区显示暂不可用与重试入口，回滚流程不被 AI 可用性阻断

### Scenario: 用户纠正推断

- **GIVEN** 用户认为 AI 推断错误
- **WHEN** 授权用户提交纠正和理由
- **THEN** 系统记录反馈、保留原输出版本，并明确反馈不会自动修改来源事实或触发生产动作

## 领域不变量

| 规则 | 可观察结果 | 状态 |
|---|---|---|
| AI 没有生产写权限 | AI 组件中不存在可触发回滚的交互 | provisional |
| 输出版本可追踪 | 摘要可关联输入、提示/模型版本和时间 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-AI-001 | 确认用例、数据许可、供应商/模型、评测集、质量阈值、超时和成本预算 | AI/产品负责人 | AI 实现前 | implementation-ready | pending |
