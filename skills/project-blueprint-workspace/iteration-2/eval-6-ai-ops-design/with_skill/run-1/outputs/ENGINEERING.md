---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

## 实现纪律

- 先读取相关 PRD、领域 SPEC、DESIGN、安全和架构章节；行为冲突先改权威规格。
- 回滚授权、目标校验、幂等和审计在服务端实现，不依赖界面或模型输出。
- 保持模块化单体边界；没有测量证据不引入缓存、消息队列、微服务或 Kubernetes。
- 任何 AI 能力保持只读、可关闭、可追踪版本，并提供不依赖模型的任务路径。

## 仓库与命令

仓库、语言、包管理器和 CI 尚未建立，不能提供虚假命令。由 `TBD-ENGINEERING-001` 确认后替换下表。

| Purpose | Command | Gate |
|---|---|---|
| Install/dev/test/lint/build | pending | implementation-ready |

## 测试门禁

| 变更 | 必需证据 |
|---|---|
| 告警/影响行为 | 正常、陈旧、冲突、权限和来源失败场景 |
| 回滚 | 状态机、竞态、重复提交、审计失败、未知终态和取消/补救演练 |
| UI | 键盘、焦点、非颜色状态、文本扩展、reduced motion 和状态文案验收 |
| 安全/依赖 | 静态检查、依赖扫描、权限负测与威胁评审 |

## 完成定义

相关 ID 与追踪矩阵保持最新；自动化与人工证据可复核；安全、迁移、观测和回滚影响已处理；diff 只含有意变化。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认仓库、团队栈、组件原语、规范命令和 CI 质量门禁 | 工程负责人 | 首个实现任务前 | implementation-ready | pending |
