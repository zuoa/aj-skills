---
blueprint_kind: engineering
blueprint_status: draft
owner: engineering-lead
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 实现前标明假设、冲突和关联 PRD/SPEC ID。
- 选择满足已确认行为的最小实现，保持 Actions、Records、Safety 等模块边界。
- 不以截图或视觉检查代替语义、键盘、屏幕阅读器和授权测试。
- 未运行检查不得宣称完成；运行命令、环境和结果进入变更证据。

## 仓库地图与命令

仓库尚未创建。客户端、API、测试和部署目录在 TBD-ENGINEERING-001 中一次确认，之后由本节作为权威来源。

| Purpose | Command | Scope/notes |
|---|---|---|
| Install | pending | 锁文件与受支持运行时确定后填写 |
| Dev | pending | 必须使用合成青少年账号/数据 |
| Unit/integration | pending | 覆盖状态机、幂等和对象级授权 |
| Accessibility | pending | 自动检查加人工屏幕阅读器、键盘和触控任务 |
| Typecheck/lint/build | pending | 合并前必需，具体工具随栈确认 |

## 代码与依赖规则

- UI 状态来自明确枚举，必须有可见文字和程序化语义映射；不得从颜色或图标反推状态。
- 完成记录成功文案与品牌 Emoji 例外集中管理，按 DESIGN.md 的唯一位置、数量和无障碍规则测试。
- 写接口带幂等策略；权限在服务端按对象校验；日志使用稳定错误码且不记录用户正文。
- 新依赖需说明用途、维护状态、许可证、安全影响和移除路径；锁定版本并自动扫描。
- 生成代码不得跳过评审、测试或可追溯性。

## 测试与评审门禁

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|
| 报名/完成状态 | SPEC 场景、幂等、失败恢复、文案与语义状态 | product + QA |
| UI/组件 | 单元/端到端、键盘、焦点、触控、200% 文本和屏幕阅读器 | accessibility lead |
| 品牌文案 | 仅许可成功消息含一个树叶 Emoji；其余团队 UI 字符串扫描为零 | brand + accessibility leads |
| 权限/数据 | 对象级授权、上传滥用、日志脱敏和删除/保留 | security/privacy leads |
| 数据库/部署 | 迁移兼容、备份恢复、监控、回滚/前向修复 | operations lead |

## Definition of done

- PRD/SPEC/ADR 与行为一致，追踪矩阵已更新。
- 自动检查通过，相关屏幕阅读器、键盘和触控人工测试附有证据。
- 安全、迁移、观测、回滚和数据生命周期影响已评估。
- 变更中只保留有意内容；没有未登记 Emoji 或与品牌例外冲突的字符串。

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认代码仓库结构、技术栈、canonical commands 与 CI 门禁 | engineering lead | 首个实现任务前 | implementation-ready | pending |
