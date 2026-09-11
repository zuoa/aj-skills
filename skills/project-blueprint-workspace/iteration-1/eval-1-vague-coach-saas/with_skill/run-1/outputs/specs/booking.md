---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: booking
source_prd: PRD-BOOK-001, PRD-BOOK-002
---

# Booking 行为规格

## SPEC-BOOK-001 — 学员在手机网页浏览可预约时间

- Source: PRD-BOOK-001
- State: provisional
- Actors: 学员
- Preconditions: 学员进入某位教练可访问的预约页；公开或受限访问方式待 TBD-IDENTITY-001。
- Requirement: 系统必须在手机网页展示该教练当前可预约的选项，并区分加载、无可用时段和失败状态。
- Acceptance method: 代表性手机视口的自动化端到端测试及手动无障碍检查。

### Scenario: 存在可预约时段

- **GIVEN** 教练已发布至少一个仍可预约的时段
- **WHEN** 学员打开对应预约页
- **THEN** 页面以可选择形式显示该时段及不含歧义的日期/时间语境

### Scenario: 没有可预约时段

- **GIVEN** 教练当前没有可预约时段
- **WHEN** 学员打开对应预约页
- **THEN** 页面明确显示暂无可预约时间，且不把空白页面或加载态当作结果

### Scenario: 获取失败

- **GIVEN** 页面无法取得最新可预约信息
- **WHEN** 学员查看页面
- **THEN** 页面显示失败和安全的重试入口，不展示无法确认的新鲜度为“可预约”的时段

## SPEC-BOOK-002 — 学员提交预约并获得确定结果

- Source: PRD-BOOK-002
- State: provisional
- Actors: 学员
- Preconditions: 学员已选择当时显示为可预约的时段，并提供 TBD-IDENTITY-001 最终要求的信息。
- Requirement: 系统必须对一次提交返回明确结果；同一不可重复使用的时段至多产生一个有效预约，重复提交不得产生额外有效预约。
- Acceptance method: 自动化领域、并发与端到端测试；在教练端核对成功预约可见。

### Scenario: 成功预约

- **GIVEN** 所选时段仍可预约且提交信息有效
- **WHEN** 学员提交预约
- **THEN** 系统显示预约成功及足以识别该预约的摘要，且教练管理端可见同一预约

### Scenario: 并发竞争同一时段

- **GIVEN** 两位学员近同时提交同一不可重复使用的时段
- **WHEN** 系统处理两个请求
- **THEN** 至多一个请求获得成功；其他请求得到“时段已不可用”及返回选择的路径

### Scenario: 重复提交或结果重试

- **GIVEN** 同一预约提交因重复点击或网络重试被再次发送
- **WHEN** 系统识别为同一次意图
- **THEN** 系统不创建第二个有效预约，并返回一致且可理解的结果

### Scenario: 输入无效

- **GIVEN** 必填信息缺失或格式不符合已确认规则
- **WHEN** 学员提交预约
- **THEN** 系统不创建预约，并在相应字段给出可修正反馈

## 领域不变量

| Rule | 可观察效果 | State |
|---|---|---|
| 确定结果 | 学员不会同时看到成功与失败，也不会因服务错误被告知成功 | provisional |
| 不重复占用 | 单容量时段至多有一个有效预约 | provisional，容量模型待 TBD-BOOK-001 |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IDENTITY-001 | 确认教练登录方式、学员身份/必填信息与公开页访问模式 | 产品与安全负责人（未指定） | 身份与预约实现前 | implementation-ready | pending |
| TBD-NOTIFY-001 | 确认预约结果是否还需邮件/短信/站内通知及送达语义 | 产品负责人（未指定） | 预约闭环签署前 | implementation-ready | pending |

