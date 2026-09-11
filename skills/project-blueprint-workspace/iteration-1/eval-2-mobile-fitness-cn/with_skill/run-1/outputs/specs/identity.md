---
blueprint_kind: domain-spec
blueprint_status: draft
owner: backend-lead
last_reviewed: 2026-09-10
domain: identity
source_prd: PRD-IDENTITY-001
---

# 身份行为规格

## SPEC-IDENTITY-001 — 获取验证码

- Source: PRD-IDENTITY-001
- State: confirmed；频率 provisional
- Actors: 未登录会员
- Preconditions: 用户接受账号与隐私告知并输入中国大陆手机号。
- Requirement: 系统对格式合法号码发起验证码请求，统一返回不泄露注册状态的结果；同号码 60 秒内最多发送一次、24 小时最多 10 次，同设备/IP 另有限流。
- Acceptance method: API 契约、限流、号码枚举和短信沙箱自动化验收。

### Scenario: 正常请求

- **GIVEN** 合法手机号且未触发频率限制
- **WHEN** 用户请求验证码
- **THEN** 页面进入 60 秒倒计时并显示模糊化号码；服务端响应不说明号码是否已注册

### Scenario: 被限流

- **GIVEN** 同一主体在窗口内超过限制
- **WHEN** 再次请求验证码
- **THEN** 系统不发送短信，给出可重试时间且不改变已发送验证码状态

## SPEC-IDENTITY-002 — 验证与会话

- Source: PRD-IDENTITY-001
- State: confirmed；会话时长 provisional
- Actors: 未登录会员
- Preconditions: 已有未过期验证码挑战。
- Requirement: 正确验证码创建或进入唯一账号并建立会话；验证码 5 分钟过期、单次成功使用，连续 5 次错误后挑战失效。
- Acceptance method: 认证集成测试、重放测试、跨端会话手工验收。

### Scenario: 成功登录

- **GIVEN** 有效挑战和正确验证码
- **WHEN** 用户提交验证码
- **THEN** 系统建立会话并进入“今日”，验证码不可再次使用

### Scenario: 错误或过期

- **GIVEN** 验证码错误、已使用或过期
- **WHEN** 用户提交
- **THEN** 系统拒绝登录，返回统一错误并保留安全的重试/重新获取路径

## SPEC-IDENTITY-003 — 退出与撤销

- Source: PRD-IDENTITY-001
- State: provisional；若风控结果要求更短会话则重评
- Actors: 已登录会员或教练
- Preconditions: 存在一个或多个活动会话。
- Requirement: 单设备退出立即撤销当前刷新凭据；“退出所有设备”在 5 分钟内使既有会话不可继续访问受保护数据。
- Acceptance method: 多设备端到端测试与撤销延迟观测。

### Scenario: 单设备退出

- **GIVEN** 用户在两台设备已登录
- **WHEN** 在一台设备退出
- **THEN** 该设备无法刷新会话，另一台保持登录

### Scenario: 全部退出

- **GIVEN** 用户选择退出所有设备
- **WHEN** 任一旧会话再次请求受保护数据
- **THEN** 最迟 5 分钟内返回未认证并要求重新验证手机号

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 认证响应不泄露账号存在性 | 相同条件下新旧手机号得到同类文案和时序 | confirmed |
| 验证码不可记录到客户端日志/分析 | 支持导出日志中不出现验证码 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IDENTITY-001 | 确认短信模板签名、供应商实名资质和反滥用阈值 | backend-lead | M2 第 2 周 | production-ready | pending |

