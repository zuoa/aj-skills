---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

- 以 PRD/SPEC ID 驱动变更；业务冲突先更新规格。
- 保持 TypeScript 模块化单体和 Flutter 移动客户端的最小边界，不自行加入微服务、Kafka、Elasticsearch、Redis 或 Kubernetes。
- 自动覆盖验证码、对象级授权、打卡幂等/离线冲突、上传限制/授权、推送偏好与失败降级。
- 移动端发布前在目标 iOS/Android 版本真机验证权限、深链、离线、动态字体和后台/推送行为。
- 不使用真实个人信息或照片作为夹具，不报告未运行的检查。

仓库、Flutter/Dart/Node 版本、包管理器与规范命令尚未提供，全部登记待定，不生成占位命令作为事实。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认仓库结构、版本、命令、测试矩阵、CI 和代码评审责任 | technical-owner | 实现前 | implementation-ready | pending |
