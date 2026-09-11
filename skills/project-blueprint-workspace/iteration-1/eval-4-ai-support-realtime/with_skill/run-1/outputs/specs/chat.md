---
blueprint_kind: domain-spec
blueprint_status: draft
owner: app-lead
last_reviewed: 2026-09-10
domain: chat
source_prd: PRD-CHAT-001
---

# Chat 行为规格

## SPEC-CHAT-001 — 接收与发送人工消息

- Source: PRD-CHAT-001
- State: confirmed
- Actors: 访客、已授权坐席
- Preconditions: 双方处于同一有效租户会话。
- Requirement: 系统必须把已持久化的访客消息推送到坐席，并仅把坐席明确发送的最终文本推送给访客。
- Acceptance method: 端到端自动化测试与 3000 连接压测。

### Scenario: 正常双向聊天

- **GIVEN** 访客与坐席均在线且会话有效
- **WHEN** 任一方发送文本消息
- **THEN** 对方看到一次该消息，刷新后历史记录保持一致

### Scenario: 重复提交

- **GIVEN** 客户端因超时使用同一幂等键重试
- **WHEN** 服务端再次收到发送请求
- **THEN** 会话历史和对端只出现一条消息

## SPEC-CHAT-002 — 断线恢复和人工可用性

- Source: PRD-CHAT-001, PRD-DEGRADE-001
- State: confirmed
- Actors: 访客、坐席
- Preconditions: 会话仍有效。
- Requirement: 实时连接中断后，客户端必须显示连接状态、自动重连，并从持久化游标补齐缺失消息；模型故障不得阻止人工消息。
- Acceptance method: 网络故障与模型故障注入测试。

### Scenario: 网络恢复

- **GIVEN** 客户端断线期间产生了新消息
- **WHEN** 连接恢复并携带最后确认游标
- **THEN** 缺失消息按会话顺序补齐且不重复

### Scenario: 模型不可用

- **GIVEN** AI 草稿服务处于不可用状态
- **WHEN** 坐席输入并发送人工文本
- **THEN** 访客正常收到消息且界面明确显示 AI 暂不可用

## Domain invariants

| Rule | Observable effect | State |
|---|---|---|
| 消息带稳定 ID 和租户/会话归属 | 重试不重复、跨租户不可见 | confirmed |

## 待决定事项

无。
