---
blueprint_kind: domain-spec
blueprint_status: draft
owner: bookstore-owner
last_reviewed: 2026-09-10
domain: catalog
source_prd: PRD-CATALOG-001
---

# 库存与检索行为规格

## SPEC-CATALOG-001 — 管理单册

- Source: PRD-CATALOG-001
- State: provisional
- Actors: 已登录店员
- Requirement: 系统必须允许店员创建和修改单册，并在保存后显示当前值与结果。
- Acceptance method: 自动化权限、字段校验与持久化测试；桌面流程人工验收。

### Scenario: 保存有效单册

- **GIVEN** 店员已登录且必填书目信息、品相、价格和状态有效
- **WHEN** 店员保存
- **THEN** 系统显示已保存记录及可检索的单册编号

### Scenario: 拒绝无效或冲突修改

- **GIVEN** 字段无效或记录已被另一店员更新
- **WHEN** 店员保存
- **THEN** 系统不覆盖较新数据，并指出需修正或重新载入的字段

## SPEC-SEARCH-001 — 检索公开库存

- Source: PRD-SEARCH-001
- State: provisional
- Actors: 顾客
- Requirement: 系统必须支持题名、作者或 ISBN 检索，结果只显示公开字段和当前可预订性。
- Acceptance method: 自动化搜索/权限测试；目标手机宽度人工验收。

### Scenario: 查看匹配单册

- **GIVEN** 公开目录存在匹配单册
- **WHEN** 顾客搜索并选择结果
- **THEN** 系统显示书目、各单册品相、价格和可预订状态

### Scenario: 无结果或连接失败

- **GIVEN** 没有匹配项或请求失败
- **WHEN** 顾客提交搜索
- **THEN** 系统分别显示调整关键词建议或保留查询的重试操作

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-CATALOG-001 | 确认必填字段、品相词表、批量导入和检索容错 | bookstore-owner | 实现前 | implementation-ready | pending |
