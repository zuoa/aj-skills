---
blueprint_kind: architecture
blueprint_status: draft
owner: engineering-lead
last_reviewed: 2026-09-10
---

# 系统架构

## 约束与质量预算

| 属性 | 目标/范围 | Evidence | State | Revisit trigger |
|---|---|---|---|---|
| 无障碍 | 状态语义由服务端响应与客户端文字一致表达 | PRD-ACCESS-001 | confirmed | 核心客户端变化 |
| 隐私 | 默认不公开未成年人的联系方式、精确住址或完整轨迹 | PRD-SAFETY-001 | provisional | 地区与年龄规则确认 |
| 一致性 | 报名和完成记录写入幂等；核验状态有审计历史 | SPEC-ACTION-001..003 | confirmed | 离线写入进入范围 |
| 性能/可用性 | 数值预算待试点规模和运维能力确认 | TBD-ARCH-001 | pending | 实现前确认 |

## 系统上下文

```text
青少年参与者 ── HTTPS ──> 社区环保行动应用 <── HTTPS ── 组织者/审核员
                              │
                              ├── 身份与通知提供方
                              └── 对象存储（可选照片）
```

浏览器与服务端之间、服务端与外部提供方之间是信任边界。外部通知只携带最低必要信息，不在消息正文暴露敏感位置或审核材料。

## 容器与部署单元

| 单元 | 责任 | 接口 | 数据所有权 | Owner | State |
|---|---|---|---|---|---|
| 响应式 Web/PWA | 呈现、表单状态、无障碍语义、可恢复草稿 | HTTPS JSON API | 仅本地未提交草稿 | frontend team | provisional |
| 模块化单体 API | 身份、行动、报名、完成记录、审核和举报规则 | versioned HTTPS API | 业务规则与事务 | backend team | provisional |
| 关系型数据库 | 账号引用、行动、报名、完成记录、审核状态、审计元数据 | 仅服务端访问 | 结构化业务数据 | backend/operations | provisional |
| 对象存储 | 用户许可上传的证据文件 | signed upload/download | 文件对象 | operations | provisional |
| Worker | 通知、媒体扫描和异步清理 | 数据库任务表或托管任务 | 无独立业务真相 | backend team | provisional |

## 模块边界

| 模块 | 责任 | Allowed dependencies | Related SPEC |
|---|---|---|---|
| Identity | 账号、角色、组织者授权 | 不读取证据内容 | SPEC-SAFETY-001 |
| Actions | 行动详情、资格、报名 | Identity | SPEC-ACTION-001 |
| Records | 草稿提交、幂等保存、核验状态 | Identity, Actions, Media | SPEC-ACTION-002; SPEC-ACTION-003 |
| Safety | 举报、审核权限、审计和升级 | Identity, Actions, Records | SPEC-SAFETY-001 |
| Notifications | 用户可理解的状态通知 | 只消费已提交的领域事件 | SPEC-ACTION-003; SPEC-ACCESS-001 |

## 数据与一致性

| 数据/实体 | Source of truth | Classification | 一致性/事务 | Retention |
|---|---|---|---|---|
| 行动与报名 | 关系型数据库 | internal/personal | 名额检查与报名原子提交；幂等键防重复 | 活动周期后按政策归档/删除，pending |
| 完成记录 | 关系型数据库 | personal | 创建与状态转换有版本号及审计记录 | TBD-SECURITY-001 |
| 证据照片 | 对象存储，数据库保存引用 | personal, potentially sensitive | 上传完成后才可关联记录；扫描失败不可公开 | TBD-SECURITY-001 |
| 举报与审核 | 关系型数据库 | confidential | 追加式审计；权限与内容分离 | TBD-SECURITY-001 |
| 本地草稿 | 用户设备 | personal | 未提交，不视为服务端成功 | 用户提交/删除或到期，pending |

## 接口与集成

| 接口 | Contract/versioning | Auth | Timeout/retry/idempotency | Degradation |
|---|---|---|---|---|
| Web API | `/api/v1`，错误含稳定 code 与可显示文案键 | 安全会话，具体方式 pending | 写入携带 idempotency key；只重试安全请求 | 显示文字错误并保留草稿 |
| 文件上传 | 短时签名 URL、限制类型与大小 | 记录所有者授权 | 分片/重试策略在证据约束确认后决定 | 允许稍后添加或说明为何必需 |
| 通知提供方 | 版本化适配器 | 服务身份 | 有限重试与去重 | 站内状态仍为权威，不把通知送达当成功 |

## 技术与中间件决定

| 决定 | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|
| 应用形态 | 一个团队、早期 MVP、需一致授权与审计 | 模块化单体；微服务 | 模块化单体 | 独立扩展较少，但边界和事务更简单 | provisional | 独立团队/发布/扩展边界形成 |
| 主存储 | 事务、关联查询、状态审计 | PostgreSQL；文档库 | 托管 PostgreSQL | 需要 schema migration | provisional | 访问模式证明不适配 |
| 异步工作 | 通知与媒体扫描；未知规模 | 数据库任务/托管任务；独立 broker | 从托管任务或数据库 worker 开始 | 峰值隔离有限 | provisional | 持续积压、扇出或独立可用性目标出现 |
| 缓存/搜索 | 无已知证据要求 | 数据库索引；外部系统 | 首版不引入 | 极大规模或复杂相关性搜索前需复核 | confirmed | 实测预算不达标 |

## 失败与演进

- 预期降级：通知提供方失败不改变站内状态；媒体处理失败隔离文件并允许重新上传；离线时不宣称提交成功。
- 容量边界：在 TBD-ARCH-001 确认前不承诺吞吐或延迟数字。
- 拆分触发：独立团队需要独立发布、数据隔离成为监管要求，或实测负载无法通过单体水平扩展满足预算。

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 确认试点流量、用户可见延迟、可用性与成本预算 | engineering and product leads | 架构基线批准前 | implementation-ready | pending |
| TBD-ARCH-002 | 确认账号认证与青少年组织归属模型 | security and product leads | 身份实现前 | implementation-ready | pending |
