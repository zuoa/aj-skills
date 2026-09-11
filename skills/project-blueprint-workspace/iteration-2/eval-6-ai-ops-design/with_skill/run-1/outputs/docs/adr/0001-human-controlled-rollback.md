---
blueprint_kind: adr
blueprint_status: proposed
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# ADR 0001：回滚保持确定性的人类控制边界

- Status: proposed
- Date: 2026-09-10
- Related requirements: PRD-ROLLBACK-001, PRD-SAFETY-001; SPEC-ROLLBACK-001..003

## 背景与选项

回滚具有生产影响，而模型输出是概率性的。候选为模型直接执行、模型建议后由策略与人员批准、完全不使用模型。

## 决定

如启用 AI，仅生成带来源和不确定性的只读建议。回滚目标、权限、当前版本、审批与审计由确定性服务校验，最终提交由有权限人员明确触发。

## 后果与复核

增加一次人工确认和策略服务依赖，但保持责任边界、可审计性及无模型降级路径。仅当风险评审、用户研究和可验证控制证明另一方案更安全时复核。
