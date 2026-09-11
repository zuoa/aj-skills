---
blueprint_kind: prd
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 独立教练课程预约 SaaS 产品需求

## 状态与用户

本草案只确认两类用户和平台：独立教练使用网页管理端，学员使用手机网页预约。课程类型、收费方式、地区、团队、时间、预算和规模未提供，不推定为事实。

教练的核心任务是公布可预约时段并处理预约；学员的核心任务是找到合适时段、提交预约并看到明确结果。

## MVP 与非目标

MVP 暂定包含教练登录、课程/可用时段管理、公开预约页、预约创建与取消、教练预约列表。首版不包含在线支付、多教练机构、多场地资源优化、视频会议、原生 App、营销自动化或复杂报表；范围需产品负责人批准。

## 产品需求

### PRD-SCHEDULE-001 — 管理可预约时段

- Requirement: 教练可创建、修改和关闭课程时段，并看到保存结果。
- Acceptance: 已发布时段可在学员端查看；冲突或无效输入不被静默保存。
- State: provisional

### PRD-BOOKING-001 — 学员预约

- Requirement: 学员可选择仍可用的时段、提供必要联系信息并提交预约。
- Acceptance: 同一容量不得被超订，成功和冲突结果均明确。
- State: provisional

### PRD-BOOKING-002 — 取消与管理预约

- Requirement: 教练可查看预约；学员取消方式、权限与截止规则待定。
- Acceptance: 每次允许的状态变化都显示结果，非法变化被拒绝。
- State: provisional

### PRD-ACCESS-001 — 公开与管理边界

- Requirement: 学员只访问公开时段和自己的预约操作；管理功能要求教练身份。
- Acceptance: 未授权用户不能读取学员名单或执行管理操作。
- State: provisional

## 成功衡量与约束

不填转化率、可用性或节省时间等无基线数字。由验收负责人选择任务完成、冲突防止与运营结果的指标、基线和目标。

| Topic | State | Note |
|---|---|---|
| Clients | confirmed | 教练桌面/网页管理端；学员手机网页 |
| Market/language | pending | 影响日期、时区、币种、隐私 |
| Scale/budget/deadline | pending | 不据此引入复杂基础设施 |
| Team/owners | pending | 阻断实现与上线责任 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PRODUCT-001 | 确认 MVP、课程/容量/取消规则、市场、语言和验收负责人 | project-sponsor | 需求评审前 | implementation-ready | pending |
| TBD-METRIC-001 | 确认指标、基线与目标 | product-owner | 试点前 | production-ready | pending |
