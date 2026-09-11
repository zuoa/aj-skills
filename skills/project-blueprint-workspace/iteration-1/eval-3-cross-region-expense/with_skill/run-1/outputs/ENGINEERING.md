---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 实现前声明假设、冲突和所依据的 PRD/SPEC ID；pending 行为不得被静默固化。
- 采用满足已确认要求的最小实现；模块化单体边界未证明不足前不拆微服务。
- 每次变更必须显式考虑 tenant context、home region、敏感日志、幂等、迁移、观测和回滚。
- 行为变化先更新 PRD/SPEC，再更新设计、架构、测试与代码。

## 仓库映射

| Area | Path | Responsibility | Read before changing |
|---|---|---|---|
| Product behavior | `PRD.md`, `SPEC.md`, `specs/` | 意图与可观察行为 | 对应 PRD/SPEC |
| UX | `DESIGN.md` | 三端交互、状态与无障碍 | 对应流程章节 |
| System design | `ARCHITECTURE.md`, `docs/adr/` | 边界、数据与技术决策 | 区域/模块/接口章节 |
| Security/operations | `SECURITY.md`, `DEPLOY.md` | 控制、发布、恢复与 owner | 风险和区域章节 |
| Source/tests | 待仓库建立后登记 | 产品实现与验证 | TBD-ENGINEERING-001 |

## 命令

| Purpose | Command | Scope/notes |
|---|---|---|
| Install | TBD-ENGINEERING-001 | 技术栈确认后登记唯一命令 |
| Dev | TBD-ENGINEERING-001 | 必须支持合成租户/假供应商 |
| Unit tests | TBD-ENGINEERING-001 | 领域状态机与策略 |
| Integration tests | TBD-ENGINEERING-001 | DB、对象存储、SSO/支付契约 |
| Typecheck/lint | TBD-ENGINEERING-001 | 阻断合并 |
| Build | TBD-ENGINEERING-001 | 生成不可变制品与 SBOM |

## 代码与依赖规则

- Language/framework conventions: 待团队能力与运行平台确认；不得仅因流行度选型。
- Module boundaries: 模块不得绕过公开接口读写其他模块表；所有 repository 方法显式接受 tenant/region context。
- Error/logging: 用户错误稳定且不泄露对象存在性；结构化日志含 correlation ID，不含发票正文、完整银行号、token、断言或 secret。
- Dependency policy: 锁定版本、来源可追溯、许可证/SCA/维护状态检查；新增外部 SDK 需安全与区域数据流评审。
- Generated code: OpenAPI/SDK/迁移产物由源生成且 CI 检查漂移；不得手改生成文件。

## 测试与评审门禁

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|
| 任一数据访问 | 正常权限、同租户越权、跨租户、错误区域 | 模块 owner+安全 |
| 费用/审批/预算状态机 | 单元+事务+并发+幂等+审计事件 | 产品/模块 owner |
| 文件上传 | 类型/大小、恶意文件、扫描超时、URL 重放、删除 | 安全/文件 owner |
| SSO/角色 | 协议负向、停用/撤销、配置变更、紧急访问 | 身份/安全 owner |
| 支付 | 沙箱契约、超时、重放、乱序、重复、对账差异 | 支付/安全 owner |
| 数据库迁移 | 前后兼容、回填、生产量级演练、回滚限制 | 数据/SRE owner |
| 区域/部署 | 策略检查、错误路由、EU 内备份恢复、RPO/RTO 演练 | SRE+法务/安全 |
| Web/mobile UI | SPEC E2E、无障碍、弱网、兼容窗口 | 产品/设计/移动 owner |

## 完成定义

- 相关 PRD/SPEC/ADR 当前有效，pending 假设已标记且不阻断目标 gate。
- 相关自动与人工检查通过并保存证据，不以代码审阅代替运行验证。
- tenant/region/security、迁移、观测、成本与回滚影响已处理。
- API/事件变更保持已批准移动兼容窗口；功能标志有 owner 与删除日期。
- 仅有意变更留在 diff，运行命令和 runbook 已同步。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认技术负责人、语言/框架、仓库布局、标准命令、覆盖门槛与 CI 平台 | 工程负责人 | 首个实现 PR 前 | implementation-ready | pending |

