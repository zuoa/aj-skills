---
blueprint_kind: deploy
blueprint_status: draft
owner: ops-owner
last_reviewed: 2026-09-10
---

# 部署与运行

## 运行拓扑

| Environment/unit | Region/service | Network/data boundary | Owner | State |
|---|---|---|---|---|
| Production edge | 中国大陆同一云：DNS/CDN/WAF/LB | 公网 TLS；仅 LB 到 API | ops-owner | provisional；主体/备案和报价后确认 |
| API | 两个可用区的托管容器/PaaS，最少 2 实例 | 私网访问 DB/对象/secret；受控外连供应商 | backend-lead | provisional |
| Worker | 同镜像独立进程，最少 1+ 可替换实例 | 无公网入站；私网 DB/对象 | backend-lead | provisional |
| PostgreSQL | 中国大陆同 region 托管 PostgreSQL 高可用 | 私网、TLS、按时间点恢复 | ops-owner | provisional |
| Object/CDN | 中国大陆私有对象桶；鉴权 CDN/短签名 | 隔离上传/ready/backup 前缀 | security-owner | provisional |
| SMS/push | 经批准的国内供应商 + APNs | 最小 payload、专用密钥 | mobile-lead | pending（TBD-PROVIDER-001） |

Provisional 首选是阿里云中国大陆的 SAE/同类托管容器 + RDS PostgreSQL + OSS/CDN/WAF；若主体接入、成本或能力不合适，可整体映射至等价国内云。避免跨云常态运行；保留标准 Docker 镜像、PostgreSQL 备份和对象 manifest 作为退出路径。

## 环境矩阵

| Environment | Purpose | Data policy | Access | Promotion rule |
|---|---|---|---|---|
| Local | 单模块开发、模拟 provider | 合成数据；本地对象模拟器 | 开发者设备 | 本地测试通过 |
| Preview | 每 PR UI/API 验证，72h 自动销毁 | 合成种子；禁真实手机号/照片 | 团队 SSO/VPN | CI 绿色创建，不向生产提升数据 |
| Staging | 发布候选、迁移、压测、商店沙箱 | 合成/明确同意的测试账号；生产结构非生产内容 | 团队受控账号 | 同一制品经门禁提升 |
| Production | 中国大陆正式服务 | 真实数据；最小权限/审计 | release/ops 限定 | 两人审批、变更单、回滚条件 |

## 构建、配置与密钥

- 后端每个 commit 构建一次 OCI 镜像，包含 commit SHA、SBOM、签名和扫描报告；同 digest 从 staging 提升生产，不重新构建。
- Flutter iOS/Android 产物按 release commit 构建、签名、保存 symbols/mapping；Web 产物内容哈希并以不可变静态文件发布。
- 配置 schema 在启动时验证：环境、region、public base URL、DB pool、object bucket/prefix、provider endpoint、timeout、feature flag、minimum client version；敏感值只引用 secret key 名。
- 生产 secret 使用国内云 KMS/secret manager；开发/预发/生产账户和 key 隔离；读取使用 workload identity，不能注入仓库或长期 CI 变量。季度访问审查，provider key 至少 90 天轮换（provisional）。
- Runtime 只使用仍受上游安全支持的 stable/LTS；每季度升级窗口，EOL 前 90 天完成迁移。确切版本在仓库初始化 ADR/lockfile 固定，避免本文记录易过期版本。

## CI/CD 与发布

| Stage | Automated checks | Approval | Artifact/evidence | Failure action |
|---|---|---|---|---|
| PR | format/lint/typecheck、unit、contract、secret/SCA/SAST、Flutter analyze/test | 1 reviewer；安全路径 code owner | 测试报告、覆盖率差异、扫描 | 阻止合并 |
| Main | integration、DB migration lint、build/sign/SBOM、容器/IaC scan | 自动 | 不可变 artifacts/provenance | 不发布候选 |
| Staging | E2E 三角色、设备 smoke、迁移 dry-run、100 RPS 30m 压测 | QA + product | 截图、指标、迁移与回滚记录 | 修复后新候选 |
| Production web/API | 5%→25%→100% canary/rolling，synthetic + SLI | release-owner + ops | change record、dashboard snapshot | 自动停升；达到阈值回滚 |
| Mobile | internal→1%→10%→50%→100% 分阶段 | product + mobile lead | 商店构建号、crash/ANR、API SLI | 暂停/下架版本；服务端 flag 降级 |

- 数据库采用 expand/contract：先加兼容 schema→双读/写或 backfill（可重启、限速）→客户端窗口后移除；同一发布不得做不可逆 drop。迁移有超时/锁预算，失败停止流量提升。
- 后端保持最近 2 个已发布移动版本兼容；紧急时用服务端 feature flag 禁用照片/提醒等非核心功能。最低版本提升需产品、安全审批和商店可用性验证。
- Web/API 回滚到上一镜像/静态 manifest；schema 仅前向修复。移动二进制无法即时回滚，使用阶段发布、远程 kill switch 和兼容 API。

## 可观测性与事故

| User signal/SLI | Target | Alert condition | Owner/runbook |
|---|---|---|---|
| OTP 请求被接受率（排除合法限流） | ≥99% provisional | 5m <95% 或 provider 错误 >5% | on-call / SMS failover runbook |
| 核心 API good events | 月 99.9% provisional；p95 <500ms | 10m error >2% 或 p95 >1s；burn-rate 组合告警 | backend on-call |
| 打卡确认 | 99.5%/5m provisional | 10m <98% 或幂等冲突异常 | backend on-call |
| 照片处理 | 95% <60s provisional | ready p95 >180s、reject/queue >5% | media owner |
| 提醒提交渠道 | 授权有效 token ≥95% provisional | 15m <90% 或队列延迟 >5m | mobile/backend on-call |
| 教练列表 | p95 <800ms provisional | 10m >1.5s 或 authz 5xx | backend on-call |

- JSON 结构日志（30 天）、指标（13 个月降采样）、分布式 trace 采样 7 天、管理审计 180 天 provisional；以 correlation ID 串联，严格脱敏。
- Synthetic 每分钟覆盖体验页、API health 和合成账号“登录沙箱→计划→打卡”；真实短信不做高频 synthetic。
- SEV-1/2 响应见 SECURITY.md；事故频道、值班表和外部状态页/客服模板在发布前演练。所有告警必须有 owner、阈值、runbook 和最近验证时间。

## 备份与恢复

| System/data | Backup/replication | RPO | RTO | Restore test and owner |
|---|---|---|---|---|
| PostgreSQL | 多可用区高可用、连续日志/PITR、每日快照 35 天、月度加密导出 3 月 | 15m | 4h | 每月抽表、季度完整隔离恢复；ops-owner |
| Object photos | 服务端加密、版本/删除保护 24h、每日 inventory；备份桶 35 天（若合规批准） | 24h | 8h | 季度按 manifest 恢复并验证授权；security-owner |
| Config/IaC | Git + 签名 release；secret metadata 清单不含值 | 1 release | 4h | 每季度从空环境重建 staging；ops-owner |
| Audit | 独立受限存储日归档 | 24h | 24h | 半年检索演练；security-owner |

托管 RDS 的实际系列必须支持日志备份/PITR；阿里云官方资料说明不同实例能力不同，选择前按[备份恢复概览](https://help.aliyun.com/zh/rds/support/backup-and-restoration-4/)和[PostgreSQL 按时间点恢复说明](https://help.aliyun.com/zh/rds/apsaradb-rds-for-postgresql/restore-data-of-an-apsaradb-rds-for-postgresql-instance)核实（访问 2026-09-10）。“已配置备份”不等于通过闸门，首次完整恢复演练及计时证据才可关闭 TBD-OPERATIONS-001。

## 成本与生命周期

以下是 20k DAU 的月度规划 envelope，不是报价；全部 provisional，M1 用同主体/区域正式报价替换，M4 用实测单位成本校准。

| Cost driver | Expected range | Budget/alert | Owner | Decommission rule |
|---|---|---|---|---|
| API/worker/edge/WAF | ¥1,400–1,900 | ¥1,900；CPU/内存按 SLO 扩缩 | ops-owner | 环境/旧 revision 7 天自动回收 |
| PostgreSQL/backup | ¥1,500–2,000 | ¥2,000；连接/IO/存储 60% review | backend-lead | 先导出恢复验证再销毁 |
| 对象存储/CDN/处理 | ¥800–1,500 | ¥1,500；人均图片 GB/流量周报 | media owner | 生命周期 + orphan object 每日清理 |
| SMS | ¥700–1,300 | ¥1,300；单日 >月均 2x / 攻击告警 | product-owner | 号码/模板/供应商停用清理 |
| 监控、安全、DNS/其他 | ¥500–900 | ¥900 | security-owner | 数据保留到期与资产台账 |
| 预留 | ¥400–1,400 | 总账 80%=¥6,400 预警；100%=¥8,000 阻止非必要扩容 | tech-lead | 每月回收闲置 |

若连续 7 日月度预测 >¥6,400：先压缩/缩略图与 CDN、清理预览/日志、调度规格；不能以降低备份、授权、加密或告警换成本。若仍超 ¥8,000，由 product-owner 在降低图片限额、购买承诺用量或申请预算之间作显式决定。

## 域名、备案与外部渠道

- 主体必须持有域名、ICP备案/可能许可、APP 备案、云账户和商店账号；中国大陆非经营性互联网服务备案要求以[工信部现行办法](https://www.miit.gov.cn/zcfg/xxtxl/art/2024/art_7e48434c08c24131b4b7eecfca5b2b6c.html)核实（访问 2026-09-10）。公安联网备案/等保定级适用性由专业人员确认，不在本文下法律结论。
- DNS 用企业账号、MFA、双人审批；TLS 自动续期，30/14/7 天到期告警；域名/证书资产季度核对。
- iOS bundle ID、Android applicationId、Universal/App Links 域名在 M1 冻结；签名证书/密钥由公司账号托管，CI 使用受保护短期访问，禁止个人唯一持有。
- 商店：iOS TestFlight→分阶段发布；Android 至少覆盖目标主流商店/渠道的内测与灰度。元数据、隐私标签/清单、权限说明、APP 备案号、截图和客服渠道需与实际行为一致。
- iOS 推送使用 token-based APNs，设备 token 注册与更新遵循 [Apple 官方 APNs 文档](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)（访问 2026-09-10）；payload 不含手机号、训练详情或图片 URL。
- Provider 配额、SLA、DPA、出口/删除、支持联系人和替换 adapter 均进供应商台账；每半年做短信或推送沙箱切换演练。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 根据主体、备案接入和报价冻结中国大陆云 region/服务规格及 8,000 元成本基线 | tech-lead | M1 末 | production-ready | pending |
| TBD-STORE-001 | 建立公司 iOS/Android 商店账号、bundle IDs、签名保管、渠道清单与上架排期 | mobile-lead | M1 末 | production-ready | pending |
| TBD-OPERATIONS-001 | 指定具名主/备 on-call，完成告警路由、事故演练和 PostgreSQL/对象完整恢复演练 | product-owner | M5 第 2 周 | production-ready | pending |

