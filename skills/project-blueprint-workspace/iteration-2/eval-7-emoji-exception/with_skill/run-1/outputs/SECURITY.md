---
blueprint_kind: security
blueprint_status: draft
owner: security-lead
last_reviewed: 2026-09-10
---

# 安全与隐私

## 风险画像与范围

- 用户与暴露：面向青少年的公网社区应用；存在个人资料、位置语境、照片和用户生成内容。
- 敏感能力：组织者发布、完成证据、举报与审核；陌生人互动不在 MVP。
- 待核实制度：目标地区、具体年龄范围、监护人同意、数据主体权利、儿童安全和可访问性义务。
- 安全 owner：security lead；青少年安全 owner：trust and safety lead。

## 数据清单

| 数据 | Classification | Purpose/source | Access | Region | Retention/deletion | State |
|---|---|---|---|---|---|---|
| 账号最小资料与年龄段 | personal | 账号、适龄和权限 | 用户本人及必要管理员 | pending | 账户删除和法定保留待定 | provisional |
| 报名与参加状态 | personal | 提供行动流程 | 本人、对应组织者 | pending | 行动结束后最小化保留，期限待定 | provisional |
| 完成说明和可选照片 | personal/potentially sensitive | 核验完成情况 | 本人、对应组织者、必要审核员 | pending | 审核完成后分级保留，期限待定 | provisional |
| 举报与审核记录 | confidential | 安全处置和审计 | 授权审核员 | pending | 由政策与适用规则确定 | pending |
| 日志与设备安全信号 | internal/personal | 防滥用和排障 | 最小化授权人员 | pending | 短期保留，精确期限待定 | provisional |

不得要求公开精确家庭住址、学校班级、电话号码或完整行动轨迹。照片上传前提示检查人脸、校服、门牌和定位元数据；服务端去除不需要的 EXIF。

## 信任边界与威胁

| Boundary/flow | Threat or abuse case | Control | Verification | Owner |
|---|---|---|---|---|
| 浏览器到 API | 账号接管、枚举、越权 | 安全会话、速率限制、对象级授权、通用错误 | 自动化授权与会话测试 | security lead |
| 参与者到组织者 | 精确位置/身份过度暴露 | 最小字段、社区范围替代精确地址、按行动授权 | 数据流评审 | privacy lead |
| 文件到存储 | 恶意文件、不当内容、元数据泄漏 | 类型/大小验证、隔离扫描、EXIF 清理、受控 URL | 上传滥用测试 | backend lead |
| 审核工具 | 内部滥用或错误处置 | 最小权限、强认证、审计、双人复核高风险动作 | 权限评审与审计抽查 | safety lead |
| 通知提供方 | 消息泄露敏感内容 | 最少内容、站内详情、供应商审查 | 模板测试与供应商清单 | privacy lead |

## 身份与访问

| Actor | Authentication | Authorization/tenant boundary | Session/credential policy | Audit |
|---|---|---|---|---|
| 青少年参与者 | 方式由 TBD-ARCH-002 确认 | 仅本人资料、报名与记录 | 安全 cookie/平台凭据；恢复流程不泄露身份 | 登录、安全设置、敏感读取 |
| 组织者 | 强认证，候选含 passkey/MFA | 仅所属组织与行动 | 提权操作重认证 | 发布、核验、导出和权限变更 |
| 审核员 | 强认证/MFA | 单独安全角色和最小队列权限 | 短会话、受控设备策略待定 | 所有查看与处置 |

## 应用与供应链控制

- 输入/上传：服务端 schema 验证，富文本按允许列表处理；文件先隔离后可见；输出编码。
- 防滥用：报名、提交、举报和认证端点分别限速；不把自动规则当作未成年人高风险内容的唯一裁决。
- Secrets：只存于托管密钥系统；禁止进入仓库、前端包和日志；访问、轮换与 break-glass 有审计。
- Dependencies：锁文件、来源审查、自动漏洞扫描、支持版本策略和修复 owner。
- Verification：威胁建模、代码评审、SAST/依赖/secret 扫描、对象级授权集成测试，以及上线前青少年安全评审。

## 隐私与地区待核实项

| 问题 | Official source/date | Engineering response | Owner | State |
|---|---|---|---|---|
| 具体年龄、监护人同意与验证 | 目标地区确认后查询主管机关 | 年龄段数据最小化；在结论前不实现暗模式同意 | privacy/legal lead | pending |
| 地区、数据驻留与处理者 | 目标地区确认后查询官方来源 | 保持数据拓扑可配置，记录处理者 | privacy lead | pending |
| 保留、删除与导出 | 目标地区确认后查询官方来源 | 为用户、证据与审核数据定义分类生命周期 | product/privacy leads | pending |

## 检测与事件响应

- 证据：认证、权限拒绝、组织者操作、文件隔离、举报和审核处置形成可关联审计事件，日志不得记录敏感正文。
- 升级：账号接管、未成年人现实安全风险、敏感数据暴露和审核滥用分别定义严重度与联系人。
- 通信：由 incident commander 协调；涉及法定义务时由隐私/法律 owner 核实，蓝图不代替法律判断。
- 复盘：保留时间线、影响范围、修复与验证证据，必要时更新 PRD/SPEC。

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 完成适用地区、年龄/同意、数据保留与事件义务评审 | privacy/legal lead | 试点招募前 | production-ready | pending |
