---
blueprint_kind: security
blueprint_status: draft
owner: security-lead
last_reviewed: 2026-09-10
---

# 安全与隐私

## 风险范围

- 公网 Web、多租户、企业机密知识与可能含个人信息的聊天、AI 第三方处理。
- 安全负责人由技术负责人兼任；生产前指定事件响应值班人。

## 数据清单

| Data | Classification | Access | Region | Retention/deletion | State |
|---|---|---|---|---|---|
| 身份/角色 | personal/confidential | 本人、租户管理员、授权服务 | TBD-REGION-001 | 合同终止后删除，期限待确认 | pending |
| 对话/草稿 | confidential/personal | 会话坐席、审计角色 | TBD-REGION-001 | 企业策略；删除传播到索引 | pending |
| 企业知识/向量 | confidential | 租户管理员、检索服务 | TBD-REGION-001 | 版本化；撤回后禁用于新生成 | provisional |
| 审计/用量 | confidential | 安全/财务授权角色 | 同生产区域 | 防篡改；期限待确认 | pending |

## 信任边界与威胁

| Boundary/flow | Threat | Control | Verification | Owner |
|---|---|---|---|---|
| 客户端→平台 | 越权、重放、滥用 | OIDC、短期会话、RBAC、tenant_id 服务端绑定、幂等/限流 | ASVS 导向测试 | 后端 |
| 知识→检索 | 跨租户泄露、提示注入 | 行级租户隔离、发布状态过滤、内容标记、检索结果最小化 | 隔离/注入测试 | AI |
| 平台→LLM | 训练使用、过度披露、保留 | DPA/不训练条款、最小上下文、日志/保留配置、供应商 allowlist | 合同+配置审计 | 安全 |
| 模型→坐席 | 幻觉/恶意指令 | 仅草稿、来源显示、输出编码、无工具权限、人工确认 | 评测集+负向 E2E | AI |

## 身份与访问

| Actor | Authentication | Authorization/tenant boundary | Session policy | Audit |
|---|---|---|---|---|
| 坐席/管理员 | 企业 OIDC，管理员要求 MFA | RBAC + 租户范围 + 会话分配 | 短期、撤权失效 | 登录、查看敏感数据、确认发送、知识变更 |
| 服务身份 | 托管 workload identity | 最小 IAM，环境隔离 | 无静态长期密钥 | 管理操作与供应商调用 |

## AI 与企业数据控制

- 企业输入、输出、反馈和知识不得用于本平台跨租户训练，也不得交给会用于训练的供应商配置。
- 供应商上线门槛：合同/DPA、子处理者与地域清单、保留期/日志开关、删除与事件通知机制均完成审查；不合格即禁用 AI。
- Prompt、检索片段、草稿、确认者、模型/提示版本使用 correlation ID 关联；日志默认脱敏，不记录完整机密正文。
- 模型无发送、数据库写入或外部工具权限；最终发送控制位于确定性服务端状态机。

## 应用与供应链控制

- 所有输入做长度、编码和 schema 校验；富文本输出净化；MVP 不接收公共文件上传。
- 密钥进入托管 secret manager，90 天轮换或按供应商更短要求；禁止提交仓库或下发浏览器。
- 锁定依赖、生成 SBOM、CI 做 secret/dependency/SAST 扫描；高危漏洞发布前修复。
- 合并需评审；租户隔离、草稿越权发送和提示注入为强制测试项。

## 检测与事件响应

- 监测异常登录、跨租户拒绝、草稿越权、供应商错误、批量导出和密钥操作；安全审计与应用日志分权保存。
- P1：疑似跨租户泄露或密钥泄露，立即禁用相关入口/密钥并由安全负责人协调通知；保留 correlation ID 和审计证据。
- 事件后补充测试、轮换凭据并记录根因与整改期限。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 确认数据分类、保留/删除期限、地域、事件通知义务及供应商 DPA | 安全负责人/法务 | 生产数据接入前 | production-ready | pending |
