# 技术架构规范

## 1. 架构目标

- 6 个月内由小团队交付，降低多端重复开发和分布式系统复杂度。
- 支撑初期 20,000 DAU、3 倍突发余量，并能按模块拆分而无需重写领域模型。
- 大陆网络环境下不依赖 Google 服务作为唯一关键路径。
- 照片、手机号、训练/身体感受数据默认按敏感或高风险个人信息保护。

## 2. 推荐技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 客户端 | Flutter stable + Dart | 会员 iOS/Android/Web；教练 Web 独立入口但共享 packages |
| 状态/路由 | Riverpod + go_router | 明确依赖、可测试、支持 Web 深链 |
| 本地存储 | secure storage + SQLite/Drift | token 进系统安全区；草稿加密后入本地库 |
| API | TypeScript + NestJS | 模块化单体，REST/JSON，OpenAPI 生成客户端 |
| 数据库 | PostgreSQL 15+ 托管版 | 事务、约束、JSONB 与成熟备份能力 |
| 缓存/队列 | Redis 托管版 + BullMQ | 验证码、限流、短缓存、提醒/媒体任务 |
| 媒体 | 大陆对象存储 + CDN | 私有桶、签名 URL、生命周期规则 |
| 推送 | APNs + Android 厂商聚合/适配层 | 按 token/厂商路由；供应商可替换 |
| 可观测 | OpenTelemetry + 托管日志/指标/追踪 | 统一 request/trace ID，减少多套 agent |
| CI/CD | Git 托管 CI + Fastlane/商店流水线 | lint、测试、构建、签名、灰度、回滚 |

具体云厂商与推送供应商均为 **provisional**：采购前以大陆节点可用性、备案接入、SLA、数据处理协议、成本实测和团队运维经验打分；任何单供应商估价高于预算 20% 或缺少所需合规条款时重评。

## 3. 代码与部署拓扑

```text
Flutter monorepo
├─ apps/member_app       iOS / Android / responsive Web
├─ apps/coach_web        responsive Web
└─ packages/             design_system / api_client / domain / analytics

Internet
  -> CDN/WAF
      -> Static Web assets
      -> API Load Balancer
          -> API instance A/B (NestJS modular monolith)
              -> PostgreSQL (HA)
              -> Redis
              -> Object Storage (private)
              -> SMS provider adapter
              -> Push provider adapter
          -> Worker instance(s)
              -> reminder / image scan / thumbnail / export / cleanup jobs
```

生产、预发布、开发使用独立账号/项目或至少独立 VPC 与凭据；生产数据不得复制到非生产环境。

## 4. 后端模块边界

| 模块 | 责任 | 禁止 |
|---|---|---|
| Identity | OTP、token、设备会话、账号状态 | 不存训练业务规则 |
| Profile | 昵称、时区、隐私设置、教练关系 | 不直接发送通知 |
| Plan | 模板、版本、动作、分配、日程实例 | 不写打卡事实 |
| Check-in | 打卡、感受、备注、完成状态 | 不直接处理图片二进制 |
| Media | 上传会话、元数据、扫描、缩略图、签名读取 | 不授予超出资源所有者的访问 |
| Reminder | 规则、调度、发送、供应商回执、退订 | 不把队列当事实源 |
| Coach | 教练查询模型与批量工作流 | 不绕过 Profile 授权关系 |
| Privacy | 同意记录、导出、注销、删除任务 | 不静默改变保留期 |
| Audit | 管理/教练敏感操作不可变事件 | 不记录验证码/token/照片内容 |

模块仅通过显式 service 接口访问；禁止跨模块直接写表。MVP 同进程部署，独立 schema/目录与队列，为未来拆分保留边界。

## 5. 关键流程

### 5.1 照片直传

1. 客户端请求 `POST /media/upload-sessions`，声明 MIME、字节数、哈希和用途。
2. API 校验用户/打卡权限，返回 10 分钟有效、限定 key/MIME/大小的签名上传参数。
3. 客户端直传私有桶，不经过 API 进程；支持分片但单图无需并发超过 2。
4. 客户端调用完成接口；worker 读取隔离区对象，验证魔数、解码、清除元数据、病毒/违规内容检查、生成缩略图。
5. 状态从 `uploaded` 变为 `ready` 或 `rejected`；只有 `ready` 对象可生成 5 分钟读取 URL。

失败补偿：24 小时未完成的上传会话及孤儿对象自动清理；照片处理最多重试 3 次，之后进入死信队列并告警。

### 5.2 提醒调度

- 数据库保存用户规则与下一次执行时间；每分钟扫描未来 5 分钟窗口，基于 `(rule_id, occurrence_at)` 建唯一任务。
- worker 发送前再检查授权、静默期、账户状态、当天完成状态。
- 供应商响应写发送尝试；指数退避最多 3 次，超过提醒有效时间即丢弃，不补发过期提醒。
- 禁止用 Redis 延迟队列作为唯一日程事实源；Redis 丢失后可从数据库重建。

### 5.3 打卡一致性

- 唯一约束：`(member_id, plan_day_id, local_date)`。
- 创建/更新要求 `Idempotency-Key`；服务端保留响应 24 小时。
- 更新使用 `version` 乐观锁；冲突返回 409 与最新资源，客户端让用户选择合并/覆盖。
- 打卡事务提交后写 outbox 事件，由 worker 更新教练看板与提醒取消状态，避免双写丢失。

## 6. 鉴权与会话

- access token：JWT 或不透明 token，15 分钟有效；refresh token 30 天有效、每次刷新轮换并检测复用。
- Web refresh token 放 `HttpOnly; Secure; SameSite=Lax` cookie；移动端放 Keychain/Keystore。
- token 仅含稳定主体 ID、角色和会话 ID，不含手机号或健康数据。
- 服务端 RBAC + 资源级 ABAC：角色允许动作后，还必须校验教练关系/资源所有权。
- 密码学密钥由云 KMS 管理；至少每 180 天轮换，泄露时立即轮换并撤销会话。

## 7. 性能预算

| 场景 | 服务端 P95 | 端到端目标 | 限制 |
|---|---:|---:|---|
| OTP 校验 | 300 ms（不含短信送达） | 1 s | 5 次失败即失效 |
| 今日计划 | 300 ms | 2 s 首屏 | 响应 ≤ 200 KB |
| 创建打卡 | 500 ms（不含图片上传） | 2 s | 幂等 |
| 教练学员列表 | 700 ms | 2.5 s | cursor 分页 20/50 |
| 获取图片签名 URL | 250 ms | 1 s | URL 5 分钟有效 |

客户端首包：移动端安装包和 Web 初始 JS 以构建基线测量，S6 后每次发布不得增长超过 10%，否则需性能评审。Web 路由懒加载；缩略图优先，列表不加载原图。

## 8. 可扩展性边界

- API/worker 无状态，CPU 60% 持续 10 分钟触发扩容；数据库连接使用池并设硬上限。
- 高频教练聚合使用异步读模型，不在列表页实时扫描全量打卡。
- 超过 100,000 DAU、写入峰值 > 300 RPS、单表 > 100M 行或教练查询 P95 > 1 秒持续一周时，评估按月分区、读副本或拆分 worker；触发前不引入微服务。
- 媒体 CDN 使用短期签名且防盗链；敏感原图默认不缓存公共边缘节点。

## 9. 客户端工程规范

- feature-first 目录；UI 不直接调用 HTTP；domain 不依赖 Flutter。
- API client 从锁定版本的 OpenAPI 生成，生成代码不可手改。
- 所有异步页面具备 loading/empty/error/retry 四态。
- 断网打卡先保存在加密草稿队列，显示“待同步”；照片与文本独立重试。
- 日志默认脱敏，release 禁止打印请求体、token、手机号和本地数据库内容。
- Remote Config/feature flag 仅用于开关和渐进发布，不承载权限或核心业务真相。

