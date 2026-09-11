---
blueprint_kind: domain-spec
blueprint_status: draft
owner: ai-lead
last_reviewed: 2026-09-10
domain: ai-assist
source_prd: PRD-AI-001, PRD-APPROVAL-001, PRD-PRIVACY-001, PRD-DEGRADE-001, PRD-COST-001
---

# AI Assist 行为规格

## SPEC-AI-001 — 流式生成可引用草稿

- Source: PRD-AI-001
- State: confirmed
- Actors: 已授权坐席
- Preconditions: 坐席打开有效会话且租户 AI 功能可用。
- Requirement: 请求生成后，系统逐步显示草稿，并将使用的企业知识来源与草稿关联。
- Acceptance method: 端到端流式测试；代表性负载下验证首 token P95 ≤ 2 秒。

### Scenario: 正常生成

- **GIVEN** 当前租户有已发布知识且模型可用
- **WHEN** 坐席请求草稿
- **THEN** 界面流式显示草稿、生成状态和可核对的知识引用

### Scenario: 无可用知识

- **GIVEN** 检索没有达到相关性阈值的知识
- **WHEN** 坐席请求草稿
- **THEN** 系统明确提示“未找到可靠知识”，不伪造企业引用，坐席仍可人工输入

## SPEC-AI-002 — 故障时退化为人工模式

- Source: PRD-AI-001, PRD-DEGRADE-001
- State: confirmed
- Actors: 坐席
- Preconditions: 会话本身可用。
- Requirement: 模型超时、限流或不可用时，系统终止该次草稿流、显示可恢复错误并保持人工聊天可用。
- Acceptance method: 超时、限流、断流和熔断故障注入测试。

### Scenario: 模型超时

- **GIVEN** 模型没有在配置的首 token 截止时间内响应
- **WHEN** 草稿请求超时
- **THEN** 坐席看到 AI 不可用提示、可重试或继续人工回复，访客不受影响

### Scenario: 中途断流

- **GIVEN** 草稿已显示部分 token
- **WHEN** 模型流中断
- **THEN** 部分内容标记为“不完整且未确认”，不会自动发送

## SPEC-AI-003 — 坐席确认是唯一发送入口

- Source: PRD-APPROVAL-001
- State: confirmed
- Actors: 已授权坐席
- Preconditions: 草稿生成中或已完成。
- Requirement: 系统必须把草稿与已发送消息分离；仅坐席对最终文本执行确认发送后，访客端才可见。
- Acceptance method: API 权限、状态机和端到端负向测试。

### Scenario: 编辑并确认

- **GIVEN** 坐席收到 AI 草稿
- **WHEN** 坐席编辑文本并点击确认发送
- **THEN** 访客只看到编辑后的最终文本，审计记录保存确认者与草稿版本

### Scenario: 未确认或越权

- **GIVEN** 草稿未确认或请求者无会话发送权限
- **WHEN** 客户端尝试提交草稿为消息
- **THEN** 服务端拒绝，访客端没有新消息并产生安全审计事件

## SPEC-AI-004 — 数据使用透明和租户隔离

- Source: PRD-PRIVACY-001
- State: confirmed
- Actors: 企业管理员、坐席
- Preconditions: 企业数据将进入检索或模型上下文。
- Requirement: 系统仅向已批准且承诺不用于训练的供应商发送必要上下文，并允许管理员查看供应商状态与数据政策配置。
- Acceptance method: 配置审计、供应商合同检查和跨租户隔离测试。

### Scenario: 合规配置

- **GIVEN** 供应商合同与租户配置均已批准
- **WHEN** 坐席请求草稿
- **THEN** 仅当前租户的最小必要数据被处理并留下可关联审计记录

### Scenario: 供应商不合规

- **GIVEN** 供应商训练使用或保留政策未获批准
- **WHEN** 坐席请求草稿
- **THEN** 系统不发送企业数据并退化为人工模式

## SPEC-AI-005 — 预算护栏不阻断人工聊天

- Source: PRD-COST-001
- State: confirmed
- Actors: 管理员、坐席
- Preconditions: 月度 AI 或基础设施用量达到配置阈值。
- Requirement: 系统必须展示用量；达到硬限额时可暂停新草稿生成，但不得暂停人工聊天。
- Acceptance method: 账单用量模拟与限额测试。

### Scenario: 达到 AI 硬限额

- **GIVEN** 当月 AI 可变支出达到硬限额
- **WHEN** 坐席请求新草稿
- **THEN** 系统提示预算限制并保持人工输入和发送可用

### Scenario: 进入预警区间

- **GIVEN** 预测总支出超过预算预警线
- **WHEN** 管理员查看运营面板
- **THEN** 系统显示预测、主要成本驱动和建议动作

## Domain invariants

| Rule | Observable effect | State |
|---|---|---|
| AI 仅提供草稿 | 永不自动外发 | confirmed |
| 任何 AI 故障均为可见且可人工绕过 | 聊天主流程保持可用 | confirmed |

## 待决定事项

无。
