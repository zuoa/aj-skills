---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-001
last_reviewed: 2026-09-10
---

# 部署与运行

暂定使用托管 Web 运行时和托管关系数据库，避免在团队与规模未知时承担集群运维。供应商、区域、版本与价格均未选择。

| Environment | Purpose | Data policy | Promotion |
|---|---|---|---|
| local | 开发 | 合成数据 | 不提升本地数据 |
| preview/test | 自动与人工验收 | 合成/去标识数据 | 通过质量门禁 |
| production | 真实预约 | 按待确认的数据政策 | 提升同一不可变构建物 |

CI 应执行测试、类型/静态检查、构建、依赖与秘密扫描。配置按环境校验，秘密由托管 secret store 提供。数据库迁移采用向后兼容的 expand/contract，破坏性步骤需备份、验证和人工批准。

观测聚焦学员能否读取时段/得到明确预约结果、教练写入是否成功、认证是否可用；目标和告警阈值 pending。日志用关联 ID 且不含完整联系方式。

生产前必须指定备份范围、加密、保留、恢复演练、RPO/RTO、告警、发布、回滚和事故沟通责任；当前不填虚构数值。成本驱动为运行时、数据库、存储、流量和未来通知，预算与告警待定。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认区域/供应商、预算、运行责任、SLO、发布回滚、备份和 RTO/RPO | operations-owner | 生产环境前 | production-ready | pending |
