---
blueprint_kind: domain-spec
blueprint_status: draft
owner: accessibility-lead
last_reviewed: 2026-09-10
domain: accessibility
source_prd: PRD-ACCESS-001
---

# 无障碍行为规格

## SPEC-ACCESS-001 — 屏幕阅读器理解状态变化

- Source: PRD-ACCESS-001
- State: confirmed
- Actors: 使用屏幕阅读器的参与者或组织者
- Preconditions: 用户位于报名、提交、审核或举报流程。
- Requirement: 控件必须有可感知名称、角色和值；异步状态变化必须以简短文字公告，不重复朗读装饰内容。
- Acceptance method: 对支持矩阵内的浏览器与屏幕阅读器组合执行人工任务测试，并保留测试记录。

### Scenario: 完成记录成功公告

- **GIVEN** 屏幕阅读器已开启且用户提交有效记录
- **WHEN** 系统确认保存成功
- **THEN** 辅助技术只需听到独立完整的成功文字即可理解结果，焦点不被强制移到通知上

### Scenario: 公告失败

- **GIVEN** 屏幕阅读器未自动读出异步消息
- **WHEN** 用户继续浏览页面
- **THEN** 成功或错误文字仍位于语义结构和焦点顺序中，可被再次找到

## SPEC-ACCESS-002 — 非颜色操作与多输入支持

- Source: PRD-ACCESS-001
- State: confirmed
- Actors: 键盘、触控、放大或低视力用户
- Requirement: 状态同时使用文字与程序化语义；所有核心操作可用键盘和触控完成，焦点可见且顺序符合阅读顺序。
- Acceptance method: 仅键盘全流程、触控目标检查、高对比度/无颜色检查及 200% 文本缩放人工测试。

### Scenario: 不依赖颜色识别核验状态

- **GIVEN** 页面颜色被移除或用户无法区分状态色
- **WHEN** 用户查看完成记录
- **THEN** 用户仍可从可见文字及语义状态区分待核验、已通过与需补充

### Scenario: 键盘提交

- **GIVEN** 用户不使用指针设备
- **WHEN** 用户按阅读顺序操作报名和提交表单
- **THEN** 每个交互控件均可到达和激活，焦点样式清晰，错误摘要可定位到对应字段

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ACCESS-001 | 确认支持的浏览器、屏幕阅读器和设备测试矩阵 | accessibility and QA leads | 首轮可用性测试前 | implementation-ready | pending |
