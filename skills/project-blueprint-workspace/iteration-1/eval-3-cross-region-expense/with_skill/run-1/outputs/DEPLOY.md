---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-001
last_reviewed: 2026-09-10
---

# 部署与运行

## 运行拓扑

| Environment/unit | Region/service | Network/data boundary | Owner | State |
|---|---|---|---|---|
| Global routing control plane | 待选全球/多区托管服务 | 仅租户伪名、home region 与健康元数据 | 平台负责人 | provisional |
| EU production data cell | EU 内两个或更多故障域 | EU 业务数据、文件、审计、备份不出 EU | EU SRE | confirmed 约束；服务待定 |
| US production data cell | 美国批准区域 | US 租户数据面 | US SRE | provisional |
| CN production data cell | 中国大陆批准区域/实体 | CN 租户数据面；跨境默认禁止 | CN SRE/法务 | provisional |
| Regional payment/IdP integrations | 各 home region | 仅最小必要字段；供应商边界 | 集成 owner | pending |

## 环境矩阵

| Environment | Purpose | Data policy | Access | Promotion rule |
|---|---|---|---|---|
| Local | 单模块开发 | 仅合成数据、假供应商 | 开发者设备 | 不提升本地制品 |
| Preview | PR UI/API 验证 | 合成数据；短期隔离环境 | 团队+评审者 | PR 关闭自动销毁 |
| Test/Staging per region | 集成、迁移、恢复预演 | 合成或批准脱敏数据；不得复制生产原件 | JIT 团队访问 | 同一签名制品通过门禁后提升 |
| Production per region | 客户业务 | 仅本区域租户生产数据 | 最小权限、JIT、受审计 | 变更审批+渐进发布 |

## 构建、配置与密钥

- Build artifact and provenance: 一次构建的 Web/API/worker/移动候选制品生成 SBOM、签名与来源证明；区域提升使用相同版本、区域配置分离。
- Configuration schema: 配置经 schema 校验；区域、端点、功能开关与保留策略显式；禁止默认回退到其他区域。
- Secret provider, access and rotation: 每区域 secret manager 与密钥；workload identity；break-glass 访问限时、双人审批并告警。
- Runtime/version support policy: 语言、框架、数据库和移动最低 OS 待技术/产品 owner 确认，不在草案编造版本。

## CI/CD 与发布

| Stage | Automated checks | Approval | Artifact/evidence | Failure action |
|---|---|---|---|---|
| PR | unit、contract、lint/type、SAST、SCA、secret、tenant isolation | 代码 owner；高风险安全 review | 测试报告、SBOM 草案 | 阻断合并 |
| Build | 可复现构建、签名、镜像扫描 | 平台 owner | 不可变制品、provenance、SBOM | 禁止提升 |
| Staging | 区域路由、迁移、SSO/支付沙箱、文件扫描、恢复 smoke | 产品+SRE；高风险安全 | 区域测试和迁移证据 | 回滚候选/修复 |
| Production | canary/rolling、synthetic、错误率与延迟门禁 | 变更 owner+区域 SRE | 部署审计、制品 digest | 自动暂停/回滚 |

- Database migration/rollback: expand/contract；旧/新应用双兼容；先 schema、后回填、再切读、最后删除。不可逆迁移须备份验证、恢复步骤和人工批准，应用回滚不假定数据自动回滚。
- Release strategy: 区域分批 canary/rolling；EU 单独验证；控制面变更必须验证不会错误跨区路由。
- Feature flags and compatibility: 标志需 owner、过期日和区域默认值；API 至少维持经确认的移动兼容窗口，待 TBD-DEPLOY-002。
- Mobile: iOS/Android 分阶段发布；签名账号、商店主体、隐私声明、最低版本与紧急禁用策略待确认。

## 可观测性与事件

| User signal/SLI | Target | Alert condition | Owner/runbook |
|---|---|---|---|
| 登录成功率/时延 | TBD-SLO-001 | 相对基线或租户 IdP 失败预算，待确认 | 身份 on-call |
| 费用提交成功率/时延 | TBD-SLO-001 | 连续失败或上传/扫描积压，待确认 | 应用 on-call |
| 审批决定成功率 | TBD-SLO-001 | 状态冲突或错误率超预算 | 应用 on-call |
| 支付待确认时长/对账差异 | 供应商 SLA 与业务阈值待定 | 老化付款或差异出现即按级别路由 | 支付 on-call |
| 区域路由违规拒绝 | 0 预期正常事件 | 任一出现立即安全告警 | 安全/SRE |
| 审计管道新鲜度 | 阈值待 TBD-SECURITY-002 | 丢失/积压超过阈值 | 安全 on-call |

- Logs/metrics/traces/audit retention: 每区域保存；correlation ID 不含 PII；应用日志默认脱敏；保留期由法务/安全确定。
- Incident severity and escalation: TBD-SECURITY-001 定义安全/隐私，TBD-DEPLOY-001 定义运行事件；供应商与客户沟通路径需演练。
- Status/user communication: 公共状态页按区域/能力报告，不暴露租户或安全细节；法律通知由法务判断。

## 备份与恢复

| System/data | Backup/replication | RPO | RTO | Restore test and owner |
|---|---|---|---|---|
| 区域关系库 | 同区域多故障域复制+连续日志/PITR；加密备份 | ≤15 分钟 | ≤2 小时 | 每季度暂定完整恢复；区域 SRE；上线前必须首演 |
| 区域对象存储 | 版本化/防误删+同区域冗余；EU 仅 EU | ≤15 分钟（需供应商能力验证） | ≤2 小时 | 季度抽样+年度暂定全流程；平台 owner |
| 区域审计存储 | append-only/WORM 能力待定+同区域备份 | ≤15 分钟 | ≤2 小时 | 完整性与恢复联合演练；安全 owner |
| 路由控制面 | 多副本+配置历史；不含敏感载荷 | ≤15 分钟 | ≤2 小时 | 恢复到已知版本且验证不误路由；平台 owner |
| 支付外部状态 | 平台状态备份+供应商对账重建 | ≤15 分钟平台记录 | ≤2 小时恢复对账能力 | 沙箱/受控生产演练；支付 owner |

恢复判定必须包含 API 可服务、租户/区域正确、文件可读、审计连续和支付可对账，而不只是数据库启动。任何 EU 恢复目标位置必须在 EU 内。实际能力与演练频率由 TBD-DEPLOY-001 验收。

## 成本与生命周期

| Cost driver | Expected range | Budget/alert | Owner | Decommission rule |
|---|---|---|---|---|
| 三个区域的基础运行成本 | TBD-COST-001 | 月预算与预测阈值待定 | FinOps/平台 | 无租户区域仅在保留/合同清理后关闭 |
| 发票存储、预览、扫描与出口 | TBD-COST-001 | 按租户/区域/GB 归集 | FinOps/文件 owner | 依批准保留删除源与派生物 |
| DB、备份与审计 | TBD-COST-001 | 容量/IO/备份增长告警 | 数据平台 | 验证保留与法律冻结后清理 |
| 支付/SSO/通知供应商 | TBD-COST-001 | 按交易/MAU/消息归集 | 集成 owner | 导出配置与未完事务后切换 |

## 域名与外部渠道

- DNS/TLS/certificate ownership: 平台团队；区域域名与证书自动续期、到期告警和接管流程待验证。
- Store/mini-program: iOS/Android 账号、签名、审核周期、隐私清单与发布轨道由 TBD-DEPLOY-002 确认；小程序不在 MVP。
- Provider quota/support/exit: 每区域供应商必须记录配额、支持升级、数据导出/删除、替代方案与退出成本；签约受 TBD-LEGAL-001 约束。

## 上线闸门（证据，不是认证结论）

- RPO 15 分钟/RTO 2 小时在每个生产区域完成计时恢复演练且结果符合业务完整性判定。
- EU 备份、日志、支持访问、遥测、支付与故障转移的数据流经法务/安全批准并做区域策略测试。
- SLO、告警、on-call、runbook、状态沟通和供应商升级链有 owner 并演练。
- 迁移/回滚、移动兼容和密钥轮换至少完成一次预演；严重安全问题已关闭或正式接受。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认生产/SRE owner、云区域、on-call、备份技术、恢复演练频率与通过标准 | 平台/SRE 负责人 | 生产基础设施批准前 | production-ready | pending |
| TBD-DEPLOY-002 | 确认 iOS/Android 账号、签名 owner、最低版本、兼容窗口、隐私清单与紧急发布策略 | 移动/发布负责人 | 移动 Beta 前 | production-ready | pending |
| TBD-COST-001 | 确认基线/变量成本预算、容量输入、告警阈值和 FinOps owner | 财务/平台负责人 | 基础设施采购前 | production-ready | pending |

