---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SPEC-001
last_reviewed: 2026-09-10
domain: booking
source_prd: PRD-BOOKING-001
---

# 排期与预约行为规格

## SPEC-SCHEDULE-001 — 发布可预约时段

- Source: PRD-SCHEDULE-001
- State: provisional
- Actors: 已登录教练
- Requirement: 教练可保存并发布有效时段；系统显示保存后的值和发布状态。
- Acceptance method: 自动化字段、冲突与授权测试；管理端人工流程验收。

### Scenario: 发布有效时段
- **GIVEN** 教练已登录且开始、结束与容量有效
- **WHEN** 教练发布时段
- **THEN** 管理端显示已发布，学员端可查询该时段

### Scenario: 拒绝无效时段
- **GIVEN** 结束时间不晚于开始时间或与规则冲突
- **WHEN** 教练保存
- **THEN** 系统不发布，并指出需修正的字段

## SPEC-BOOKING-001 — 创建预约

- Source: PRD-BOOKING-001
- State: provisional
- Actors: 学员
- Requirement: 学员可预约可用时段，系统必须原子地防止超出容量。
- Acceptance method: 自动化并发、重复提交与校验测试；手机网页人工验收。

### Scenario: 预约仍有容量的时段
- **GIVEN** 时段已发布且仍有容量
- **WHEN** 学员提交有效联系信息
- **THEN** 系统显示预约编号、状态、时段和后续操作

### Scenario: 并发占用最后容量
- **GIVEN** 多个请求竞争最后一个名额
- **WHEN** 请求被处理
- **THEN** 只有允许容量内的预约成功，其他请求得到无泄露的冲突结果

## SPEC-BOOKING-002 — 管理或取消预约

- Source: PRD-BOOKING-002
- State: provisional
- Actors: 教练、学员
- Requirement: 系统只允许已确认的角色执行合法状态转换，并显示当前结果。
- Acceptance method: 自动化状态机、授权和过期链接测试。

### Scenario: 教练查看预约
- **GIVEN** 教练会话有效
- **WHEN** 教练打开预约列表
- **THEN** 系统只显示该教练有权管理的预约

### Scenario: 无效取消
- **GIVEN** 预约已取消、规则禁止取消或链接无效
- **WHEN** 学员尝试取消
- **THEN** 系统保持当前状态并说明可采取的下一步

## SPEC-ACCESS-001 — 隔离管理数据

- Source: PRD-ACCESS-001
- State: provisional
- Actors: 访客、教练
- Requirement: 管理接口必须验证身份与资源所有权，公开页不得返回学员名单。
- Acceptance method: 自动化角色矩阵与直接 URL/API 访问测试。

### Scenario: 授权管理
- **GIVEN** 教练已认证且资源归其所有
- **WHEN** 请求管理资源
- **THEN** 系统允许相应操作并显示结果

### Scenario: 越权访问
- **GIVEN** 身份无效或资源不归该教练
- **WHEN** 请求管理资源
- **THEN** 系统拒绝访问且不返回受限数据

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-BOOKING-001 | 确认容量、缓冲、重复预约、取消与通知行为 | product-owner | 实现前 | implementation-ready | pending |
