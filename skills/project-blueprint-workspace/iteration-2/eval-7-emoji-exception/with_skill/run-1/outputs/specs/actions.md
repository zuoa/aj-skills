---
blueprint_kind: domain-spec
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
domain: actions
source_prd: PRD-ACTION-001; PRD-ACTION-002
---

# 行动领域行为规格

## SPEC-ACTION-001 — 报名与取消报名

- Source: PRD-ACTION-001
- State: confirmed
- Actors: 已登录青少年参与者
- Preconditions: 行动可报名，用户满足已公布条件。
- Requirement: 系统必须显示当前报名状态；报名或取消后返回文字结果，重复激活不得产生重复记录。
- Acceptance method: 自动化状态转换测试，加屏幕阅读器、键盘和触控人工测试。

### Scenario: 报名成功

- **GIVEN** 用户尚未报名且行动有名额
- **WHEN** 用户激活带有可见文字的“报名参加”操作
- **THEN** 页面显示“已报名”，该变化通过礼貌级实时区域公告，刷新后仍保持一致

### Scenario: 名额刚被占满

- **GIVEN** 用户查看页面时仍有名额，但提交前名额已满
- **WHEN** 用户提交报名
- **THEN** 系统不创建报名，并以文字说明“名额已满”及返回行动列表的下一步

## SPEC-ACTION-002 — 提交线下行动完成记录

- Source: PRD-ACTION-002
- State: confirmed
- Actors: 已报名参与者
- Preconditions: 行动已开始，用户可以填写完成说明并按规则添加证据。
- Requirement: 系统必须保存一条可核验记录，并以独立可理解的文字告知提交结果；装饰不得成为状态的唯一载体。
- Acceptance method: 自动化提交/幂等测试；屏幕阅读器公告人工测试。

### Scenario: 提交成功

- **GIVEN** 用户完成线下行动并填写有效记录
- **WHEN** 用户激活“提交完成记录”
- **THEN** 系统只创建一条记录，焦点保持在可预测位置，并显示及公告“行动已记录，感谢你的参与。”

### Scenario: 网络失败

- **GIVEN** 提交内容已填写且网络中断
- **WHEN** 用户尝试提交
- **THEN** 系统不宣称成功，保留可恢复草稿，并以文字说明未提交及重试方式

## SPEC-ACTION-003 — 核验结果

- Source: PRD-ACTION-002
- State: provisional
- Actors: 组织者、参与者
- Requirement: 核验结果必须是“待核验”“已通过”或“需补充”之一，并显示结果文字、更新时间和可用下一步。
- Acceptance method: 自动化权限和状态测试；参与者通知人工测试。

### Scenario: 通过记录

- **GIVEN** 组织者有核验权限且记录待核验
- **WHEN** 组织者选择“通过”并确认
- **THEN** 参与者看到“已通过”文字，屏幕阅读器读取状态和更新时间

### Scenario: 无权核验

- **GIVEN** 登录用户不是该行动的授权组织者
- **WHEN** 用户访问核验操作
- **THEN** 系统不展示或执行该操作，并返回不泄露记录细节的权限错误

## 领域不变量

| 规则 | 可观察效果 | State |
|---|---|---|
| 报名与完成记录均幂等 | 重复激活不会产生多个对象 | confirmed |
| 状态有文字等价表达 | 去除颜色、图标和动效后含义仍完整 | confirmed |

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ACTION-001 | 确认证据类型、文件上限与核验时效 | product and safety leads | 交互定稿前 | implementation-ready | pending |
