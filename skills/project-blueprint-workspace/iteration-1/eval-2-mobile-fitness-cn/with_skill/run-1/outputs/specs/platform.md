---
blueprint_kind: domain-spec
blueprint_status: draft
owner: mobile-lead
last_reviewed: 2026-09-10
domain: platform
source_prd: PRD-PLATFORM-001
---

# 跨端行为规格

## SPEC-PLATFORM-001 — 跨端状态连续

- Source: PRD-PLATFORM-001
- State: confirmed（平台）；同步时序 provisional
- Actors: 已登录会员
- Preconditions: 同一手机号账号在两个受支持客户端登录。
- Requirement: 服务端确认的计划、打卡、照片元数据与提醒设置在 iOS、Android 和响应式 Web 上保持一致；刷新后不得回退到旧的成功状态。
- Acceptance method: 三端契约测试加真实设备手工验收，保存请求/响应和截图证据。

### Scenario: 成功跨端同步

- **GIVEN** 会员在 Android 成功提交当日打卡
- **WHEN** 其在 Web 刷新“历史”
- **THEN** Web 显示同一条打卡及服务端确认时间，不要求重复提交

### Scenario: 旧客户端写入冲突

- **GIVEN** 客户端缓存的计划版本已被教练更新
- **WHEN** 客户端基于旧版本提交关联操作
- **THEN** 系统保留合法打卡并提示计划已更新，不静默覆盖新计划

## SPEC-PLATFORM-002 — 弱网与最低版本

- Source: PRD-PLATFORM-001
- State: provisional；若核心用户离线率高或失败率 >3% 重评完整离线同步
- Actors: 会员
- Preconditions: 客户端曾成功加载数据或版本低于服务端最低兼容版本。
- Requirement: 断网时只读展示最近缓存并标注更新时间；写入可保存本地草稿但不显示为已成功；不兼容版本给出升级路径。
- Acceptance method: 网络整形、缓存过期和版本策略端到端验收。

### Scenario: 离线查看

- **GIVEN** 会员曾加载今日计划且当前断网
- **WHEN** 打开“今日”
- **THEN** 显示缓存计划、离线标记和最后更新时间

### Scenario: 离线打卡

- **GIVEN** 当前无网络
- **WHEN** 会员点击提交打卡
- **THEN** 系统保存可编辑草稿并明确“尚未提交”，恢复联网后由用户确认提交

### Scenario: 强制升级

- **GIVEN** 当前客户端低于安全最低版本
- **WHEN** 用户进入需登录功能
- **THEN** 系统阻止不兼容操作、说明原因并提供官方升级入口；体验训练仍可用时继续开放

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 仅服务端确认代表成功 | 客户端重启后不出现“假成功” | provisional |
| 缓存带版本和更新时间 | 用户能分辨数据是否可能过期 | provisional |

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PLATFORM-001 | 以 M2 真实设备数据冻结最低 OS/浏览器矩阵 | mobile-lead | M2 末 | production-ready | pending |

