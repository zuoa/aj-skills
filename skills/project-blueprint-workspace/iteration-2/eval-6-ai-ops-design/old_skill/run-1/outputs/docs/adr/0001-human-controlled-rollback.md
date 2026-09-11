---
blueprint_kind: adr
blueprint_status: proposed
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# ADR 0001：回滚保持人类控制

- Status: proposed
- Date: 2026-09-10
- Related requirements: PRD-ROLLBACK-001; SPEC-ROLLBACK-001..003

## 决定

AI 只能提供带来源和不确定性的只读建议。回滚目标、权限、版本、审批与审计由确定性服务校验，最终提交由有权限人员明确触发。

## 后果

增加一次人工确认与策略依赖，但保留责任边界、可审计性和无模型降级路径。风险评审和可验证控制发生实质变化时复核。
