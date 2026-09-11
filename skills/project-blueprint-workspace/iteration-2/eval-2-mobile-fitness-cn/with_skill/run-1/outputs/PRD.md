---
blueprint_kind: prd
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 健身习惯产品需求

## 项目画像

| Item | Value | State |
|---|---|---|
| 市场 | 中国大陆公开上线 | confirmed |
| 用户端 | iOS、Android、响应式 Web | confirmed |
| 教练端 | Web | confirmed |
| 团队 | 3 人，Flutter；后端熟悉 TypeScript | confirmed |
| 工期 | 6 个月 | confirmed |
| 初期规模 | 约 2 万日活 | confirmed（用户估算） |
| 月基础设施预算 | 8000 元 | confirmed（用户约束） |

目标用户是执行个人训练计划的学员与为学员配置计划、查看进展的教练。产品负责人、年龄范围、商业模式、可用性目标和具体上线日期未提供。

## MVP 与非目标

MVP 包含手机号登录、训练计划、每日打卡、照片上传、提醒推送及教练 Web 管理。暂不包含支付、可穿戴设备、直播、社交动态、排行榜、AI 教练、营养诊断、多语言或复杂数据仓库。

## 产品需求

### PRD-AUTH-001 — 手机号登录
- Requirement: 用户通过手机号和一次性验证码建立会话；失败、频控和过期结果明确。
- State: provisional

### PRD-TRAIN-001 — 训练计划
- Requirement: 教练为授权学员维护计划，学员只查看自己的当前计划。
- State: provisional

### PRD-CHECKIN-001 — 每日打卡
- Requirement: 学员按业务日期提交、查看并在允许规则内修改打卡。
- State: provisional

### PRD-MEDIA-001 — 照片上传
- Requirement: 学员可为打卡上传受限照片并看到处理结果。
- State: provisional

### PRD-NOTIFY-001 — 提醒推送
- Requirement: 在用户授权且渠道可用时发送训练/打卡提醒；失败不改变计划或打卡事实。
- State: provisional

### PRD-COACH-001 — 教练权限
- Requirement: 教练只能访问已建立关系的学员及其允许数据，关键变更可审计。
- State: provisional

## 成功与约束

成功指标、留存基线、提醒效果和运营目标不得由“2 万日活”推导，登记待定。产品不提供医疗诊断或伤病治疗建议；健康免责声明和适用边界需产品/专业负责人确认。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PRODUCT-001 | 确认产品负责人、年龄范围、计划/打卡规则、教练关系、指标与上线日期 | sponsor | 需求评审前 | implementation-ready | pending |
| TBD-COMPLIANCE-001 | 由合适责任人核实大陆上线主体、备案、隐私、SDK、商店和健康内容要求 | legal/compliance owner | 供应商签约前 | production-ready | pending |
