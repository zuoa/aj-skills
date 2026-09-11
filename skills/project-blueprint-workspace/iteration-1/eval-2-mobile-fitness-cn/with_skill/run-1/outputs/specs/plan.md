---
blueprint_kind: domain-spec
blueprint_status: draft
owner: product-owner
last_reviewed: 2026-09-10
domain: plan
source_prd: PRD-PLAN-001
---

# 训练计划行为规格

## SPEC-PLAN-001 — 查看今日与计划

- Source: PRD-PLAN-001
- State: confirmed
- Actors: 会员；未登录访客仅能看体验训练
- Preconditions: 会员已登录，或访客进入体验入口。
- Requirement: 系统按用户本地训练日展示适用的已发布计划版本、动作顺序、训练量和教练说明；没有计划时展示真实空态。
- Acceptance method: 时区参数化契约测试、内容快照测试和可用性验收。

### Scenario: 有当日训练

- **GIVEN** 会员在其本地日期有已生效训练日
- **WHEN** 打开“今日”
- **THEN** 显示计划名称、动作顺序、组次/时长、注意事项与版本生效时间

### Scenario: 无计划

- **GIVEN** 当日没有适用计划
- **WHEN** 会员打开“今日”
- **THEN** 显示“今日未安排”及联系教练/查看历史入口，不创建默认打卡任务

### Scenario: 访客体验

- **GIVEN** 用户未登录
- **WHEN** 选择体验训练
- **THEN** 可查看完整体验内容，系统不保存个体进度且清楚说明登录后的价值

## SPEC-PLAN-002 — 版本生效与历史稳定

- Source: PRD-PLAN-001
- State: provisional；若业务要求当日紧急纠正则增加显式替换流程
- Actors: 会员、教练
- Preconditions: 教练已发布至少一个计划版本。
- Requirement: 新版本只影响其生效日起的训练；已发生训练日继续显示当时版本。被撤回的未来版本不得影响既有历史。
- Acceptance method: 版本边界、跨日和历史回归自动化验收。

### Scenario: 发布未来版本

- **GIVEN** 当前计划已产生历史记录
- **WHEN** 教练发布明日生效的新版本
- **THEN** 今日与历史保持旧版本，明日起显示新版本

### Scenario: 并发更新

- **GIVEN** 两个教练页面基于同一旧版本编辑
- **WHEN** 后提交者发布
- **THEN** 系统拒绝覆盖并展示“计划已更新”，要求重新加载比较

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 发布版本不可原地编辑 | 会员历史可复核 | provisional |
| 未发布草稿对会员不可见 | 会员只见明确生效内容 | confirmed |

## 待决定事项

无；内容库范围在 PRD 里按里程碑重评，不阻断实现。

