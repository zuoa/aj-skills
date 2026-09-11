---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: expense
source_prd: PRD-EXPENSE-001
---

# 费用与发票行为规格

## SPEC-EXPENSE-001 — 创建并提交费用

- Source: PRD-EXPENSE-001
- State: provisional
- Actors: 员工
- Preconditions: 用户已登录正确租户；租户允许该用户提交费用。
- Requirement: 系统必须让员工在 Web、iOS、Android 创建草稿、上传发票、填写必填字段并提交；成功提交后记录不可歧义的状态和提交时间。
- Acceptance method: 三端契约测试与端到端测试；产品人工核对状态文案。

### Scenario: 成功提交

- **GIVEN** 员工拥有提交权限，发票与字段满足当前规则
- **WHEN** 员工确认提交
- **THEN** 系统只创建一次已提交费用，显示编号、状态和提交时间，并阻止员工静默修改已提交版本

### Scenario: 校验失败

- **GIVEN** 必填字段缺失、金额格式错误或文件不满足策略
- **WHEN** 员工提交
- **THEN** 系统保持草稿，定位可修复问题，不创建审批任务

### Scenario: 重复请求

- **GIVEN** 同一次提交因网络重试被重复发送
- **WHEN** 系统收到相同幂等标识
- **THEN** 系统返回同一费用结果且只生成一个审批任务

## SPEC-EXPENSE-002 — 发票上传与离线边界

- Source: PRD-EXPENSE-001
- State: provisional
- Actors: 员工
- Preconditions: 用户正在编辑费用草稿。
- Requirement: 系统必须显示上传进度和安全扫描状态；未完成或未通过扫描的文件不能随费用提交。移动端离线时不得声称提交成功。
- Acceptance method: 恶意/超限/中断文件测试、弱网与离线移动端测试。

### Scenario: 安全上传

- **GIVEN** 文件类型、大小符合租户策略且安全扫描通过
- **WHEN** 上传完成
- **THEN** 系统将文件标为可提交并提供预览或可访问的文件信息

### Scenario: 可疑文件

- **GIVEN** 文件扫描失败、超时或判定为不安全
- **WHEN** 员工尝试提交
- **THEN** 系统隔离文件、阻止提交、给出不暴露扫描内部细节的错误与重试/替换路径

### Scenario: 移动端离线

- **GIVEN** 设备无网络
- **WHEN** 员工点击提交
- **THEN** 系统明确显示尚未提交；若启用离线草稿，仅本地保存且恢复联网后要求用户再次确认

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 已提交版本不可被提交人静默覆盖 | 修改必须形成退回后的新版本并保留前一版本 | provisional |
| 文件状态属于费用可提交条件 | 扫描未通过时无审批任务 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-EXPENSE-001 | 确认文件类型、大小、张数、字段和重复发票规则 | 产品与安全负责人 | 费用模块实现前 | implementation-ready | pending |

