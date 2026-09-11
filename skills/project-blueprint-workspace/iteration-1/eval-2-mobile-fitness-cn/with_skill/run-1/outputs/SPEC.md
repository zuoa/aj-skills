---
blueprint_kind: spec-index
blueprint_status: draft
owner: product-owner
last_reviewed: 2026-09-10
---

# 系统行为规格

## 范围与权威

本索引管理全局可观察规则、领域索引、追踪和就绪度；具体行为只在 `specs/` 中定义。冲突时先更新 PRD/SPEC，再更新设计、架构与测试。

## 术语

| 术语 | 含义 | 来源 |
|---|---|---|
| 会员 | 使用训练、打卡、照片和提醒功能的个人用户 | PRD.md |
| 教练 | 经运营授予角色，并被分配会员的工作人员 | PRD-COACH-001 |
| 体验训练 | 未登录也可查看且不保存个人进度的一套训练 | PRD.md MVP |
| 训练日 | 计划中按会员 IANA 时区确定的本地自然日 | PRD-CHECKIN-001 |
| 有效打卡 | 某训练日唯一、未删除的完成记录 | PRD-CHECKIN-001 |
| 计划版本 | 发布后不可静默改写的训练计划快照 | PRD-PLAN-001 |
| 私密照片 | 仅会员本人和当前获授权教练可访问的打卡附件 | PRD-MEDIA-001 |

## 全局行为规则

| Rule ID | 可观察规则 | Source | State |
|---|---|---|---|
| GLOBAL-001 | 所有用户可见时间按其已保存 IANA 时区显示；未设置时首次使用设备时区并让用户确认 | PRD-CHECKIN-001 | provisional；跨时区缺陷 >1% 时重评 |
| GLOBAL-002 | 写请求超时后客户端可安全重试；同一幂等键不得产生重复业务结果 | PRD-CHECKIN-001 | provisional |
| GLOBAL-003 | 错误文案说明“发生什么、是否保存、下一步”，不得暴露堆栈、内部 ID、手机号存在性或对象地址 | PRD-IDENTITY-001; PRD-PRIVACY-001 | provisional |
| GLOBAL-004 | 权限拒绝只影响依赖该权限的功能；训练浏览和无照片打卡保持可用 | PRD-PRIVACY-001 | provisional |
| GLOBAL-005 | 客户端不得把本地缓存当作成功提交证据；仅服务端确认后展示“已打卡” | PRD-CHECKIN-001 | provisional |
| GLOBAL-006 | 服务端行为向前兼容至少两个已发布移动版本；低于最低版本时给出可理解的升级提示 | PRD-PLATFORM-001 | provisional；发布节奏变化时重评 |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Platform | [specs/platform.md](specs/platform.md) | mobile-lead | draft |
| Identity | [specs/identity.md](specs/identity.md) | backend-lead | draft |
| Plan | [specs/plan.md](specs/plan.md) | product-owner | draft |
| Check-in | [specs/checkin.md](specs/checkin.md) | product-owner | draft |
| Media | [specs/media.md](specs/media.md) | security-owner | draft |
| Reminder | [specs/reminder.md](specs/reminder.md) | mobile-lead | draft |
| Coach | [specs/coach.md](specs/coach.md) | coach-lead | draft |
| Privacy | [specs/privacy.md](specs/privacy.md) | privacy-owner | draft |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-PLATFORM-001 | SPEC-PLATFORM-001 | DESIGN.md#响应式与平台行为 | ARCHITECTURE.md#容器与可部署单元 | planned |
| PRD-PLATFORM-001 | SPEC-PLATFORM-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-IDENTITY-001 | SPEC-IDENTITY-001 | DESIGN.md#关键页面与旅程 | ARCHITECTURE.md#身份会话与授权 | planned |
| PRD-IDENTITY-001 | SPEC-IDENTITY-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#身份会话与授权 | planned |
| PRD-IDENTITY-001 | SPEC-IDENTITY-003 | DESIGN.md#ui-状态矩阵 | SECURITY.md#身份与访问 | planned |
| PRD-PLAN-001 | SPEC-PLAN-001 | DESIGN.md#关键页面与旅程 | ARCHITECTURE.md#模块边界 | planned |
| PRD-PLAN-001 | SPEC-PLAN-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-CHECKIN-001 | SPEC-CHECKIN-001 | DESIGN.md#关键页面与旅程 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-CHECKIN-001 | SPEC-CHECKIN-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-MEDIA-001 | SPEC-MEDIA-001 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#照片上传动态视图 | planned |
| PRD-MEDIA-001 | SPEC-MEDIA-002 | DESIGN.md#ui-状态矩阵 | SECURITY.md#信任边界与威胁 | planned |
| PRD-REMINDER-001 | SPEC-REMINDER-001 | DESIGN.md#关键页面与旅程 | ARCHITECTURE.md#提醒投递动态视图 | planned |
| PRD-REMINDER-001 | SPEC-REMINDER-002 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-COACH-001 | SPEC-COACH-001 | DESIGN.md#信息架构 | ARCHITECTURE.md#身份会话与授权 | planned |
| PRD-COACH-001 | SPEC-COACH-002 | DESIGN.md#关键页面与旅程 | ARCHITECTURE.md#模块边界 | planned |
| PRD-COACH-001 | SPEC-COACH-003 | DESIGN.md#ui-状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-PRIVACY-001 | SPEC-PRIVACY-001 | DESIGN.md#无障碍与内容 | SECURITY.md#隐私与区域义务 | planned |
| PRD-PRIVACY-001 | SPEC-PRIVACY-002 | DESIGN.md#关键页面与旅程 | SECURITY.md#数据清单 | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | PRD.md#核心旅程；PRD.md#mvp-与非目标；DESIGN.md |
| implementation-ready | ready | none | 本索引全部领域规格；DESIGN.md；ARCHITECTURE.md；ENGINEERING.md。provisional 默认可先实现，触发重评时先变更规格 |
| production-ready | blocked | TBD-PRODUCT-001, TBD-COMPLIANCE-001, TBD-PROVIDER-001, TBD-STORE-001, TBD-OPERATIONS-001 | SECURITY.md#待决定事项；DEPLOY.md#待决定事项；上架/备案、恢复演练与签约证据尚缺 |

## 规格变更规则

1. 行为变化先修改相应 `PRD-*` 与 `SPEC-*`，保留 ID；删除时标注 superseded。
2. provisional 项触发重评后，由 owner 记录测量证据，并升级为 confirmed、调整目标或登记新的待决定项。
3. 任何跨境服务、支付、公开内容、未成年人、医疗建议或可穿戴数据进入范围时，production-ready 自动回到 blocked 并重做隐私/安全评审。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 由产品验收负责人在 M1 末签署全部 provisional 行为默认，或提交差异变更 | product-owner | M1 末 | production-ready | pending |

