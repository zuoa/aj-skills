---
blueprint_kind: security
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
---

# 安全与隐私蓝图

## 风险画像与范围

- Users and exposure: 公网 Web/移动客户端、企业用户、特权企业管理员、平台运营人员、IdP 与支付供应商。
- Sensitive capabilities: 多租户、公开文件上传、SSO、角色/预算管理、银行账户引用、支付指令、审计导出、跨区域运营。
- Applicable markets/regimes to verify: 中国大陆、欧盟成员国与美国客户所在地及行业/合同要求。**[LEGAL REVIEW] TBD-LEGAL-001**。
- Security owner: **[SECURITY OWNER] TBD-SECURITY-001**。
- 本文用 OWASP ASVS、移动安全与 NIST SSDF 思路作为工程检查清单，不代表认证、审计通过或法律合规结论。

## 数据清单

| Data | Classification | Purpose/source | Access | Region | Retention/deletion | State |
|---|---|---|---|---|---|---|
| 身份属性（姓名、邮箱、员工号、角色） | personal/confidential | SSO 与授权 | 用户本人、租户管理员、受控支持 | 租户 home region | **[LEGAL] TBD-LEGAL-001** | pending |
| 发票原件与预览 | sensitive personal/confidential | 费用证据；用户上传 | 提交人、审批链、授权财务/审计 | EU 租户仅 EU；其他按 home region | **[LEGAL] TBD-LEGAL-001** | pending |
| 费用/预算/审批 | confidential，可能含 personal | 管理费用 | 角色+资源范围 | home region | **[LEGAL] TBD-LEGAL-001** | pending |
| 银行账户信息 | sensitive personal/financial | 支付 | 最小授权财务角色；优先 token/掩码 | home region 与批准供应商区域 | **[LEGAL/SECURITY] TBD-PAYMENT-001** | pending |
| 支付状态与供应商引用 | financial/confidential | 付款与对账 | 财务角色、审计、受控支持 | home region | **[LEGAL] TBD-LEGAL-001** | pending |
| 审计日志 | confidential，可能含 personal | 追溯和响应 | 租户审计员/平台安全按范围 | 与业务对象同区域 | **[LEGAL/SECURITY] TBD-SECURITY-002** | pending |
| 路由元数据 | internal/confidential | 选择 home region | 平台服务和极少数运营人员 | 暂定全球；不得含直接身份/业务载荷 | **[LEGAL/SECURITY] TBD-LEGAL-001** | pending |

## 信任边界与威胁

| Boundary/flow | Threat or abuse case | Control | Verification | Owner |
|---|---|---|---|---|
| Client → regional API | 令牌盗用、租户 ID 篡改、越权 | 服务端会话验证、tenant context、对象级授权、限流 | 跨租户自动测试+渗透测试 | 安全/应用 |
| Browser/mobile → file store | 恶意文件、公开 URL、元数据泄露 | 隔离区、类型/大小校验、恶意软件扫描、短期签名 URL、派生预览 | 文件语料库与 URL 重放测试 | 安全/平台 |
| API → IdP | 伪造断言、重放、错误租户 | 签名、issuer/audience、nonce/state、时间窗、配置审批 | SSO 负向契约测试 | 身份团队 |
| Regional worker → payment | 重复付款、凭据泄露、供应商劫持 | 幂等键、出站 allowlist、密钥托管、对账、双人审批按风险 | 沙箱+故障注入+密钥访问审计 | 支付/安全 |
| Payment webhook → API | 假回调、重放、乱序 | 签名、事件 ID、时间窗、状态机、隔离队列 | 重放/乱序/签名测试 | 支付团队 |
| Region → observability/support | 敏感数据跨区、内部滥用 | 区域日志池、默认脱敏、JIT 访问、EU 支持边界 | DLP/字段抽查+访问复核 | 安全/SRE |
| CI/CD → production | 供应链篡改、越权部署 | 固定依赖、制品签名/SBOM、受保护环境、最小权限 | provenance 验证与部署审计 | 平台团队 |

## 身份与访问

| Actor | Authentication | Authorization/tenant boundary | Session/credential policy | Audit |
|---|---|---|---|---|
| 员工/经理 | 租户 SSO，协议待定 | RBAC+tenant+组织/审批范围 | 短期会话、撤销与空闲/绝对时限待确认 | 登录、失败、敏感读写 |
| 企业管理员 | 租户 SSO+强认证要求待确认 | 租户内管理权限，敏感操作再确认 | 禁止共享账号；会话风险控制 | 角色、SSO、预算、导出 |
| 平台运营/支持 | 企业身份+强 MFA | 默认无业务数据；JIT、工单、时限与最小范围 | 受管设备与特权会话 | 全量访问和审批链 |
| 服务身份 | workload identity | 单区域、单服务、单资源权限 | 无静态长寿命密钥为目标 | 令牌颁发和异常访问 |

## 应用与供应链控制

- Validation and upload handling: 客户端校验不可信；服务端白名单字段、金额边界、内容嗅探、随机对象键、隔离扫描；扫描失败关闭。
- Tenant isolation: 所有领域仓储要求 tenant context；对象键与加密上下文含租户/区域；禁止仅靠 UI 过滤；生产前做跨租户 IDOR 与批量接口测试。
- Encryption: TLS 传输；托管存储加密；区域独立密钥，发票/银行相关数据是否需要字段级或租户级密钥由 TBD-SECURITY-002 决定。
- Rate/abuse controls: 按账号、租户、IP、上传字节、登录/回调端点分层限流；不以限流替代授权。
- Secrets and key rotation: 专用 secret manager、workload identity、无仓库密钥；轮换、吊销和 break-glass 演练由安全 owner 批准。
- Dependency provenance and updates: 锁文件、受信 registry、SBOM、SCA、镜像/制品签名、支持版本策略；高危修复 SLA 待安全负责人确认。
- Security checks: PR 必须进行静态分析、依赖/secret 扫描；发布前威胁建模、SSO/支付/上传/租户隔离专项评审与独立渗透测试。

## 隐私与区域核实清单（非合规结论）

| Question/requirement | Official source/date | Engineering response | Owner | State |
|---|---|---|---|---|
| EU 中哪些主体/数据/备份/日志/远程访问受驻留约束，跨境机制如何处理 | **[LEGAL] 由法务列出适用的欧盟/成员国官方来源；尚未核验** | 默认所有 EU 租户业务与可识别运行数据留 EU，跨区失败关闭 | 法务负责人 | pending |
| 中国大陆主体、托管/备案、个人信息与跨境处理要求 | **[LEGAL] 由中国法务基于主管机关官方来源核验** | CN 独立数据面；SDK/处理者/跨境清单未批准前不启用 | 中国法务/隐私负责人 | pending |
| 美国联邦、州、行业和合同义务 | **[LEGAL] 由美国法务基于官方来源核验** | US 数据面、权利请求与保留策略按批准矩阵配置 | 美国法务/隐私负责人 | pending |
| 控制者/处理者角色、DPA、子处理者、合法基础、通知/同意与权利请求 SLA | **[LEGAL] 尚未核验** | 建立处理活动、供应商与数据权利工作流；不在代码中假定统一规则 | 法务/隐私负责人 | pending |
| 支付范围、资金流、银行信息字段、供应商责任与事件通知 | **[LEGAL/SECURITY] 尚未核验** | tokenization、最小字段、区域供应商适配和对账 | 支付法务/安全负责人 | pending |

## 检测与事件响应

- Detection and evidence: 认证异常、跨租户拒绝、特权访问、预算/审批/支付变更、回调失败、区域策略拒绝与审计管道中断均需告警或可查询证据；日志禁止记录原始发票、完整银行号、token 或断言。
- Severity/escalation: **[SECURITY OWNER]** 需定义 SEV 分级、24×7 路由、供应商升级、法务通知判断与证据保全。
- Response and communication owner: TBD-SECURITY-001；区域事件不得把 EU 证据复制到区外作为默认响应方式。
- Post-incident: 根因、控制缺口、补救 owner/期限与复盘；法律通知由法务判断，蓝图不预判结论。

## 发布前安全证据

- 跨租户、对象级授权、管理员与支持访问测试通过。
- 文件上传恶意语料、签名 URL、支付幂等/回调、SSO 负向测试通过。
- 数据流/资产/子处理者/驻留矩阵经 **[LEGAL REVIEW]** 签字。
- 威胁模型、独立渗透测试和高严重性问题关闭或经 **[SECURITY OWNER]** 风险接受。
- 区域日志、备份、恢复、删除和事件响应演练有证据。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-LEGAL-001 | **[LEGAL REVIEW]** 确认中/欧/美适用义务、数据角色、驻留/跨境、保留删除、子处理者与支付责任矩阵 | 各辖区法务/隐私负责人 | 供应商签约和生产设计冻结前 | production-ready | pending |
| TBD-SECURITY-001 | **[SECURITY OWNER]** 任命安全负责人并批准威胁模型、身份基线、测试与事件响应 | CISO/安全负责人 | 实现前（基线）及上线前（验收） | production-ready | pending |
| TBD-SECURITY-002 | **[SECURITY OWNER]** 确认加密粒度、密钥轮换、日志/审计保留、防篡改和修复 SLA | 安全负责人 | 数据模型冻结前 | production-ready | pending |

