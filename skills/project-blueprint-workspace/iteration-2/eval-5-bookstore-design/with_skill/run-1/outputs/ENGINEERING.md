---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 实现前引用 PRD/SPEC ID，暴露冲突与假设；行为变更先改规格。
- 从模块化单体和关系数据库开始，不在缺少证据时加入缓存、搜索集群、消息代理、微服务或 Kubernetes。
- 店员/顾客权限、预订并发和审计属于必须自动验证的高风险路径。
- 不声称未运行的测试通过；日志和测试夹具不使用真实顾客资料。

## 仓库与命令

代码仓库和技术栈尚未建立。目录、安装、开发、测试、类型检查、lint、构建和迁移命令均由 `TBD-ENGINEERING-001` 确认后写入，禁止用示例命令冒充事实。

## 测试与评审门禁

| Change | Required evidence |
|---|---|
| 目录字段/检索 | 单元与 API 契约测试；桌面/手机可用性检查 |
| 预订状态/并发 | 状态机、事务并发、幂等与恢复测试 |
| 身份/权限 | 角色矩阵、对象级访问和直接 URL 测试 |
| 数据迁移 | 前后兼容、备份/恢复与回滚限制说明 |
| UI | 键盘、焦点、窄屏、文本扩展及状态矩阵检查 |

## 完成定义

相关蓝图与追踪矩阵已更新；适用自动/人工检查有证据；安全、迁移、观测和回滚影响已评审；差异中只剩有意更改。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认代码仓库、语言/框架、规范命令、测试工具和评审责任 | technical-owner | 实现前 | implementation-ready | pending |
