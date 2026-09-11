---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# 系统架构

## 约束与质量预算

| Attribute | Target/range | Evidence | State | Revisit trigger |
|---|---|---|---|---|
| 安全性 | 未通过服务端授权、前置校验或必需审计写入时不得发起回滚 | SPEC-ROLLBACK-001, SPEC-ROLLBACK-003 | provisional | 威胁评审或策略变化 |
| 一致性 | 回滚提交以服务/环境/当前版本作并发校验；重复请求不产生重复执行 | SPEC-ROLLBACK-001 | provisional | 下游不支持稳定幂等键 |
| 数据新鲜度 | `TBD-SPEC-001` | 无来源基线 | pending | 来源契约与真实延迟样本可用 |
| 性能/可用性 | `TBD-DEPLOY-003` | 无流量和关键旅程基线 | pending | 生产 SLI 评审 |
| 恢复 | `TBD-DEPLOY-001` | 无业务影响分析 | pending | 生产架构批准前 |
| 规模/成本 | `TBD-PRODUCT-004`, `TBD-DEPLOY-004` | 无用户量、事件量、成本上限 | pending | 实现排期前 |

## 系统上下文

```text
[值班人员/批准者]
        | 浏览器会话、组织身份
        v
+----------------------- AI 运维控制台 -----------------------+
| 聚合告警与影响证据；记录确认；受控委派回滚；提供审计查询      |
+--------------------------------------------------------------+
    | read                 | read                 | command/query
    v                      v                      v
[监控/告警源]        [服务目录/发布记录]        [部署/回滚系统]
                                                     |
                                                     v
                                               [目标运行环境]

        控制台信任边界：外部来源数据不可信；回滚命令为特权出口。
```

身份提供方、通知/事件系统及模型提供方是否存在均未确认，见 `TBD-ARCH-002`、`TBD-AI-001`。控制台不是告警或部署事实的最终来源，但拥有影响确认记录、回滚请求编排记录和自身审计事件。

## 容器与可部署单元

| Unit | Responsibility | Interfaces | Data owned | Owner | State |
|---|---|---|---|---|---|
| Web client | 告警队列、证据轨道、确认与执行状态界面 | HTTPS JSON API | 仅短期界面状态 | 前端负责人待指派 | provisional |
| Application API | 身份/授权、聚合、确认、回滚预检、审计查询 | HTTPS；来源/部署适配器 | 影响确认、策略引用、执行元数据、审计 | TBD-ARCH-001 | provisional |
| Job worker | 可靠执行与轮询下游回滚，处理超时/重试/终态 | 数据库作业领取；下游 API | 作业租约与执行步骤 | TBD-ARCH-001 | provisional |
| Relational database | 事务记录、幂等、审计、适配器游标 | SQL，仅服务端访问 | 控制台系统记录 | 数据负责人待指派 | provisional |
| External adapters | 统一不同告警、目录和部署契约 | 供应商 API/webhook | 不拥有外部事实 | 集成负责人待指派 | provisional |

Web client、API 与 worker 暂定从同一模块化单体代码库构建；API 与 worker 可独立进程部署但同一发布版本。实际进程数由负载和平台决定。

## 模块边界

| Module | Responsibility | Allowed dependencies | Related SPEC |
|---|---|---|---|
| IdentityPolicy | 认证上下文、服务/环境权限和审批策略 | 身份适配器、策略配置、Audit | SPEC-ROLLBACK-003 |
| Alerts | 标准化告警、筛选和新鲜度 | 告警适配器、ServiceCatalog | SPEC-ALERT-001, SPEC-ALERT-002 |
| ServiceCatalog | 解析服务、环境、依赖和负责人标识 | 目录/发布适配器 | SPEC-IMPACT-001 |
| Impact | 构建带来源关系图、记录确认和证据版本 | Alerts、ServiceCatalog、Audit | SPEC-IMPACT-001, SPEC-IMPACT-002 |
| Rollback | 生成候选、预检、幂等创建执行和推进状态机 | Impact、IdentityPolicy、部署适配器、Audit | SPEC-ROLLBACK-001, SPEC-ROLLBACK-002 |
| Audit | 追加审计事件和授权查询 | 数据库、身份上下文 | SPEC-ROLLBACK-003 |
| Advisory | 可选的只读建议边界，不拥有事实或执行权 | 仅脱敏证据投影；模型适配器若启用 | `TBD-AI-001` |

禁止 UI 直接调用回滚系统；禁止 Advisory 依赖 Rollback 命令接口；外部适配器不得把供应商字段渗透成领域权限决定。

## 数据与一致性

| Data/entity | Source of truth | Classification | Consistency/transaction | Retention |
|---|---|---|---|---|
| 原始告警/遥测摘要 | 对应监控来源 | provisional internal；待 `TBD-SECURITY-003` | 带来源版本和抓取时间的只读投影 | `TBD-SECURITY-003` |
| 服务、环境、版本关系 | 服务目录/部署来源 | provisional confidential | 不同来源并列；不得静默覆盖冲突 | `TBD-SECURITY-003` |
| 影响确认 | 控制台数据库 | confidential provisional | 乐观并发；绑定证据版本；事务写确认与审计 | `TBD-SECURITY-003` |
| 回滚执行记录 | 控制台数据库；执行结果由部署源验证 | confidential provisional | 幂等键唯一；状态转换受状态机约束；审计同事务/可靠外盒 | `TBD-SECURITY-003` |
| 身份与授权 | 组织身份/策略系统 | personal/confidential provisional | 请求时服务端评估，不依赖客户端声明 | `TBD-SECURITY-003` |
| 模型输入输出 | not-applicable 直到 `TBD-AI-001` 批准 | pending | 不得进入基线数据流 | `TBD-AI-001` |

## 接口与集成

| Interface | Contract/versioning | Auth | Timeout/retry/idempotency | Degradation |
|---|---|---|---|---|
| Web API | 版本化 JSON schema；错误含稳定 code、correlation ID、结果状态 | 组织会话；CSRF 防护按会话方案 | 读请求可有限重试；命令携带幂等键 | 部分来源失败时返回分区状态，不制造完整快照 |
| 告警/目录读取 | 适配器把外部 ID 映射为 namespaced ID；契约测试固定 | 最小权限机器身份 | 超时与退避值 pending；读重试需有上限 | 使用带时间旧投影或显示不可用 |
| 部署命令 | 每种目标独立版本化适配器；明确 accepted 与 completed | 独立短期机器凭据 | 必须有请求幂等键；查询可重试；命令不盲重试 | 超时进入“状态未知”，由查询/人工升级解决 |
| webhook（若来源支持） | 验签、事件 ID 去重、schema 版本 | 共享密钥或非对称签名待来源确认 | 去重窗口 pending | webhook 失败可由受控轮询补偿 |
| 模型接口 | not-applicable 直到 `TBD-AI-001` | 不适用 | 不适用 | 不影响告警、影响确认和回滚核心旅程 |

具体供应商、配额、支持区域、字段和退出约束由 `TBD-ARCH-002` 盘点，不在无证据时指定。

## 技术与中间件决策

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|
| 应用形态 | 单团队假设；事务与审计强相关；需适配多个来源 | 模块化单体；微服务 | 模块化单体 | 模块边界需代码评审维护；换取较低部署和联调成本 | provisional | 出现独立团队/发布、隔离或量级证据 |
| 主存储 | 确认、幂等、审计需事务与查询 | 托管关系库；文档库 | 托管关系数据库 | 需要 schema 迁移；换取事务和约束 | provisional | 数据模型或区域要求不适配 |
| 后台作业 | 回滚长任务必须耐进程重启与重复回调 | 数据库作业 worker；消息代理 | 数据库支持的持久 worker | 高吞吐和复杂 fan-out 能力有限 | provisional | 已测突发/重试/fan-out 超出数据库预算 |
| 更新通道 | 用户需要状态更新但延迟目标未知 | 有界轮询；SSE/WebSocket | 有界轮询，页面可见时启用 | 额外读请求；实现和降级更简单 | provisional | `TBD-SPEC-001` 要求服务器推送延迟 |
| 缓存 | 当前无热点读证据 | 无共享缓存；Redis | 不引入 Redis；使用数据库投影与 HTTP 缓存语义 | 高峰读取能力待测 | provisional | 测得热点或共享临时协调需求 |
| 搜索 | MVP 为结构化筛选，无相关性需求 | 数据库索引；搜索引擎 | 数据库索引 | 模糊检索有限 | provisional | 规格要求相关性、分词或复杂分面 |
| Web/服务端技术 | 团队技能与现有标准未知 | TypeScript 全栈；Python API + TS Web；组织现有栈 | `TBD-ARCH-003` 前不锁定；暂以类型化契约优先 | 延迟建立脚手架，避免误选团队不熟悉栈 | pending | 团队和平台事实确认 |
| LLM | 仅有审美要求；核心动作高风险 | 不接入；只读单模型；可切换模型适配层 | 基线不接入；若批准仅启用只读 Advisory | 首版少一项生成能力；避免无评测地扩大风险 | provisional | `TBD-AI-001` 有明确价值、评测、数据和成本边界 |
| Kubernetes | 无平台团队和工作负载证据 | 托管容器/PaaS；Kubernetes | 不指定 Kubernetes；优先组织已有托管运行平台 | 平台可移植性取决于组织环境 | provisional | 策略、调度或平台能力给出必要证据 |

## 高风险动态流

```text
用户 -> API: 提交目标 + 证据版本 + 幂等键
API -> IdentityPolicy: 服务端授权/审批校验
API -> Impact: 校验证据仍为当前版本
API -> Audit/DB: 原子写入请求与审计；失败则终止
API -> 用户: 返回唯一 execution_id（已受理）
Worker -> 部署适配器: 带幂等键发起/查询
部署适配器 -> Worker: accepted / running / terminal / unknown
Worker -> DB/Audit: 受约束状态转换与证据
用户 -> API: 查询执行状态；不凭连接中断推断结果
```

## 失败与演进

### 预期降级

- 告警或目录来源失败：保留分区结果并标来源时间；影响确认可能降为不可提交。
- 身份/策略不可用：已有页面可按安全评审结果只读，任何新回滚命令 fail closed。
- 数据库不可用：不接受确认或回滚；不得以客户端队列替代审计保障。
- 部署来源不可查询：执行显示“状态未知”，不盲重试命令。
- Advisory/模型不可用：隐藏建议或显示不可用，不影响证据查看和人工回滚旅程。

### 容量边界

用户数、告警率、服务数、关系边数、回滚并发、保留量和峰值形态均 pending。不得据此预设分片、消息代理、搜索集群或微服务。

### 拆分/替换触发条件

- 独立团队需要分别发布或安全隔离某模块时，再评估服务拆分。
- 数据库 worker 在真实峰值下无法满足经批准的排队/恢复预算时，再评估消息代理。
- 结构化数据库查询无法满足已批准检索行为与性能预算时，再评估搜索引擎。
- 有证据证明轮询无法满足状态新鲜度且基础设施支持时，再评估 SSE/WebSocket。
- 模型功能只有在离线评测、禁止结果、人工责任、数据处理、版本固定、成本/延迟预算均获批准后进入生产设计。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 指定架构/数据负责人并批准逻辑边界 | 工程负责人 | 实现启动前 | implementation-ready | pending |
| TBD-ARCH-002 | 盘点告警、目录、身份、部署和协作系统的契约、配额、区域、凭据与退出路径 | 集成负责人 | 集成设计前 | implementation-ready | pending |
| TBD-ARCH-003 | 依据团队技能、现有平台和支持策略锁定语言、框架、关系数据库与组件库 | 工程负责人 | 仓库初始化前 | implementation-ready | pending |
| TBD-AI-001 | 决定模型价值、输出契约、离线评测集/门槛、禁止结果、数据策略和降级 | 产品负责人、安全负责人 | 原型验收前 | implementation-ready | pending |
