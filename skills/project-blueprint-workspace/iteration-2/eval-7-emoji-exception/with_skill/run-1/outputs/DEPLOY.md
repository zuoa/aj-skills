---
blueprint_kind: deploy
blueprint_status: draft
owner: operations-lead
last_reviewed: 2026-09-10
---

# 部署与运行

## 运行拓扑与环境

| 环境/单元 | Region/service | Network/data boundary | Owner | State |
|---|---|---|---|---|
| preview | 托管 Web/API；使用合成数据 | 不接生产数据库或密钥 | engineering | provisional |
| staging | 与生产同类托管服务 | 去标识测试数据；受团队访问控制 | QA/operations | provisional |
| production | 区域与供应商待定 | 公网边缘、私有数据服务、受控运维访问 | operations | pending |

本地环境使用合成账号与文件；禁止复制真实青少年数据。构建一次并在 staging 验证后提升同一不可变产物至 production。

## 构建、配置与密钥

- 产物：锁定依赖的前端静态包与 API/worker 容器；CI 记录源码提交、依赖清单、签名和扫描结果。
- 配置：按环境验证 schema；功能开关不得绕过授权、审计或可访问状态文本。
- 密钥：托管 secret provider，最小访问、轮换和 break-glass 审计。
- 运行时：具体版本在仓库创建后锁定并记录支持期限。

## CI/CD 与发布

| Stage | Automated checks | Approval | Evidence | Failure action |
|---|---|---|---|---|
| pull request | unit/integration、类型、lint、依赖/secret 扫描、可访问性静态检查 | code owner | CI report | 阻止合并 |
| staging | 数据迁移、端到端、授权、屏幕阅读器人工检查清单 | QA + security for risk changes | signed release record | 不提升产物 |
| production | smoke、健康检查、迁移兼容检查 | operations owner | deployment record | 停止或回滚应用 |

- 数据库迁移使用 expand/contract；不可逆数据变更必须先备份并演练恢复。
- 首版采用小批量/滚动发布；数据迁移不能靠应用回滚撤销时，必须有前向修复步骤。
- 前端与 API 保持兼容窗口；PWA 缓存版本必须能发现更新并避免旧客户端写入错误 schema。

## 可观测性与事件

| User signal/SLI | Target | Alert condition | Owner/runbook |
|---|---|---|---|
| 报名结果可用 | TBD-DEPLOY-001 | 超过已批准错误预算 | operations/product |
| 完成记录成功写入 | TBD-DEPLOY-001 | 保存错误或任务积压超阈值 | operations/backend |
| 审核操作可用且授权正确 | TBD-DEPLOY-001 | 权限异常或审计缺失 | security/safety |

结构化日志使用 correlation ID，不记录提交正文、照片或认证秘密。事件严重度、值班范围、用户通知渠道和 runbook 在试点前批准。

## 备份与恢复

| System/data | Backup/replication | RPO | RTO | Restore test and owner |
|---|---|---|---|---|
| 关系型数据库 | 加密自动备份与时间点恢复，频率待定 | TBD-DEPLOY-001 | TBD-DEPLOY-001 | operations 在上线前演练并记录 |
| 对象存储 | 版本/生命周期与跨故障域策略待定 | TBD-DEPLOY-001 | TBD-DEPLOY-001 | operations 按抽样文件恢复演练 |
| 配置与基础设施 | 版本化配置/基础设施定义 | 以仓库为准 | 重建目标待定 | engineering/operations 演练新环境 |

## 成本、域名与退出

- 成本驱动：数据库、对象存储/流量、媒体扫描和通知；预算与告警阈值由 TBD-DEPLOY-001 决定。
- 域名、DNS、TLS 自动续期和状态页 owner 待定；证书失效必须在到期前告警。
- 服务供应商需记录数据导出、删除、配额、支持和替代路径；不在缺少地区与预算约束时锁定厂商。
- 原生商店分发当前 not-applicable；若 TBD-PRODUCT-002 改为原生范围，新增签名、隐私声明、分阶段发布和最低版本策略。

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认生产地区、供应商、SLO、RTO/RPO、成本上限和值班 owner | operations and product leads | 试点上线评审前 | production-ready | pending |
