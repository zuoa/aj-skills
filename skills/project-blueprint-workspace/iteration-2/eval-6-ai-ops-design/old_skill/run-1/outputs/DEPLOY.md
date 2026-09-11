---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-001
last_reviewed: 2026-09-10
---

# 部署与运行

## 拓扑与环境

以 Web、模块化 API/worker 和关系型数据库作为 provisional 单一发布基线；云、区域、网络和托管服务由 `TBD-DEPLOY-001` 决定。

| 环境 | 数据/访问 | 晋级规则 |
|---|---|---|
| local/preview | 合成或脱敏数据；无生产执行凭据 | 开发验证 |
| staging | 生产形态、非生产目标 | 同一不可变构建物通过规格、权限、迁移和回滚演练 |
| production | 最小权限、受控 break-glass | 审批和分阶段发布 |

## CI/CD 与可观测性

- 构建物记录提交、依赖和来源证明，逐环境晋级。
- 数据变更采用 expand/contract；无已验证恢复路径时不得发布。
- 观测告警/证据新鲜度、回滚受理与未知终态、授权拒绝、审计写入，以及启用后 AI 的质量、延迟和成本。
- 控制台故障时必须存在独立、受审计的手工恢复路径。

## 备份、恢复与成本

确认/操作/审计记录和可重建投影应分别定义备份策略；RTO、RPO、保留与演练见 `TBD-RECOVERY-001`。SLI/SLO、阈值、路由和事故沟通见 `TBD-OPERATIONS-001`。容量和成本上限随 `TBD-PRODUCT-001` 确认。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认云、区域、网络、环境拓扑和生产责任 | 平台负责人 | 部署设计前 | production-ready | pending |
| TBD-RECOVERY-001 | 定义各数据类别 RTO/RPO、备份保留和恢复演练 | SRE/数据负责人 | 上线评审前 | production-ready | pending |
| TBD-OPERATIONS-001 | 定义用户中心 SLI/SLO、阈值、值班路由和事故沟通 | SRE 负责人 | 生产演练前 | production-ready | pending |
