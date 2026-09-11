---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-SPEC-001
last_reviewed: 2026-09-10
domain: media-access
source_prd: PRD-MEDIA-001
---

# 照片、通知与教练权限规格

## SPEC-MEDIA-001 — 上传打卡照片
- Source: PRD-MEDIA-001
- State: provisional
- Actors: 学员
- Requirement: 系统只接受已确认类型/大小/数量的照片，并分别显示选择、上传、处理、成功和失败状态。
- Acceptance method: 自动化类型/大小/权限/恶意文件测试；iOS、Android、Web 真机上传验收。

### Scenario: 合法照片
- **GIVEN** 用户授权访问照片并选择符合规则的文件
- **WHEN** 用户提交打卡
- **THEN** 系统显示上传/处理进度，完成后只向授权主体展示照片

### Scenario: 权限拒绝或上传失败
- **GIVEN** 用户拒绝照片权限、文件不合规或网络中断
- **WHEN** 用户尝试附加照片
- **THEN** 系统保留可恢复的打卡内容，解释重新授权/选图/重试方式，不假称上传成功

## SPEC-NOTIFY-001 — 推送提醒
- Source: PRD-NOTIFY-001
- State: provisional
- Actors: 学员
- Requirement: 系统只在用户授权与偏好允许时发送提醒；推送失败不改变训练或打卡状态。
- Acceptance method: 自动化偏好/时区/幂等测试；iOS/Android 推送沙箱与拒权真机验收。

### Scenario: 授权提醒
- **GIVEN** 用户已授权推送并启用某提醒
- **WHEN** 该用户时区中的触发条件成立
- **THEN** 系统尝试一次可追踪发送，点击进入相关训练上下文

### Scenario: 拒权或供应商失败
- **GIVEN** 用户拒绝权限或推送供应商不可用
- **WHEN** 提醒到期
- **THEN** 产品不重复弹权限，不改变业务事实，并显示可选的设置/降级路径

## SPEC-COACH-001 — 教练访问学员
- Source: PRD-COACH-001
- State: provisional
- Actors: 教练
- Requirement: 教练仅可访问已授权学员，敏感查看和计划变更形成审计事件。
- Acceptance method: 自动化关系、对象级权限、直接 URL 与审计测试。

### Scenario: 授权关系
- **GIVEN** 教练与学员存在有效关系
- **WHEN** 教练查看进展或修改计划
- **THEN** 系统只显示允许字段并记录关键变更

### Scenario: 越权访问
- **GIVEN** 关系不存在、过期或属于另一教练
- **WHEN** 请求学员资料
- **THEN** 系统拒绝且不通过错误信息泄露资料存在性

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-MEDIA-001 | 确认照片限制/处理/保留、推送渠道/偏好和教练关系授权 | product/security owner | 集成前 | implementation-ready | pending |
