---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 行为冲突先更新 PRD/SPEC；只实现满足已确认规格的最小变化。
- 回滚授权、目标校验、幂等和审计在服务端完成；AI 输出不得持有执行权限。
- 无测量证据不引入缓存、消息队列、微服务或 Kubernetes。

## 命令与门禁

仓库、包管理器和 CI 未建立。`TBD-ENGINEERING-001` 关闭前，install/dev/test/lint/build 命令均为 pending，不得声称测试通过。

| Change | Required evidence |
|---|---|
| 告警/影响 | 正常、陈旧、冲突、权限和来源失败场景 |
| 回滚 | 状态机、竞态、重复提交、审计失败、未知终态和恢复演练 |
| UI | 键盘、焦点、非颜色状态、文本扩展和 reduced motion |
| AI | 离线评测、提示注入、引用完整性、无模型降级 |

## 完成定义

相关 ID 与追踪矩阵更新；证据可复核；安全、迁移、观测和回滚影响已处理；diff 只含有意变化。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认仓库、团队栈、组件原语、规范命令与 CI 门禁 | 工程负责人 | 首个实现任务前 | implementation-ready | pending |
