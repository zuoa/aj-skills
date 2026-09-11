---
blueprint_kind: domain-spec
blueprint_status: draft
owner: accessibility-lead
last_reviewed: 2026-09-10
domain: accessibility
source_prd: PRD-ACCESS-001
---

# 无障碍行为规格

## SPEC-ACCESS-001 — 屏幕阅读器状态公告

- Source: PRD-ACCESS-001
- State: confirmed
- Actors: 使用屏幕阅读器的用户
- Requirement: 控件有可感知名称、角色和值，异步结果以独立完整文字公告。
- Acceptance method: 支持矩阵中的屏幕阅读器人工测试。

### Scenario: 提交成功

- **GIVEN** 屏幕阅读器开启且用户提交有效记录
- **WHEN** 系统保存成功
- **THEN** 屏幕阅读器公告完整成功文字且不依赖装饰符号理解结果

### Scenario: 未自动公告

- **GIVEN** 实时公告未被辅助技术读出
- **WHEN** 用户继续浏览页面
- **THEN** 结果文字仍在语义结构和焦点顺序中可找到

## SPEC-ACCESS-002 — 非图形状态与输入方式

- Source: PRD-ACCESS-001
- State: confirmed
- Actors: 键盘、触控、低视力用户
- Requirement: 所有状态有文字和程序化语义；核心操作可用键盘和触控完成，焦点清楚。
- Acceptance method: 仅键盘、触控、高对比度和 200% 文本缩放人工测试。

### Scenario: 无颜色状态

- **GIVEN** 用户不能感知状态色
- **WHEN** 用户查看报名或核验结果
- **THEN** 可见文字仍能区分当前状态和下一步

### Scenario: 键盘完成流程

- **GIVEN** 用户不使用指针设备
- **WHEN** 用户从行动详情完成报名和记录提交
- **THEN** 所有控件按阅读顺序可达可操作，错误可定位到字段

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ACCESS-001 | 确认浏览器、屏幕阅读器和设备支持矩阵 | accessibility/QA | 可用性测试前 | implementation-ready | pending |
