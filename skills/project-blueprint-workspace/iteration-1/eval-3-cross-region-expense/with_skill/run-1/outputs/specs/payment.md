---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PAYMENT-001
last_reviewed: 2026-09-10
domain: payment
source_prd: PRD-PAYMENT-001
---

# 第三方支付行为规格

## SPEC-PAYMENT-001 — 发起一次付款

- Source: PRD-PAYMENT-001
- State: provisional
- Actors: 财务授权角色、系统
- Preconditions: 费用处于可付款状态，收款账户通过所需验证，操作者有权限。
- Requirement: 系统必须为同一获批费用创建至多一个有效付款意图，以幂等方式提交供应商，并展示“处理中”而非把接单误报为到账。
- Acceptance method: 供应商沙箱契约测试、超时/重试/并发故障注入和账务对账测试。

### Scenario: 供应商接单

- **GIVEN** 费用可付款且供应商接受请求
- **WHEN** 授权角色发起付款
- **THEN** 系统显示处理中，保存供应商引用和审计事件，不显示已到账

### Scenario: 请求超时

- **GIVEN** 平台无法判断供应商是否已接单
- **WHEN** 调用超时
- **THEN** 系统保持待确认状态，通过相同幂等键查询/重试，禁止再次人工发起独立付款

## SPEC-PAYMENT-002 — 接收支付结果并对账

- Source: PRD-PAYMENT-001
- State: provisional
- Actors: 第三方支付服务、财务授权角色
- Preconditions: 存在付款意图或收到需人工核对的供应商事件。
- Requirement: 系统必须验证回调真实性、去重、关联租户与付款意图，并仅按允许的状态迁移更新结果；不一致进入人工复核。
- Acceptance method: 签名、重放、乱序、未知事件、拒付和对账差异测试。

### Scenario: 有效终态回调

- **GIVEN** 回调签名有效且关联到本区域本租户的处理中付款
- **WHEN** 供应商报告成功或失败终态
- **THEN** 系统更新一次终态、记录证据并通知授权用户

### Scenario: 重放或乱序回调

- **GIVEN** 回调已处理或会使状态非法回退
- **WHEN** 系统再次收到该事件
- **THEN** 系统不重复付款、不回退终态，记录去重或异常结果

### Scenario: 关联不明

- **GIVEN** 事件签名有效但无法安全关联唯一租户和付款意图
- **WHEN** 系统收到回调
- **THEN** 系统不改变付款状态，将事件隔离供人工复核且不跨区复制敏感内容

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 接单不等于到账 | 用户看到区分明确的处理中与终态 | confirmed |
| 付款操作幂等 | 网络重试不创建第二笔付款 | confirmed |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PAYMENT-001 | 按中/欧/美确认支付供应商、资金流责任、账户字段、回调与退出方案 | 支付产品、法务、安全负责人 | 支付模块实现前 | implementation-ready | pending |

