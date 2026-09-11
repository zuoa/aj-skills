---
blueprint_kind: domain-spec
blueprint_status: draft
owner: mobile-lead
last_reviewed: 2026-09-10
domain: reminder
source_prd: PRD-REMINDER-001
---

# 提醒行为规格

## SPEC-REMINDER-001 — 配置提醒

- Source: PRD-REMINDER-001
- State: confirmed；默认时间 provisional
- Actors: 已登录会员
- Preconditions: 用户进入提醒设置；系统尚未因此自动申请通知权限。
- Requirement: 用户主动开启后才请求系统通知权限；可选择本地时间和星期，默认 20:00 每日但不自动启用；关闭后不再创建新的训练推送。
- Acceptance method: iOS/Android 真机权限、时区和设置契约验收。

### Scenario: 首次开启

- **GIVEN** 系统通知权限未决定
- **WHEN** 用户打开提醒开关
- **THEN** 先解释用途再触发系统权限；授权后保存时间/星期并显示已启用

### Scenario: 拒绝权限

- **GIVEN** 用户拒绝系统权限
- **WHEN** 返回设置页
- **THEN** 状态显示“系统通知已关闭”，训练和打卡仍可用，并提供设置指引

### Scenario: 关闭提醒

- **GIVEN** 提醒已开启
- **WHEN** 用户关闭
- **THEN** 设置立即显示关闭，之后不再排入新的训练推送任务

## SPEC-REMINDER-002 — 尽力投递与去重

- Source: PRD-REMINDER-001
- State: provisional；Beta 按到达率重评渠道
- Actors: 已开启提醒的会员
- Preconditions: 当天符合所选星期，且未在发送前完成打卡。
- Requirement: 系统在用户本地设定时间附近尝试一次提醒；同用户同训练日最多一次；投递失败不得修改打卡状态，可在 App 内显示非侵入式今日任务提示。
- Acceptance method: 调度时区、幂等、渠道回执、失效 token 和降级演练。

### Scenario: 正常投递

- **GIVEN** 用户已授权、当天未打卡且设备 token 有效
- **WHEN** 到达设定本地时间
- **THEN** 系统至多提交一次推送，点击后深链到“今日”

### Scenario: 已完成

- **GIVEN** 用户在提醒时间前已打卡
- **WHEN** 调度器处理当天任务
- **THEN** 不发送训练提醒，审计结果记为已跳过

### Scenario: 渠道失败

- **GIVEN** 推送渠道超时或 token 失效
- **WHEN** 投递失败
- **THEN** 不向用户显示虚假“已送达”；下次打开 App 可见今日任务，失效 token 被标记待刷新

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 提醒不代表完成 | 任何回执均不改打卡 | confirmed |
| 每训练日至多一条 | 重试不会导致重复骚扰 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-REMINDER-001 | 真实设备 PoC 后选择 Android 聚合/OEM 推送方案并完成 SDK 隐私审查 | mobile-lead | M2 末 | production-ready | pending |

