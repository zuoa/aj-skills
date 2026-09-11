---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SPEC-001
last_reviewed: 2026-09-10
domain: auth
source_prd: PRD-AUTH-001
---

# 认证规格

## SPEC-AUTH-001 — 手机验证码登录
- Source: PRD-AUTH-001
- State: provisional
- Actors: 学员、教练
- Requirement: 系统须验证手机号和一次性验证码；过期、错误、频控或供应商失败时不得建立会话。
- Acceptance method: 自动化验证码生命周期、频控、枚举防护与会话测试；真机短信联调。

### Scenario: 有效验证码
- **GIVEN** 用户请求了仍有效且匹配该手机号的验证码
- **WHEN** 用户提交验证码
- **THEN** 系统建立相应角色会话且不回显验证码

### Scenario: 错误、过期或渠道失败
- **GIVEN** 验证码无效/过期，或短信渠道不可用
- **WHEN** 用户请求或提交验证码
- **THEN** 系统不登录，以不泄露账号存在性的方式说明重试/等待路径

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-AUTH-001 | 确认短信供应商、验证码时效/频控、教练开通和会话策略 | security/product owner | 集成前 | implementation-ready | pending |
