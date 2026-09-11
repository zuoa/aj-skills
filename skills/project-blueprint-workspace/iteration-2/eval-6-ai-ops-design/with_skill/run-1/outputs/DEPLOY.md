---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-002
last_reviewed: 2026-09-10
---

# 部署与运行

## 运行拓扑与环境

首版以一个 Web 客户端、一个模块化 API/worker 发布单元和一个关系型数据库为 provisional 基线；云、区域、网络边界和托管服务由 `TBD-DEPLOY-002` 决定。

| 环境 | 数据与访问 | 晋级规则 |
|---|---|---|
| local/preview | 合成或脱敏数据；开发人员 | 不连接生产执行凭据 |
| staging | 生产形态、非生产目标 | 同一不可变构建物通过规格、权限、迁移和回滚演练 |
| production | 最小权限、受控 break-glass | 审批后分阶段发布，保留关联证据 |

## 构建、发布与回滚

- CI 生成带提交、依赖和来源证明的不可变构建物；同一构建物逐环境晋级。
- 数据库变更使用 expand/contract；破坏性变更没有已验证恢复路径时不得发布。
- 发布采用小批量或 feature flag；自动回退信号和人工止损步骤由 `TBD-DEPLOY-003` 确认。
- 控制台自身的回滚不能依赖控制台唯一可用；维护独立、受审计的 break-glass runbook。

## 可观测性

| 用户信号 | 目标/告警 | Owner/runbook |
|---|---|---|
| 告警和证据新鲜度 | TBD-DEPLOY-003；来源失败与陈旧数据分开告警 | SRE |
| 回滚预检/提交/终态 | TBD-DEPLOY-003；未知结果最高优先级路由 | 发布负责人 |
| 授权与审计写入 | 拒绝率异常、审计不可写立即阻断执行 | 安全负责人 |
| AI 辅助质量/延迟/成本 | 仅在启用后由 TBD-AI-001 定义；失败不阻断确定性路径 | AI/产品负责人 |

## 备份与恢复

| 数据 | RPO/RTO | 恢复验证 |
|---|---|---|
| 确认、操作与审计记录 | TBD-DEPLOY-001 | 定期隔离恢复演练和证据抽查 |
| 可重建外部投影 | TBD-DEPLOY-001 | 从权威来源重放并核对新鲜度 |

## 成本与生命周期

主要成本来自应用/数据库、遥测保留、外部 API 和可选模型调用；上限、归属、预算告警与停用规则由 `TBD-DEPLOY-004` 决定。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 定义各数据类别 RTO/RPO、备份保留和恢复演练 | SRE、数据负责人 | 上线评审前 | production-ready | pending |
| TBD-DEPLOY-002 | 确认云、区域、网络、环境拓扑和生产责任 | 平台负责人 | 部署设计前 | production-ready | pending |
| TBD-DEPLOY-003 | 基于基线定义 SLI/SLO、阈值、路由与自动回退信号 | SRE | 生产演练前 | production-ready | pending |
| TBD-DEPLOY-004 | 定义容量范围、成本上限、预算告警和 Owner | 工程负责人 | 生产架构批准前 | production-ready | pending |
