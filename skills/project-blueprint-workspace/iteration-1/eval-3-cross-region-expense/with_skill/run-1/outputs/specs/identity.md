---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
domain: identity
source_prd: PRD-IDENTITY-001
---

# 身份与租户访问行为规格

## SPEC-IDENTITY-001 — 租户 SSO 登录

- Source: PRD-IDENTITY-001
- State: provisional
- Actors: 企业用户、企业管理员
- Preconditions: 租户已启用并配置 SSO，用户由租户入口或租户标识开始登录。
- Requirement: 系统必须只接受与目标租户配置匹配的身份断言，将用户绑定到唯一租户身份，并在登录失败时避免泄露其他租户配置。
- Acceptance method: SSO 契约测试、错误断言与跨租户渗透测试；配置变更人工演练。

### Scenario: 成功登录

- **GIVEN** IdP 返回有效、未过期且面向本租户的断言，用户映射有效
- **WHEN** 用户完成登录
- **THEN** 系统建立只属于该租户的会话并显示获授权功能

### Scenario: 错误租户或断言

- **GIVEN** 断言的发行者、受众、签名或租户映射不匹配
- **WHEN** 系统处理回调
- **THEN** 系统拒绝登录、记录安全事件，并向用户显示通用错误

### Scenario: IdP 不可用

- **GIVEN** 租户 IdP 超时或不可达
- **WHEN** 用户登录
- **THEN** 系统不得绕过 SSO；显示可重试状态和企业支持路径

## SPEC-IDENTITY-002 — 角色变更与紧急访问

- Source: PRD-IDENTITY-001
- State: provisional
- Actors: 企业管理员、平台授权支持人员
- Preconditions: 操作者已通过强认证并具有相应管理权限。
- Requirement: 角色和成员状态变更必须在本租户内生效并产生审计记录；紧急访问必须限时、审批、强认证且全量审计。
- Acceptance method: 停用时效、会话撤销、提权、紧急访问与审计测试。

### Scenario: 停用用户

- **GIVEN** 用户已被租户管理员或身份生命周期流程停用
- **WHEN** 用户再次访问或刷新会话
- **THEN** 系统在批准的传播时限内撤销访问，不影响同标识在其他租户的独立身份

### Scenario: 未授权提权

- **GIVEN** 操作者没有角色管理权限
- **WHEN** 操作者尝试提升自己或他人权限
- **THEN** 系统拒绝并记录安全审计事件

### Scenario: 紧急管理员访问

- **GIVEN** 企业 SSO 故障且满足紧急访问前置审批
- **WHEN** 授权人员启用紧急会话
- **THEN** 系统要求强认证、限制时长和范围，并向安全负责人产生告警

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 身份不跨租户继承权限 | 相同邮箱也需各租户独立授权 | confirmed |
| SSO 故障不自动降级为弱认证 | 普通用户不能绕过企业 IdP | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IDENTITY-001 | 确认首发协议（OIDC/SAML）、SCIM 范围、停用时限、MFA 与紧急访问审批 | 身份与安全负责人 | 身份模块实现前 | implementation-ready | pending |

