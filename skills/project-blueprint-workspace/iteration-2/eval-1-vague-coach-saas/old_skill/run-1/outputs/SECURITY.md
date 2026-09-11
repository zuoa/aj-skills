---
blueprint_kind: security
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
---

# 安全与隐私

公众预约入口、教练账户和学员联系方式形成主要风险。地区、数据控制者、字段、保留期和身份方案未知。

| Data | Class | Access | State |
|---|---|---|---|
| 公开课程/时段 | public | 所有人 | provisional |
| 学员联系信息与预约 | personal/confidential | 相关教练及学员本人 | pending |
| 账户、会话、审计 | confidential | 最小授权运维/教练 | pending |

控制基线：TLS；服务端身份、对象所有权和字段授权；输入验证与速率限制；预订写入的事务保护；密钥不入库；敏感字段不进入普通日志；关键管理状态变更留审计记录。依赖使用锁文件、来源审查、漏洞和秘密扫描。OWASP ASVS/NIST SSDF 仅作风险检查表，不声称认证。

身份恢复、会话时长、登录保护、数据告知/同意、访问删除请求、事件响应和通知义务必须在目标市场明确后验证。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 确认数据字段/保留、地区义务、认证、授权、安全负责人和事件流程 | security/product owner | 生产设计前 | production-ready | pending |
