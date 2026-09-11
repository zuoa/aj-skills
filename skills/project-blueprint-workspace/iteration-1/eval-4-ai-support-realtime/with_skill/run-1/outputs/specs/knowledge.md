---
blueprint_kind: domain-spec
blueprint_status: draft
owner: ai-lead
last_reviewed: 2026-09-10
domain: knowledge
source_prd: PRD-KB-001
---

# Knowledge 行为规格

## SPEC-KB-001 — 发布、撤回与隔离企业知识

- Source: PRD-KB-001
- State: provisional
- Actors: 企业知识库管理员
- Preconditions: 管理员属于目标租户并有知识管理权限。
- Requirement: 管理员可摄取、发布和撤回知识版本；仅已发布的当前租户内容可用于新草稿。
- Acceptance method: 权限、版本切换、删除传播和跨租户检索自动化测试。

### Scenario: 发布新版本

- **GIVEN** 新资料已完成处理但尚未发布
- **WHEN** 管理员发布该版本
- **THEN** 后续草稿可引用新版本且引用包含来源与版本

### Scenario: 撤回资料

- **GIVEN** 某资料当前可被检索
- **WHEN** 管理员撤回该资料
- **THEN** 新草稿不再检索该资料，历史审计仍能解释过去使用的版本

### Scenario: 跨租户请求

- **GIVEN** 用户请求其租户以外的知识
- **WHEN** 系统执行检索
- **THEN** 返回拒绝或空结果且记录安全审计，不泄露内容或元数据

## Domain invariants

| Rule | Observable effect | State |
|---|---|---|
| 未发布或已撤回内容不可用于新草稿 | 管理员能控制生效知识集合 | provisional |

## 待决定事项

无。
