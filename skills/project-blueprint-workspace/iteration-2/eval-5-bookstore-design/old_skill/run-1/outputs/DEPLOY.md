---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-001
last_reviewed: 2026-09-10
---

# 部署与运行

## 运行拓扑与环境

暂定使用托管 Web 运行时和托管关系数据库，以降低独立店铺团队的运维负担；供应商、区域和价格需在市场、预算与团队信息明确后比较，不在此虚构。

| Environment | Purpose | Data policy | Access | Promotion |
|---|---|---|---|---|
| local | 开发 | 合成数据 | 开发者 | 不提升本地数据 |
| preview/test | 自动/人工验收 | 合成或去标识样本 | 团队 | 通过质量门禁 |
| production | 真实业务 | 按数据政策 | 最小授权 | 同一不可变构建物 |

## 构建、配置与发布

- CI 生成可追溯构建物并执行测试、类型/静态检查、依赖与秘密扫描；具体命令待仓库确定。
- 配置通过环境注入并校验模式，秘密由托管 secret store 提供，不提交仓库。
- 数据库迁移使用向后兼容的 expand/contract；破坏性迁移必须有备份、验证和人工批准。
- 首版采用单区域滚动发布的建议仅为 `provisional`；健康检查失败停止或回滚，恢复步骤需演练。

## 观测与恢复

用户信号包括搜索是否成功、预订是否明确结束、管理写入是否持久化和认证是否可用。目标、告警阈值和轮值责任待业务影响确认，不填固定百分比。结构化日志使用关联 ID 并排除敏感联系信息。

数据库需要加密备份和定期恢复测试；频率、保留期、RPO、RTO 与恢复负责人均由 `TBD-DEPLOY-001` 决定。未完成恢复演练不得声称 production-ready。

## 成本与外部通道

主要成本驱动是应用运行时、数据库、存储、出站流量和未来通知。建立预算和告警前不估算金额。DNS、TLS 自动续期、域名所有权、状态沟通渠道及供应商退出/导出路径待确认。无原生移动商店发布。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认供应商/区域、预算、环境责任、SLO、告警、回滚、备份与 RTO/RPO | operations-owner | 生产环境建立前 | production-ready | pending |
