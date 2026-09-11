---
blueprint_kind: domain-spec
blueprint_status: draft
owner: privacy-owner
last_reviewed: 2026-09-10
domain: privacy
source_prd: PRD-PRIVACY-001
---

# 隐私与用户权利行为规格

## SPEC-PRIVACY-001 — 告知、选择与权限

- Source: PRD-PRIVACY-001
- State: provisional；须由合规负责人确认
- Actors: 访客、会员
- Preconditions: 功能将首次处理手机号、照片、设备 token 或调用系统权限。
- Requirement: 收集前以简明分层方式说明目的、类型、期限、接收方和权利入口；相机/相册/通知仅在用户选择相关功能时申请；拒绝非必要处理不阻断其他功能。
- Acceptance method: 首次使用路径、拒绝/撤回、权限调用静态与动态扫描、隐私文本人工验收。

### Scenario: 先告知后收集

- **GIVEN** 新用户尚未提交手机号
- **WHEN** 进入登录
- **THEN** 在发送验证码前可访问隐私摘要和全文，并记录适用版本；不同意时可返回体验训练

### Scenario: 拒绝照片权限

- **GIVEN** 用户拒绝相机和相册权限
- **WHEN** 进行打卡
- **THEN** 仍可提交无照片打卡，产品不重复强迫授权

### Scenario: 撤回通知

- **GIVEN** 用户曾授权提醒
- **WHEN** 在产品内关闭提醒
- **THEN** 后续不排入新推送，设置页说明系统层权限状态

## SPEC-PRIVACY-002 — 权利请求与账号注销

- Source: PRD-PRIVACY-001
- State: provisional；响应时限由合规评审冻结
- Actors: 已登录会员、客服/隐私负责人
- Preconditions: 用户从设置或公开客服入口发起请求。
- Requirement: 用户可发起访问副本、更正、删除、撤回和注销；系统提供受理编号。注销需再次验证控制权并说明影响，不要求新增超范围身份材料；完成后活动会话撤销，在线数据按保留表删除或匿名化。
- Acceptance method: 权利请求全链路演练、身份验证、删除证明和备份到期抽查。

### Scenario: 发起访问请求

- **GIVEN** 会员已验证当前会话
- **WHEN** 请求个人信息副本
- **THEN** 获得受理编号、范围与预计处理时间，结果通过安全下载或人工核验交付

### Scenario: 确认注销

- **GIVEN** 会员理解计划、打卡与照片将不可恢复
- **WHEN** 再次验证码确认注销
- **THEN** 账号立即不可登录，在线个人内容进入删除流程并可查询受理状态

### Scenario: 保留冲突

- **GIVEN** 某记录存在经确认的法定或安全保留依据
- **WHEN** 用户请求删除
- **THEN** 系统删除其余数据，并由隐私负责人说明暂缓删除的具体类别、依据和期限

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 拒绝非必要权限不阻断基本训练 | 用户仍可体验训练与无照片打卡 | provisional |
| 权利入口在 App 与 Web 均可达 | 不依赖单一商店或设备 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PRIVACY-001 | 冻结权利请求响应 SLA、删除例外与用户身份核验方式 | privacy-owner | M4 功能冻结前 | production-ready | pending |

