---
blueprint_kind: engineering
blueprint_status: draft
owner: tech-lead
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 先更新 PRD/SPEC，再改变可观察行为；实现满足需求的最小方案。
- 保持 Conversation 不依赖 AI；任何模型错误都必须可人工绕过。
- 所有租户数据查询显式携带 tenant_id；所有消息写入使用幂等键。
- 不在日志、测试 fixture 或浏览器持久存储中复制企业正文和密钥。

## 仓库地图

| Area | Path | Responsibility | Read first |
|---|---|---|---|
| 产品/行为 | `PRD.md`, `SPEC.md`, `specs/` | 范围与验收 | PRD/SPEC |
| 体验/架构 | `DESIGN.md`, `ARCHITECTURE.md` | UI 与内部边界 | 对应文档 |
| 安全/运行 | `SECURITY.md`, `DEPLOY.md` | 控制与生产 | 对应文档 |
| 应用代码 | `apps/`, `packages/`（脚手架时建立） | Web、服务、共享模块 | ARCHITECTURE |

## 规范命令接口

项目脚手架必须提供以下稳定入口，底层工具可替换：

| Purpose | Command | Notes |
|---|---|---|
| Install | `make setup` | 锁文件安装 |
| Dev | `make dev` | 本地依赖与应用 |
| Unit/integration | `make test` | 含租户、幂等、审批状态机 |
| Typecheck/lint | `make check` | 格式、类型、静态扫描 |
| Build | `make build` | 可复现生产构建 |
| Blueprint | `python3 ../../../../../../project-blueprint/scripts/validate_blueprint.py .` | 按实际路径调整 |

## 代码、依赖与质量门禁

- 模型/实时供应商只能经 adapter 使用；供应商错误映射为稳定领域错误。
- API/event schema 版本化；消息、草稿、知识任务必须具备幂等/并发测试。
- 新生产依赖需记录用途、许可证、安全/数据影响、成本和退出路径。
- 合并要求：单元与集成测试、lint/typecheck、租户隔离负测；AI 变更另需离线评测，实时变更另需断线恢复测试。
- 发布前：4500 连接压测、首 token P95、模型故障演练、预算限额、备份恢复和回滚证据。

## 完成定义

- 相关 PRD/SPEC/架构决策保持当前；自动化与必要人工验证通过。
- 安全、迁移、观测、成本和回滚影响已处理；diff 仅含意图内修改。

## 待决定事项

无；脚手架阶段由技术负责人把上述 `make` 接口绑定到选定语言工具链。
