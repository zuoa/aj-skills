---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与权威关系

本文件仅管理共享行为、术语、领域索引、追踪和就绪度；详细可观察行为位于 `specs/`。产品意图以 [PRD.md](PRD.md) 为准，视觉交互以 [DESIGN.md](DESIGN.md) 为准，内部机制以 [ARCHITECTURE.md](ARCHITECTURE.md) 为准。

## 术语

| 术语 | 含义 | 来源/状态 |
|---|---|---|
| 告警 | 外部观测系统提供、需要查看或处置的信号记录 | provisional，TBD-INTEGRATION-001 |
| 影响事实 | 可直接定位到系统记录源及时间的观察结果 | provisional 定义 |
| 推断 | 由规则或 AI 从证据推导、尚未经人确认的陈述 | provisional 定义 |
| 回滚目标 | 发布系统声明可恢复到的具体部署/版本 | provisional，TBD-ROLLBACK-001 |
| 终态 | 外部执行系统确认成功、失败或取消；“未知”不是成功 | provisional 定义 |

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | 状态 |
|---|---|---|---|
| GLOBAL-001 | 所有生产数据均显示来源和数据时间；超过新鲜度规则时显示“陈旧”，而非继续伪装实时 | PRD-ALERT-001 | provisional；阈值 TBD-NFR-001 |
| GLOBAL-002 | 事实、规则关联、AI 推断、人工确认与未知使用文字标签和图标区分，不只依赖颜色 | PRD-IMPACT-001 | provisional |
| GLOBAL-003 | AI 不可用、超时或被禁用时，告警查看、确定性影响证据和人工回滚流程仍可用 | PRD-AI-001 | provisional |
| GLOBAL-004 | 所有破坏性动作都明确显示环境、目标和后果；最终提交不能由 AI 或单一模糊手势触发 | PRD-ROLLBACK-001 | provisional |
| GLOBAL-005 | 时间同时显示明确时区；相对时间可作为辅助但不得替代绝对时间 | PRD-ALERT-001 | provisional |
| GLOBAL-006 | 权限不足不得隐藏原因；系统显示所需权限与安全的申请/升级路径，但不泄露敏感详情 | PRD-ROLLBACK-001 | provisional |

## 领域规格

| 领域 | 文件 | Owner | 状态 |
|---|---|---|---|
| Alerts | [specs/alerts.md](specs/alerts.md) | 产品/平台负责人 | provisional |
| Impact | [specs/impact.md](specs/impact.md) | 产品/事件管理负责人 | provisional |
| Rollback | [specs/rollback.md](specs/rollback.md) | 发布负责人 | pending：TBD-ROLLBACK-001 |
| AI Assist | [specs/ai-assist.md](specs/ai-assist.md) | AI/产品负责人 | pending：TBD-AI-001 |
| Audit | [specs/audit.md](specs/audit.md) | 安全负责人 | pending：TBD-SECURITY-001 |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-ALERT-001 | SPEC-ALERT-001, SPEC-ALERT-002 | DESIGN.md#告警工作台 | ARCHITECTURE.md#集成与接口 | planned |
| PRD-IMPACT-001 | SPEC-IMPACT-001, SPEC-IMPACT-002 | DESIGN.md#影响范围工作区 | ARCHITECTURE.md#模块边界 | planned |
| PRD-ROLLBACK-001 | SPEC-ROLLBACK-001, SPEC-ROLLBACK-002, SPEC-ROLLBACK-003 | DESIGN.md#回滚工作流 | ARCHITECTURE.md#回滚动态视图 | planned |
| PRD-AI-001 | SPEC-AI-001, SPEC-AI-002 | DESIGN.md#AI-表达规则 | ARCHITECTURE.md#AI-边界 | planned |
| PRD-AUDIT-001 | SPEC-AUDIT-001 | DESIGN.md#回滚工作流 | ARCHITECTURE.md#数据与一致性 | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PLATFORM-001 | PRD.md#核心旅程；DESIGN.md#信息架构与关键旅程 |
| implementation-ready | blocked | TBD-PRODUCT-001, TBD-PRODUCT-002, TBD-INTEGRATION-001, TBD-IDENTITY-001, TBD-ROLLBACK-001, TBD-AI-001, TBD-NFR-001, TBD-DESIGN-001, TBD-ENGINEERING-001 | specs/；DESIGN.md；ARCHITECTURE.md；ENGINEERING.md |
| production-ready | blocked | TBD-SECURITY-001, TBD-SECURITY-002, TBD-DEPLOY-001, TBD-RECOVERY-001, TBD-OPERATIONS-001 | SECURITY.md；DEPLOY.md |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-NFR-001 | 定义新鲜度、延迟、可用性、规模与降级预算 | 平台/SRE 负责人 | 架构评审前 | implementation-ready | pending |
| TBD-DESIGN-001 | 确认设计负责人、品牌约束与视觉方向 | 产品/设计负责人 | 视觉实现前 | implementation-ready | pending |
| TBD-ENGINEERING-001 | 确认团队栈、仓库和可运行命令 | 工程负责人 | 首个实现任务前 | implementation-ready | pending |
| TBD-DEPLOY-001 | 确认云/区域/环境拓扑与生产责任 | 平台负责人 | 生产设计评审前 | production-ready | pending |
| TBD-RECOVERY-001 | 定义数据类别 RTO/RPO、备份保留与恢复演练 | SRE/数据负责人 | 上线评审前 | production-ready | pending |
| TBD-OPERATIONS-001 | 定义 SLI/SLO、告警阈值、值班路由和事故沟通 | SRE 负责人 | 上线评审前 | production-ready | pending |

其余 TBD 的权威登记见 [PRD.md#待决定事项](PRD.md#待决定事项)、[SECURITY.md#待决定事项](SECURITY.md#待决定事项)、[DEPLOY.md#待决定事项](DEPLOY.md#待决定事项) 与 [ARCHITECTURE.md#待决定事项](ARCHITECTURE.md#待决定事项)。
