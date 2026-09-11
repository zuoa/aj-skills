---
blueprint_kind: deploy
blueprint_status: draft
owner: platform-owner
last_reviewed: 2026-09-10
---

# 部署与运维

## 运行拓扑与环境

| Environment/unit | Region/service | Data policy | Owner | State |
|---|---|---|---|---|
| Local/preview | 本地或临时托管环境 | 合成数据；短期销毁 | 开发 | provisional |
| Staging | 与生产同类托管服务 | 脱敏/合成数据 | 技术负责人 | provisional |
| Production | 目标地区托管 PaaS、PostgreSQL、realtime、worker、secret/observability | 仅生产数据 | 技术负责人 | pending: TBD-REGION-001 |

构建一次并推广不可变容器；公网仅开放 Web/API/realtime 边缘入口，数据库和 worker 为私网访问。

## 构建、配置与发布

- 配置经 schema 校验；密钥由托管 secret manager 注入并审计访问。
- CI 顺序：依赖/secret 扫描 → lint/typecheck/unit → integration/tenant isolation → build/SBOM → staging smoke/load → 人工生产批准。
- 数据库使用 expand/contract 迁移；应用先兼容新旧 schema；破坏性迁移需备份、回填验证和单独批准。
- 滚动或 canary 发布；聊天、AI、知识摄取可独立 feature flag；AI 回滚不影响人工聊天。

## 可观测性与事件

| User signal/SLI | Target | Alert | Owner/runbook |
|---|---|---|---|
| AI 请求到可见首 token | P95 ≤ 2s | 连续 10 分钟超标 | AI 负责人；切人工模式/检查检索与供应商 |
| 实时连接恢复 | 3000 峰值可用，4500 压测 | 连接失败/重连率持续超基线 | 平台负责人；配额/区域/回放检查 |
| 人工消息成功率 | 生产 SLO 待确认 | 错误预算阈值待确认 | 技术负责人 |
| 月度总成本 | ≤ ¥50,000 | 60%/80%/100% 阈值 | 产品/技术负责人 |

日志、指标和 traces 使用 correlation ID；正文默认脱敏。模型供应商故障触发熔断和人工模式，不自动切换未经安全审批的供应商。

## 备份与恢复

| System/data | Backup/replication | RPO | RTO | Restore test and owner |
|---|---|---|---|---|
| PostgreSQL | 托管 PITR + 加密备份 | 待确认 | 待确认 | 上线前恢复演练；平台负责人 |
| 知识原件 | 版本化对象存储（如启用） | 待确认 | 待确认 | 季度抽样恢复；平台负责人 |
| 配置/infra | 版本控制 + IaC | 以合并记录为准 | 待确认 | staging 重建演练；平台负责人 |

## 成本与生命周期

| Cost driver | Planning cap | Alert/action | Owner | Decommission rule |
|---|---|---|---|---|
| LLM/embedding token | ¥25,000/月 | 60/80% 告警；100% 暂停新草稿 | AI/产品 | 可切换 adapter/模型 |
| App/DB/realtime/worker | ¥15,000/月 | 80% 查扩容、空闲资源 | 平台 | 预览环境自动销毁 |
| Observability/backup/egress | ¥5,000/月 | 80% 查保留与采样 | 平台/安全 | 按策略归档删除 |
| Reserve | ¥5,000/月 | 未经负责人批准不动用 | 产品 | 月末归零 |

这是预算分配护栏，不是供应商报价；用试点真实 token、连接和存储数据校准。人工聊天资源不得因 AI 超支被限流。

## 外部渠道与退出

- DNS/TLS 自动续期并由平台负责人持有；MVP 无移动商店/小程序发布。
- 上线前核对 realtime/LLM 配额、地域、支持等级和数据条款；保留数据导出、模型 adapter 替换和托管服务迁移手册。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认生产 SLO、人工消息告警阈值、RTO/RPO、值班与恢复演练结果 | 技术负责人/产品负责人 | 生产上线评审前 | production-ready | pending |
