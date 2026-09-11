---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# 系统架构草案

## 约束与质量预算

| Attribute | Target/range | Evidence | State | Revisit trigger |
|---|---|---|---|---|
| 客户端 | 教练网页管理端、学员手机网页 | 用户输入 | confirmed | 客户端范围变化 |
| 一致性 | 不可重复使用的时段不得产生多个有效预约 | PRD-BOOK-002 / SPEC-BOOK-002 | provisional | 团体容量模型获确认 |
| 工作区隔离 | 所有教练管理数据按工作区授权 | PRD-ACCESS-001 / SPEC-ACCESS-001 | provisional | 租户/组织模型获确认 |
| 性能/可用性/规模 | 未给出，不编造预算 | TBD-QUALITY-001 | pending | 架构基线签署前 |
| 恢复 | 未给出，不编造 RTO/RPO | TBD-RECOVERY-001 | pending | 生产方案签署前 |

## 系统上下文

```text
[教练浏览器] -- HTTPS/管理与查看 --> [课程预约 SaaS]
[学员手机浏览器] -- HTTPS/浏览与预约 --> [课程预约 SaaS]
                                              |
                                              +-- [身份服务：候选/待定]
                                              +-- [通知服务：是否需要待定]
```

- SaaS 边界内负责公开可用性、预约、教练工作区和授权。
- 浏览器到 SaaS、SaaS 到任何外部服务均为信任边界。
- 身份与通知提供方尚未决定，不能据图视为已选型。

## 容器与可部署单元

| Unit | Responsibility | Interfaces | Data owned | Owner | State |
|---|---|---|---|---|---|
| Responsive Web | 提供教练管理端与学员手机预约界面 | HTTPS 页面/API | 不作为业务事实来源；仅会话与暂存 | 技术负责人（未指定） | provisional |
| Application | 身份边界、排班、预约、工作区授权和事务编排 | HTTPS；内部模块调用 | 业务规则，不单独持久化于进程 | 技术负责人（未指定） | provisional |
| Relational Database | 预约、时段、教练/工作区等事务数据的唯一事实来源 | 数据库协议，仅 Application 可访问 | 事务型业务数据 | 技术负责人（未指定） | provisional |
| External Identity | 若采用，完成教练身份认证 | 标准协议待选 | 凭据由提供方拥有；本系统只保存必要引用 | 安全负责人（未指定） | pending，TBD-IDENTITY-001 |
| Notification Provider | 若纳入范围，投递确认/提醒 | API/Webhook 待选 | 投递状态；业务预约仍归本系统 | 产品/技术负责人（未指定） | pending，TBD-NOTIFY-001 |

暂定仅有一个应用发布单元加一个托管关系型数据库；Web 与 Application 可以同一构建物交付。没有证据支持拆分服务。

## 模块边界

| Module | Responsibility | Allowed dependencies | Related SPEC |
|---|---|---|---|
| Identity & Workspace | 当前身份、教练工作区上下文、授权判断 | 身份适配器；工作区存储 | SPEC-ACCESS-001 |
| Scheduling | 可预约时段及发布状态、冲突规则入口 | Workspace；数据库 | SPEC-SCHED-001 |
| Booking | 可用性查询、预约提交、幂等与冲突结果 | Scheduling；Workspace（教练边界）；数据库 | SPEC-BOOK-001, SPEC-BOOK-002 |
| Coach Read Model | 教练预约列表/详情查询 | Workspace；Booking 数据 | SPEC-COACH-001 |
| Notification Adapter | 在确认需要时接收预约领域结果并请求外部投递 | Booking 的已提交结果；外部提供方 | SPEC-BOOK-002（仅当 TBD-NOTIFY-001 纳入） |

Booking 不得依赖通知成功才能保证预约事务成立；否则外部故障会让用户结果含糊。

## 数据与一致性

| Data/entity | Source of truth | Classification | Consistency/transaction | Retention |
|---|---|---|---|---|
| Coach/Workspace | 关系型数据库或身份映射（边界待定） | 内部标识 + 个人信息（provisional） | 工作区授权读取需一致 | TBD-SECURITY-001 |
| Offering/Slot | 关系型数据库 | 业务内部信息 | 发布/撤下在单事务内可观察 | TBD-SECURITY-001 |
| Booking | 关系型数据库 | 预约与联系类个人信息（provisional） | 创建预约与占用资格同一事务；数据库级唯一/容量约束防竞争 | TBD-SECURITY-001 |
| Delivery record | 若启用通知则由本地记录 + 提供方回执 | 联系信息/运营记录（provisional） | 与预约最终性解耦；可重试但去重 | TBD-SECURITY-001 |

对重复提交使用由客户端意图生成或服务端签发的幂等标识；具体契约待技术基线。时区以存储统一时刻加业务时区语境的方向处理，但最终显示/规则由 TBD-BOOK-001 决定。

## 身份与授权边界

- 教练管理端必须认证，服务端每次访问均从可信会话解析工作区；不得信任客户端提交的工作区标识作为唯一授权依据。
- 学员公开页是否匿名、链接受限或要求验证待 TBD-IDENTITY-001。
- 角色范围目前只需要“教练”和学员侧访问者；管理员、员工或组织角色不得提前实现。

## 接口与集成

| Interface | Contract/versioning | Auth | Timeout/retry/idempotency | Degradation |
|---|---|---|---|---|
| Browser ↔ Application | 同仓库类型化契约或明确 schema；破坏变更随同一发布协调 | 教练会话；学员模式待定 | 预约提交幂等；普通查询可安全重试 | 规范化错误，不将超时声明为成功 |
| Application ↔ Database | 迁移版本与应用兼容策略 | 最小权限服务凭据 | 事务与约束处理并发，不盲目重试非幂等写入 | 数据库不可用时拒绝新预约并提示重试 |
| Identity provider（候选） | 采用提供方稳定标准接口 | 服务凭据/回调校验待选 | 明确超时；回调防重放 | 已有会话策略和登录失败表现待定 |
| Notification provider（候选） | 适配器隔离提供方契约 | 服务凭据 | 有界重试与去重；预约不因投递失败回滚 | 管理端可观察失败（若进入范围） |

## 技术与中间件决策

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|
| 架构形态 | 单一早期产品；团队、规模未知；需事务一致性 | 模块化单体；微服务 | 先用模块化单体 | 发布耦合，但边界清楚且运维成本低 | provisional | 出现真实的独立团队/发布/隔离/扩缩边界 |
| 主存储 | 预约与时段要求事务和并发约束 | 关系型数据库；文档数据库 | 单一关系型数据库 | 需设计迁移，但最贴合事务与查询 | provisional | 访问模式或地域法规证明不适配 |
| 应用框架/语言 | 网页双端；团队能力、部署和预算未知 | 待团队能力明确后比较不超过三项 | 暂不指定 | 避免把偏好伪装为约束 | pending，TBD-ARCH-001 | 团队与部署约束明确 |
| 托管方式 | 运维能力、预算、地域未知 | PaaS；托管容器；serverless | 暂不指定供应商；优先低运维托管方案 | 需评估地域、锁定与成本 | pending，TBD-DEPLOY-001 | 市场、预算和负责人明确 |
| 缓存/队列/搜索/实时/微服务/Kubernetes | 当前无证据需要 | 不引入；对应专用组件 | MVP 不引入 | 极端规模下能力有限，但显著减少复杂度 | provisional | 实测热点、耐久后台任务、搜索相关性、推送延迟或组织边界出现 |

## 失败与演进

- **预期降级**：数据库不可用时只读页面也不得伪造最新可用时段，系统拒绝新预约并明确结果；通知故障（若存在）不改变已经提交的预约事实。
- **容量边界**：未知；必须用 TBD-QUALITY-001 的真实流量和数据范围完成容量验证。
- **拆分/替换触发**：模块存在独立团队与发布节奏、明确隔离/扩缩需求，或测量证明单体无法满足已确认预算时才拆分；组件替换需保持 SPEC 可观察行为。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 指定技术负责人，并根据团队能力确定语言、Web 框架、身份适配和数据库产品 | 发起人/技术负责人（未指定） | 开始实现前 | implementation-ready | pending |
| TBD-QUALITY-001 | 定义流量、数据量、延迟、可用性和可接受降级 | 产品/技术负责人（未指定） | 架构基线签署前 | implementation-ready | pending |

