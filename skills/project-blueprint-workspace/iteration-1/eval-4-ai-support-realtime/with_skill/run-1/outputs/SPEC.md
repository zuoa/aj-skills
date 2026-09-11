---
blueprint_kind: spec-index
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
---

# 系统行为规格

## 范围与权威

本文件拥有共享行为规则、领域索引、追踪关系和就绪度；详细可观察行为位于 `specs/`。

## 术语

| 术语 | 含义 | 来源 |
|---|---|---|
| 草稿 | 仅坐席可见、尚未获准发给访客的 AI 输出 | PRD-APPROVAL-001 |
| 确认发送 | 有权限坐席对最终文本执行的显式动作 | PRD-APPROVAL-001 |
| 首 token | 坐席界面首次呈现该次生成的非空模型文本 | PRD-AI-001 |
| 人工模式 | 不调用模型、但保留收发消息的运行模式 | PRD-DEGRADE-001 |

## 全局行为规则

| Rule ID | 可观察规则 | Source | State |
|---|---|---|---|
| RULE-001 | 未经坐席确认的草稿不会出现在访客端 | PRD-APPROVAL-001 | confirmed |
| RULE-002 | 同一消息重试不会导致访客看到重复消息 | PRD-CHAT-001 | provisional |
| RULE-003 | 所有展示和检索的数据均属于当前租户 | PRD-KB-001 | confirmed |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Chat | [specs/chat.md](specs/chat.md) | 应用负责人 | confirmed |
| AI Assist | [specs/ai-assist.md](specs/ai-assist.md) | AI 负责人 | confirmed |
| Knowledge | [specs/knowledge.md](specs/knowledge.md) | AI 负责人 | provisional |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-CHAT-001 | SPEC-CHAT-001, SPEC-CHAT-002 | DESIGN.md#会话工作台 | ARCHITECTURE.md#实时聊天与草稿动态 | planned |
| PRD-AI-001 | SPEC-AI-001, SPEC-AI-002 | DESIGN.md#会话工作台 | ARCHITECTURE.md#质量属性预算 | planned |
| PRD-APPROVAL-001 | SPEC-AI-003 | DESIGN.md#会话工作台 | ARCHITECTURE.md#模块边界 | planned |
| PRD-KB-001 | SPEC-KB-001 | DESIGN.md#知识库 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-PRIVACY-001 | SPEC-AI-004 | DESIGN.md#内容与信任提示 | SECURITY.md#AI-与企业数据控制 | planned |
| PRD-DEGRADE-001 | SPEC-AI-002, SPEC-CHAT-002 | DESIGN.md#UI-状态矩阵 | ARCHITECTURE.md#故障与演进 | planned |
| PRD-COST-001 | SPEC-AI-005 | DESIGN.md#UI-状态矩阵 | DEPLOY.md#成本与生命周期 | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | PRD.md；DESIGN.md |
| implementation-ready | ready | none | specs/；DESIGN.md；ARCHITECTURE.md；SECURITY.md；ENGINEERING.md |
| production-ready | blocked | TBD-REGION-001, TBD-METRIC-001, TBD-SECURITY-001, TBD-DEPLOY-001 | SECURITY.md；DEPLOY.md |

## 待决定事项

根索引无新增事项；阻断项在其权威文档的“待决定事项”表登记。
