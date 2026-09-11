---
blueprint_kind: security
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
---

# 安全与隐私

## 风险范围

内部控制台能够影响生产环境。身份、授权、审批、审计和恢复控制必须独立于浏览器及 AI 输出；具体数据、地区和组织策略均未确认。

## 数据清单

| 数据 | 分类 | 用途 | 访问 | 保留/删除 | 状态 |
|---|---|---|---|---|---|
| 告警、服务、部署元数据 | internal/confidential provisional | 研判与预检 | 服务/环境级授权 | TBD-SECURITY-001 | pending |
| 人工判断、回滚与审计事件 | highly-sensitive operational provisional | 执行与复盘 | 操作者、审批者、审计员 | TBD-SECURITY-001 | pending |
| AI 输入/输出与引用 | confidential provisional | 辅助研判 | 最小权限、只读 | TBD-AI-001 | pending |

## 信任边界与控制

| 边界 | 威胁 | 控制 | 验证 |
|---|---|---|---|
| 浏览器到 API | 会话劫持、越权 | 企业 SSO、短期会话、服务端授权 | 权限矩阵负测 |
| API 到发布系统 | 重放、目标替换、竞态 | 短期机器身份、幂等键、提交时重检服务/环境/版本 | 重放与竞态测试 |
| AI gateway | 提示注入、泄露、伪造来源 | 最小上下文、来源白名单、结构校验、只读工具、人与策略批准 | 对抗评测 |
| 审计 sink | 删除或篡改 | 追加写、关联 ID；必需审计失败则拒绝高风险动作 | 故障注入 |

## 身份、供应链与响应

查看、确认、批准和执行是不同权限；具体 IdP、角色和职责分离见 `TBD-IDENTITY-001`。密钥进入专用 secret provider，不进入仓库、日志或模型上下文。锁定依赖、扫描漏洞并保留 SBOM。指定事件响应、证据保全和通知负责人之前不可上线。

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 完成安全负责人、数据分类、保留删除、地区和事件响应盘点 | 安全/合规负责人 | 生产架构批准前 | production-ready | pending |
| TBD-IDENTITY-001 | 确认 IdP、角色、策略、审批、委托和职责分离 | 安全负责人 | API 设计前 | implementation-ready | pending |
