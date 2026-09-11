---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与权威关系

本文件负责共享行为规则、领域索引、追踪关系和就绪度。详细可观察行为位于 `specs/`；技术机制不在行为规格中定义。

## 术语

| 术语 | 含义 | 来源 |
|---|---|---|
| 告警 | 来源系统报告、需要团队判断的异常信号；不等同于已确认事故 | PRD-ALERT-001 |
| 影响证据 | 具有来源、采集时间和对象标识的事实或推断 | PRD-IMPACT-001 |
| 影响确认 | 人员对证据作出的确认、驳回或待补结论 | PRD-IMPACT-001 |
| 回滚目标 | 明确到服务、环境和版本的候选恢复动作 | PRD-ROLLBACK-001 |
| 陈旧 | 超过已配置新鲜度规则的数据；阈值为 `TBD-SPEC-001` | PRD-ALERT-001 |
| 建议 | 不具备执行权限、必须附来源和不确定性的辅助输出 | PRD-SAFETY-001 |

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | 状态 |
|---|---|---|---|
| RULE-001 | 每个外部事实显示来源与采集/更新时间，来源失败时不沿用为“最新” | PRD-ALERT-001; PRD-IMPACT-001 | provisional |
| RULE-002 | 用户可区分事实、系统推断、人工确认和未知项 | PRD-IMPACT-001; PRD-SAFETY-001 | provisional |
| RULE-003 | 回滚动作不由建议直接触发，且提交时重新校验当前状态和权限 | PRD-ROLLBACK-001; PRD-SAFETY-001 | provisional |
| RULE-004 | 所有时间同时提供明确时区；显示相对时间时可读取绝对时间 | PRD-UX-001 | provisional |
| RULE-005 | 错误结果说明发生了什么、动作是否生效以及下一步 | PRD-UX-001 | provisional |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Alerts | `specs/alerts.md` | 产品负责人 | draft |
| Impact | `specs/impact.md` | 产品负责人、SRE | draft |
| Rollback | `specs/rollback.md` | SRE、安全负责人 | draft |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-ALERT-001 | SPEC-ALERT-001 | DESIGN.md#告警队列 | ARCHITECTURE.md#模块边界 | planned |
| PRD-ALERT-001 | SPEC-ALERT-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-IMPACT-001 | SPEC-IMPACT-001 | DESIGN.md#证据轨道 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-IMPACT-001 | SPEC-IMPACT-002 | DESIGN.md#影响确认流 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-ROLLBACK-001 | SPEC-ROLLBACK-001 | DESIGN.md#回滚执行流 | ARCHITECTURE.md#高风险动态流 | planned |
| PRD-ROLLBACK-001 | SPEC-ROLLBACK-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#高风险动态流 | planned |
| PRD-SAFETY-001 | SPEC-ROLLBACK-003 | DESIGN.md#回滚执行流 | SECURITY.md#身份与访问 | planned |
| PRD-UX-001 | SPEC-ALERT-002; SPEC-IMPACT-002; SPEC-ROLLBACK-002 | DESIGN.md#无障碍与内容 | ARCHITECTURE.md#预期降级 | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PRODUCT-001; TBD-PRODUCT-003 | PRD.md#未决事项；DESIGN.md#未决事项 |
| implementation-ready | blocked | TBD-PRODUCT-002; TBD-PRODUCT-004; TBD-SPEC-001; TBD-SPEC-002; TBD-SPEC-003; TBD-DESIGN-001; TBD-ARCH-001; TBD-ARCH-002; TBD-ARCH-003; TBD-AI-001; TBD-SECURITY-002; TBD-ENGINEERING-001 | 领域规格；DESIGN.md；ARCHITECTURE.md；SECURITY.md；ENGINEERING.md |
| production-ready | blocked | TBD-COMPLIANCE-001; TBD-SECURITY-001; TBD-SECURITY-003; TBD-DEPLOY-001; TBD-DEPLOY-002; TBD-DEPLOY-003; TBD-DEPLOY-004 | SECURITY.md；DEPLOY.md |

## 待决定事项

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 定义告警更新、新鲜度和冲突合并规则 | SRE、产品负责人 | 集成契约定稿前 | implementation-ready | pending |
| TBD-SPEC-002 | 定义“影响范围完整”的证据集合和确认权限 | SRE、服务负责人 | 影响原型验收前 | implementation-ready | pending |
| TBD-SPEC-003 | 定义可回滚对象、审批矩阵、超时及部分失败行为 | SRE、安全负责人 | 回滚实现前 | implementation-ready | pending |
