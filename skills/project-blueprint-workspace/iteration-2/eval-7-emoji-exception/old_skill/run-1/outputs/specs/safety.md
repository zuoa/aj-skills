---
blueprint_kind: domain-spec
blueprint_status: draft
owner: safety-lead
last_reviewed: 2026-09-10
domain: safety
source_prd: PRD-SAFETY-001
---

# 社区安全行为规格

## SPEC-SAFETY-001 — 举报与权限

- Source: PRD-SAFETY-001
- State: provisional
- Actors: 登录用户、组织者、审核员
- Requirement: 用户可举报可见内容；仅授权人员可查看和处置举报，系统保留审计记录。
- Acceptance method: 对象级授权、举报状态和审计自动测试。

### Scenario: 举报成功

- **GIVEN** 用户可查看一个行动或完成记录
- **WHEN** 用户提交举报原因
- **THEN** 系统用文字确认收到举报并保护举报人身份

### Scenario: 未授权访问

- **GIVEN** 用户没有审核权限
- **WHEN** 用户请求举报详情
- **THEN** 系统拒绝请求且不泄露相关内容

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SAFETY-001 | 确认审核、升级和紧急渠道 | safety lead | 内测前 | production-ready | pending |
