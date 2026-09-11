---
blueprint_kind: security
blueprint_status: draft
owner: security-owner
last_reviewed: 2026-09-10
---

# 安全与隐私

## 风险画像与范围

- 面向中国大陆公网，含手机号登录、私密照片、训练/打卡、推送 token 和教练特权端，风险为中高；照片与训练记录按敏感个人信息做保守工程保护。
- 最大滥用面：短信轰炸/撞库替代攻击、会员/教练对象级越权、照片 URL 泄露、恶意文件、被盗教练账号、第三方 SDK 越界收集、批量导出和删除不彻底。
- 不在 MVP：支付、公开 UGC、聊天、精确位置、医疗诊断、未成年人、AI。任一进入即重做威胁建模。
- 本文件是工程控制基线，不是法律意见；privacy-owner 负责委托中国大陆专业人员作发布结论。

## 数据清单

| Data | Classification | Purpose/source | Access | Region | Retention/deletion | State |
|---|---|---|---|---|---|---|
| 手机号 | 个人信息 | 登录、账号通知；用户输入 | 本人；必要客服；认证服务 | 中国大陆 | 账号期；注销后 30 天内删除/不可逆散列（争议保留另审） | provisional |
| OTP challenge/风控信号 | 认证机密/个人信息 | 登录与反滥用 | Identity、受限安全人员 | 中国大陆 | challenge 10 分钟；安全日志 180 天 | provisional |
| 计划/教练关系 | 个人信息/内部 | 个性化训练与授权 | 本人、当前教练、必要运营 | 中国大陆 | 账号/服务关系期；注销后 30 天 | provisional |
| 打卡、感受 | 敏感个人信息（保守） | 习惯记录/教练跟进 | 本人、当前教练 | 中国大陆 | 账号期；权利请求/注销后 30 天 | provisional |
| 照片 | 敏感个人信息（保守） | 可选训练记录 | 本人、当前教练；处理 worker | 中国大陆 | 主动删后在线 24h；注销后 30 天；加密备份最长 35 天滚动到期 | provisional |
| 时区/提醒设置 | 个人信息 | 本地时间调度 | 本人、Reminder | 中国大陆 | 账号期；关闭删除未需字段；注销同账号 | provisional |
| 设备 push token | 个人信息/凭据 | 投递提醒 | Reminder、已批准处理者 | 中国大陆为主；APNs 路径须单独评估 | token 失效/退出所有设备/注销后删除 | provisional |
| 管理/敏感读取审计 | 安全数据，可能含个人标识 | 追责、调查 | 安全/审计角色 | 中国大陆 | 180 天，事故证据按审批延长 | provisional |
| 产品分析 | 去标识事件 | 核心漏斗/稳定性 | 产品受限角色 | 中国大陆 | 原始 90 天，聚合 13 个月 | provisional |

禁止收集：通讯录、精确位置、身份证、人脸模板、麦克风、身体活动、广告标识；若功能变更需要，先更新 PRD/SPEC、PIPIA/权限清单和告知。照片不作人脸识别或健康推断。

## 信任边界与威胁

| Boundary/flow | Threat or abuse case | Control | Verification | Owner |
|---|---|---|---|---|
| Client→API | OTP 枚举、短信轰炸、伪造 token、重放 | 统一响应；号码/设备/IP/ASN 限流；挑战单次；token 轮换 | 自动化滥用/重放测试，短信账单告警 | security-owner |
| Coach→member data | IDOR、批量爬取、被盗账号 | 服务端对象级授权；MFA（管理员）；异常批量读取告警；短会话 | 授权矩阵、渗透测试、月度审计抽样 | backend-lead |
| Client→object | MIME 伪装、超大/解压炸弹、公开桶、EXIF 泄露 | 限定签名；magic-byte/尺寸/解码校验；隔离处理；私有桶；重编码去 EXIF | 恶意语料测试、云配置扫描、公开访问探测 | security-owner |
| API→provider | 密钥泄露、供应商越界处理、重试重复 | vault、最小字段、adapter、DPA/SDK 清单、幂等 provider ID | secret scan、季度 key review、供应商证据 | ops-owner |
| Build→release | 依赖投毒、签名凭据泄露、制品替换 | lockfile、固定 action digest、SCA/SAST、SBOM、签名制品、受保护环境 | CI 证据、发布 provenance 抽查 | tech-lead |
| Database/backup | 注入、误删、备份泄露 | 参数化查询、最小 DB 角色、私网 TLS、加密备份、PITR、双人恢复审批 | SQLi 测试、权限审查、季度恢复演练 | backend-lead |
| Logging/analytics | 手机/照片 URL/token 进入日志或境外 | allowlist 结构日志、字段脱敏、禁 body/header、国内端点 | 日志 DLP 扫描、SDK 动态检测 | security-owner |

## 身份与访问

| Actor | Authentication | Authorization/tenant boundary | Session/credential policy | Audit |
|---|---|---|---|---|
| 访客 | 无 | 仅体验训练与公开告知 | 无持久个人标识；必要安全 cookie 短期 | 聚合安全事件 |
| 会员 | 手机 OTP | 仅自己对象；教练关系由服务端判定 | 15m access + 30d rotating refresh provisional；安全存储/cookie | 登录、全端退出、权利请求 |
| 教练 | 邀请账号 + 手机 OTP；M2 评估 MFA | 仅当前分配会员，无跨教练查询 | 空闲 30m、最长 12h provisional；敏感操作重认证 | 登录、搜索、敏感详情/照片读取、计划发布 |
| 运营管理员 | 企业受控账号 + MFA | 最小角色；无默认照片批量访问 | 8h 上限；紧急权限限时、双人审批 | 所有管理写入与导出 |
| Workload/CI | 短期工作负载身份优先 | 每服务/环境最小云 IAM | 不在代码/镜像；90 天轮换兜底 | secret access、部署、迁移 |

- CSRF：cookie Web 会话使用 SameSite + origin/CSRF token；CORS 精确 allowlist。
- XSS：Flutter Web/托管页面禁任意 HTML；严格 CSP；用户文本按纯文本渲染。
- 账号恢复/换号不在自助 MVP；由受审计客服流程进行控制权核验，禁止仅凭旧手机号之外的弱信息直接换绑。

## 应用与供应链控制

- API 使用 schema allowlist、长度/枚举/日期边界校验；ORM 参数化；统一错误映射；每个写接口有对象授权和幂等策略。
- 上传仅通过隔离前缀；不信任扩展名/MIME；限制像素、解码内存和处理时间；处理 worker 无公网入站、最小对象权限；不安全文件拒绝并删除。
- 限流分层：边缘 IP、设备挑战、手机号、账号、教练搜索/导出；阈值从压测和攻击演练校准，不能只依赖客户端。
- secrets 进入国内云 KMS/secret manager；开发、预发、生产隔离；短信/APNs/推送/对象密钥各自最小权限；泄露后可独立吊销。
- 每个第三方 SDK 建立名称、版本、目的、字段、权限、启动时机、域名、地域、处理者、退出方案；未过动态流量与权限审查不得进入 release 分支。
- 依赖必须来自官方 registry、提交 lockfile、禁止未审查 postinstall；CI 做 secret scan、SCA、SAST、IaC/镜像扫描和 SBOM；critical 24h、high 7d、medium 30d 修复目标为 provisional。
- 以 NIST SSDF 与 OWASP ASVS Level 2 作为检查清单，不声明认证。合并需要至少一名非作者审查；认证/授权/上传/删除需 security-owner 复核。

## 隐私与区域义务

以下均为发布前核实项；访问日期均为 2026-09-10。

| Question/requirement | Official source/date | Engineering response | Owner | State |
|---|---|---|---|---|
| 个人信息与敏感信息保护、权利、影响评估 | [《个人信息保护法》中国人大网](https://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313088.html)，2021-08-20 | 数据最小化、分层告知、保守敏感分类、权利工单；照片/训练、第三方、注销和潜在出境做 PIPIA | privacy-owner | provisional；法律复核待完成 |
| 运动健身基本功能的必要信息 | [《常见类型移动互联网应用程序必要个人信息范围规定》](https://www.cac.gov.cn/2021-03/22/c_1617990997054277.htm)，2021-03-22 | 保留无需登录的体验训练；手机号仅用于保存个性化计划/打卡的账号能力；不得因拒绝照片/通知而阻断训练 | product-owner | provisional；确认产品分类后冻结 |
| App 信息服务与权限/个人信息规则 | [《移动互联网应用程序信息服务管理规定》](https://www.cac.gov.cn/2022-06/14/c_1656821626455324.htm)，2022-06-14 | 权限按需、SDK 清单、公开规则、安全缺陷响应；上架前做静态/动态合规检测 | privacy-owner | provisional |
| ICP 与 APP 备案 | [工信部 APP 备案通知解读](https://www.miit.gov.cn/zwgk/zcjd/art/2023/art_39b4f1acc36745b98478e0ec3e07128d.html)，2023-08；[非经营性互联网信息服务备案管理办法](https://www.miit.gov.cn/zcfg/xxtxl/art/2024/art_7e48434c08c24131b4b7eecfca5b2b6c.html)，2024 修订 | 中国大陆主体、域名、接入商、网站/APP 材料作为关键路径；实际许可/备案类别由专业人员确认 | product-owner | pending（TBD-COMPLIANCE-001） |
| 数据跨境 | [《促进和规范数据跨境流动规定》](https://www.cac.gov.cn/2024-03/22/c_1712776611775634.htm)，2024-03-22 | 默认生产个人数据、日志与支持访问不出境；APNs/崩溃/分析等逐项画流并评估告知、单独同意/PIPIA及适用机制 | privacy-owner | provisional；任何境外接收方触发重评 |

未成年人：MVP provisional 只面向 18+，不以此替代年龄/实际使用评估。若接纳或识别到未成年人，停止扩大发布，补充监护同意、未成年人模式与专项评估。健康：训练/照片可能反映健康或生物特征，保守按敏感信息控制；不得用于诊断、画像广告或模型训练。

## 安全验证与发布门禁

| 时点 | Evidence | Pass condition | Owner |
|---|---|---|---|
| 每次 PR | unit/integration、SAST/SCA/secret/IaC scan | 无新增 critical/high；授权测试通过 | code owner |
| M2 | OTP 滥用、push/SDK、上传 threat review | 数据流/权限清单完整；公开桶测试失败（即不可公开） | security-owner |
| M4 | 全量 ASVS L2 风险映射、移动动态检测 | 无未接受 critical/high；隐私声明与实际流量一致 | security-owner/privacy-owner |
| M5 | 独立渗透测试 + 修复复测 | critical/high 清零；medium 有负责人/期限 | product-owner |
| 发布前 | 权限/SDK/备案/商店隐私表、恢复/事件演练 | 所有 production blocker 有证据并签字 | release-owner |

## 检测与事件响应

- 监测：OTP 发送突增/失败率、认证异常、教练批量读取、对象 403/签名异常、管理权限变化、DLP 命中、依赖高危和备份失败；日志用 correlation ID，禁止手机号明文/验证码/token/签名 URL。
- 严重度 provisional：SEV-1 为持续未授权访问、敏感照片/认证机密泄露或大面积不可恢复丢失，15 分钟确认、30 分钟召集；SEV-2 为受限泄露/核心功能显著故障，30 分钟确认。
- 步骤：遏制→保全云审计/访问/发布证据→轮换/封禁→影响评估→依法/依合同通知由 privacy-owner 决定→恢复→5 个工作日内复盘与规格修订。
- 证据存于独立受限账号/桶，哈希校验、访问审计；不得在普通工单附照片或完整手机号。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 指定具名 security/privacy owner，批准数据清单、PIPIA、渗透范围和事件联系人 | product-owner | M1 第 2 周；复核 M4 | production-ready | pending |
| TBD-PROVIDER-001 | 冻结云、短信、Android push、分析/崩溃处理者与 SDK 清单，完成合同、地域、权限、退出和跨境评估 | privacy-owner | M2 末 | production-ready | pending |

