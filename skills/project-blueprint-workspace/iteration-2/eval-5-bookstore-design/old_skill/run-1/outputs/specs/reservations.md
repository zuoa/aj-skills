---
blueprint_kind: domain-spec
blueprint_status: draft
owner: bookstore-owner
last_reviewed: 2026-09-10
domain: reservations
source_prd: PRD-RESERVE-001
---

# 预订与访问行为规格

## SPEC-RESERVE-001 — 提交单册预订

- Source: PRD-RESERVE-001
- State: provisional
- Actors: 顾客
- Requirement: 系统必须对指定单册提交预订，并原子地防止重复有效预订。
- Acceptance method: 自动化并发、校验与隐私测试；手机流程人工验收。

### Scenario: 预订可用单册

- **GIVEN** 单册可预订且顾客提交所需联系方式
- **WHEN** 顾客确认预订
- **THEN** 系统显示预订编号、当前状态和后续步骤

### Scenario: 并发冲突

- **GIVEN** 两位顾客几乎同时预订同一单册
- **WHEN** 请求被处理
- **THEN** 仅一项成为有效预订，另一项收到无泄露的不可预订说明

## SPEC-RESERVE-002 — 处理预订队列

- Source: PRD-RESERVE-002
- State: provisional
- Actors: 已登录店员
- Requirement: 系统必须只允许合法状态转换，并记录可见的操作者和时间。
- Acceptance method: 自动化状态机、权限和审计测试；桌面队列人工验收。

### Scenario: 确认预订

- **GIVEN** 预订处于待处理状态
- **WHEN** 店员确认
- **THEN** 队列和详情显示已确认状态及审计记录

### Scenario: 过期记录被再次操作

- **GIVEN** 预订已过期或被其他店员处理
- **WHEN** 店员尝试确认
- **THEN** 系统不覆盖当前状态，并提示刷新后的结果

## SPEC-ACCESS-001 — 隔离公开与店内数据

- Source: PRD-ACCESS-001
- State: provisional
- Actors: 顾客、店员
- Requirement: 系统必须按角色限制目录、顾客资料和管理操作的可见范围。
- Acceptance method: 自动化授权矩阵和直接 URL 访问测试。

### Scenario: 店员访问管理页

- **GIVEN** 店员身份有效
- **WHEN** 进入库存或预订管理页
- **THEN** 系统显示其角色允许的管理功能

### Scenario: 未授权访问

- **GIVEN** 访客没有有效店员会话
- **WHEN** 直接请求管理资源
- **THEN** 系统拒绝访问且不返回受限数据

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-RESERVE-001 | 确认联系方式、有效期、通知、取消与取书规则 | bookstore-owner | 实现前 | implementation-ready | pending |
