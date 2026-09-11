---
blueprint_kind: domain-spec
blueprint_status: draft
owner: trust-and-safety-lead
last_reviewed: 2026-09-10
domain: safety
source_prd: PRD-SAFETY-001
---

# 社区安全行为规格

## SPEC-SAFETY-001 — 举报与审核

- Source: PRD-SAFETY-001
- State: provisional
- Actors: 登录用户、授权组织者、审核员
- Requirement: 用户可举报行动或提交内容；系统必须确认收到举报，限制详情访问，并保留处置审计记录。
- Acceptance method: 自动化授权测试、审核工作流测试与青少年安全评审。

### Scenario: 举报成功

- **GIVEN** 用户正在查看可见的行动或完成记录
- **WHEN** 用户选择举报原因并提交
- **THEN** 系统以文字确认举报已收到，不公开举报人身份，并提供安全返回路径

### Scenario: 未授权查看举报

- **GIVEN** 用户没有审核权限
- **WHEN** 用户尝试访问举报详情
- **THEN** 系统拒绝访问且不泄露被举报内容或举报人信息

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SAFETY-001 | 确认审核队列、升级时限和紧急风险渠道 | trust and safety lead | 内测前 | production-ready | pending |
