---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 实现前说明假设、歧义和冲突；pending 决策不得静默固化为代码事实。
- 只实现 confirmed/provisional 且已获当前阶段批准的规格，优先满足约束的最小方案。
- 行为改变先更新 PRD/SPEC，再更新设计、架构、测试与代码。
- 保持工作区授权、预约事务和幂等边界，不以 UI 隐藏代替服务端控制。
- 只修改需求直接相关范围；验证后再宣称完成。

## 仓库地图

| Area | Path | Responsibility | Read before changing |
|---|---|---|---|
| 产品意图 | `PRD.md` | 用户、问题、范围和结果 | 所有功能变更 |
| 行为规格 | `SPEC.md`, `specs/` | 外部可观察行为与追踪 | 所有行为、测试变更 |
| 体验 | `DESIGN.md` | 页面、交互、状态、无障碍 | UI 变更 |
| 内部边界 | `ARCHITECTURE.md` | 模块、数据、一致性和依赖 | API、数据与集成变更 |
| 安全/运行 | `SECURITY.md`, `DEPLOY.md` | 控制、交付和恢复 | 身份、数据、基础设施变更 |
| 业务代码 | 尚不存在 | 待 TBD-ARCH-001 决定目录 | 开始实现前 |

## 命令

技术栈和仓库尚未建立，以下命令必须在 TBD-ENGINEERING-001 决定后填写，不得猜测：

| Purpose | Command | Scope/notes |
|---|---|---|
| Install | pending | 锁定依赖；禁止未评审的全局安装 |
| Dev | pending | 本地使用非生产数据与密钥 |
| Unit tests | pending | 领域规则与模块边界 |
| Integration/E2E | pending | 数据库事务、授权和关键预约旅程 |
| Typecheck/lint | pending | 按选定语言统一执行 |
| Build | pending | 生成可追溯不可变制品 |
| Blueprint validation | `python3 /Users/yujian/Code/py/aj-skills/skills/project-blueprint/scripts/validate_blueprint.py .` | 在蓝图根目录运行 |

## 代码与依赖规则

- **语言/框架**：pending，TBD-ARCH-001；选择前比较团队能力、托管适配、生态安全与退出成本，不以流行度决定。
- **模块边界**：Identity & Workspace、Scheduling、Booking、Coach Read Model；跨模块经明确接口，禁止绕过授权或预约事务约束直写数据。
- **错误/日志**：外部错误与 SPEC 一致；内部使用结构化、可关联日志，禁止记录秘密或不必要个人数据。
- **依赖**：使用锁文件；新增依赖说明用途、替代方案、维护/安全状况和移除路径；自动检查已知漏洞。
- **生成代码**：必须可重复生成、记录来源与命令；不要手改生成结果，除非仓库明确规定。

## 测试与评审门禁

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|
| 预约/排班规则 | 关联 SPEC 的正常、边界、失败及并发/幂等测试；追踪矩阵更新 | 产品与技术负责人（未指定） |
| 身份/工作区访问 | 未认证、跨工作区、对象级授权负向测试；安全评审 | 安全负责人（未指定） |
| UI/内容 | 关键视口任务测试、键盘/焦点、语义与状态矩阵检查 | 设计/产品负责人（未指定） |
| 数据库迁移 | 兼容性、前向迁移、回滚限制、备份/恢复影响 | 技术/运维负责人（未指定） |
| 依赖/运行时 | 锁文件、构建、测试、漏洞与来源检查 | 技术负责人（未指定） |
| 发布配置 | preview 验证、秘密/权限、观测、迁移和回滚证据 | 生产负责人（未指定） |

任何测试状态在真实执行前只能为 `planned`，不得标记 `passed`。

## 完成定义

- 相关 PRD/SPEC/ADR（如有）已更新且无未说明冲突。
- 所有适用自动化检查和手动验收已执行并留证；失败没有被隐藏。
- 安全、个人数据、迁移、可观测性、成本和回滚影响已评估。
- 新行为覆盖正常及相关失败、权限、并发、离线/恢复场景。
- 文档链接与蓝图校验通过；工作树只包含意图内改动。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 选定仓库结构、包管理、标准命令、测试工具、CI 门禁和评审责任 | 技术负责人（未指定） | 创建代码脚手架前 | implementation-ready | pending |

