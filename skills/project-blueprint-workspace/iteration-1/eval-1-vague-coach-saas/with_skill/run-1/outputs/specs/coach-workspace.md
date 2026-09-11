---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: coach-workspace
source_prd: PRD-COACH-001, PRD-ACCESS-001
---

# Coach Workspace 行为规格

## SPEC-COACH-001 — 教练查看自己的预约

- Source: PRD-COACH-001
- State: provisional
- Actors: 已认证且获工作区授权的教练
- Preconditions: 工作区已有预约，或尚无预约。
- Requirement: 系统必须在网页管理端展示当前教练工作区的预约列表和单条预约所需详情，并明确加载、空和失败状态。
- Acceptance method: 自动化授权/API 测试与管理端手动任务测试。

### Scenario: 查看已有预约

- **GIVEN** 当前教练工作区存在预约
- **WHEN** 教练打开预约列表并选择一条预约
- **THEN** 系统显示属于该工作区的预约摘要与详情，字段范围按最终数据决策执行

### Scenario: 没有预约

- **GIVEN** 当前教练工作区没有预约
- **WHEN** 教练打开预约列表
- **THEN** 系统显示明确空状态，而非错误或永久加载状态

### Scenario: 列表加载失败

- **GIVEN** 系统暂时无法返回预约列表
- **WHEN** 教练打开或重试列表
- **THEN** 系统显示失败状态与重试入口，不把旧数据误示为最新结果

## SPEC-ACCESS-001 — 教练工作区隔离

- Source: PRD-ACCESS-001
- State: provisional
- Actors: 教练、未认证访问者
- Preconditions: 系统存在至少两个不同工作区，或请求未携带有效教练身份。
- Requirement: 所有教练管理行为必须要求认证并按工作区授权；请求者不得读取或修改其他工作区的数据。
- Acceptance method: 自动化认证、对象级授权和跨工作区负向测试；安全评审抽查。

### Scenario: 已授权访问

- **GIVEN** 教练已认证并请求自己工作区中的资源
- **WHEN** 教练执行其角色允许的管理操作
- **THEN** 系统只返回或修改该工作区的数据

### Scenario: 跨工作区访问

- **GIVEN** 已认证教练请求另一个工作区的资源标识
- **WHEN** 系统处理请求
- **THEN** 系统拒绝访问且不返回目标数据内容

### Scenario: 未认证访问

- **GIVEN** 请求者没有有效教练会话
- **WHEN** 请求管理端受保护资源
- **THEN** 系统要求认证或返回拒绝结果，不展示工作区数据

## 领域不变量

| Rule | 可观察效果 | State |
|---|---|---|
| 默认拒绝 | 没有明确工作区授权就不能观察或改变管理数据 | provisional |
| 空状态可区分 | “无预约”和“无法读取预约”使用不同状态 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IDENTITY-001 | 确认教练登录方式、学员身份/必填信息与公开页访问模式 | 产品与安全负责人（未指定） | 身份与预约实现前 | implementation-ready | pending |

