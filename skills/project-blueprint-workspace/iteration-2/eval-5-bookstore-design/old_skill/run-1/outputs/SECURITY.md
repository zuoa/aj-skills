---
blueprint_kind: security
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
---

# 安全与隐私

## 风险画像

公众可访问目录，店员端具有库存和顾客预订资料的管理权限。联系方式属于个人数据；地区、控制者、字段、保留期和通知义务未知。本蓝图使用 OWASP ASVS/NIST SSDF 作为检查框架，不声称认证或法律合规。

## 数据清单

| Data | Class | Purpose/access | Retention/deletion | State |
|---|---|---|---|---|
| 公开书目、价格、品相 | public/business | 顾客与店员查找单册 | 下架/历史策略待定 | provisional |
| 库存内部字段 | internal | 授权店员 | 待定 | pending |
| 顾客联系方式、预订 | personal/confidential | 顾客本人和授权店员 | 待定 | pending |
| 账户、会话、审计 | confidential | 授权运维/审计 | 待定 | pending |

## 信任边界与控制

- 公网到应用：TLS、输入验证、速率/滥用限制；阈值由风险测试确定。
- 顾客到店员数据：默认拒绝、服务端授权、对象级访问测试；不依赖隐藏按钮。
- 应用到数据库：最小权限凭据、托管密钥、备份加密和网络限制。
- 管理状态变更：记录操作者、目标、前后状态、时间和关联 ID；日志不得记录完整敏感字段。
- 预订冲突：在事务边界内执行，不以客户端检查代替。

## 身份与供应链

店员认证方式、角色数量、会话时长、恢复与离职撤权均 pending。暂定只设 staff 角色，扩大权限模型需业务证据。依赖必须锁定版本、记录来源并在 CI 进行漏洞/秘密扫描；高风险发现的修复时限由安全负责人确定。

## 隐私与事件响应

只收集完成预订所需字段；同意/告知文案、导出/删除请求和数据驻留须依据目标市场核实。事件需保留审计证据、指定升级联系人和用户沟通责任，未指定前 production-ready 阻断。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 确认市场、数据字段/保留、身份方案、安全负责人和事件流程 | bookstore-owner/security-owner | 上线设计前 | production-ready | pending |
