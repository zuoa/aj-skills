---
blueprint_kind: prd
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
---

# 青少年社区环保行动应用 PRD

## 文档状态

| Item | Value |
|---|---|
| Working title | 社区绿行动 |
| Status | provisional |
| Product owner | product lead |
| Target release | pending |

## 问题与用户

青少年参与者需要找到可信的社区环保行动、报名参与，并在完成线下行动后提交记录。社区组织者需要发布行动、核验完成情况和处理举报。当前未给出目标地区、具体年龄范围、团队、预算和发布时间，这些信息不得推测为已确认事实。

## 目标与成功指标

| Goal | Measure | Target | Evidence owner | State |
|---|---|---|---|---|
| 完成行动闭环 | 从浏览到提交成功的任务完成情况 | 试点目标待定 | product/QA | pending |
| 辅助技术可用 | 屏幕阅读器、键盘和触控任务测试 | 核心任务无阻断 | accessibility/QA | confirmed |
| 社区安全 | 举报、权限与处置场景通过评审 | 政策批准后确定 | safety lead | pending |

## MVP 与非目标

### MVP

- 行动列表与详情，包括时间、地点范围、组织者、安全要求和名额。
- 报名、取消报名、我的行动。
- 线下行动完成记录及组织者核验。
- 举报、审核与必要的审计记录。
- 状态文字、屏幕阅读器、键盘和触控支持。

### 非目标

- 公开排行榜、陌生人私信、支付、广告和自动化内容裁决。
- 法定志愿时长或碳减排核证。

## 核心流程

| Journey | Actor | Trigger | Successful outcome | Failure/exception |
|---|---|---|---|---|
| 报名行动 | 青少年 | 查看行动详情 | 显示“已报名”文字状态 | 满员或资格不足时给出原因 |
| 提交完成记录 | 青少年 | 完成线下行动 | 保存一条记录并显示明确成功消息 | 网络失败保留输入且不宣称成功 |
| 核验 | 组织者 | 查看待核验记录 | 状态改为“已通过”或“需补充” | 无权限时拒绝且不泄露内容 |
| 举报 | 登录用户 | 发现不当行动或内容 | 确认收到并进入审核 | 限速且保护举报人身份 |

## 产品需求

### PRD-ACTION-001 — 浏览与报名行动

- User value: 找到适合自己的线下环保行动并理解参加要求。
- Requirement: 用户可以查看、报名和取消报名，系统以文字显示结果。
- Product acceptance: 正常、满员、取消和重复激活场景可验证。
- State: confirmed
- Source/owner: 用户简述 / product lead

### PRD-ACTION-002 — 完成记录与核验

- User value: 记录完成结果并理解组织者核验状态。
- Requirement: 参与者提交说明和允许的证据；组织者通过或要求补充。
- Product acceptance: 成功、失败、重复提交、待核验和需补充均有文字结果。
- State: confirmed
- Source/owner: 用户简述 / product lead

### PRD-ACCESS-001 — 无障碍核心流程

- User value: 屏幕阅读器及不同输入方式的用户可独立完成任务。
- Requirement: 状态不能只由图形或颜色表达；核心流程支持屏幕阅读器、键盘和触控。
- Product acceptance: 辅助技术和输入方式人工测试通过。
- State: confirmed
- Source/owner: 用户明确要求 / accessibility lead

### PRD-SAFETY-001 — 青少年社区保护

- User value: 降低不当接触、内容和位置暴露风险。
- Requirement: 最小公开资料，限制组织者权限，提供举报和审核。
- Product acceptance: 对象级授权、举报和审计场景通过。
- State: provisional
- Source/owner: 青少年场景推导，需 safety lead 批准

## 产品约束

| Topic | Constraint | State | Source | Revisit trigger |
|---|---|---|---|---|
| 品牌 | 仅线下行动完成成功消息允许一个树叶 Emoji | confirmed | 现有品牌规范 | 品牌规范变更 |
| 无障碍 | 屏幕阅读器支持；状态不只靠图形或颜色 | confirmed | 用户要求 | 支持平台改变 |
| 平台 | 响应式 Web/PWA 为工作假设 | provisional | 最小客户端假设 | 分发需求确认 |
| 地区/年龄 | 具体范围与同意机制未知 | pending | 缺少输入 | 试点招募前 |

## 风险与假设

| ID | Type | Statement | Impact | Validation |
|---|---|---|---|---|
| RISK-001 | risk | 照片可能暴露面孔、校服或定位信息 | 隐私和现实安全 | 上传流程测试与安全评审 |
| ASSUMPTION-001 | assumption | 一个团队交付首版 | 影响架构与部署复杂度 | 团队确认 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-PRODUCT-001 | 确认目标地区、年龄范围与监护人要求 | product/privacy lead | 试点前 | production-ready | pending |
| TBD-PRODUCT-002 | 确认客户端范围和成功指标 | product lead | 设计评审前 | implementation-ready | pending |
| TBD-PRODUCT-003 | 批准社区安全和审核政策 | safety lead | 内测前 | production-ready | pending |
