---
blueprint_kind: domain-spec
blueprint_status: draft
owner: product-owner
last_reviewed: 2026-09-10
domain: checkin
source_prd: PRD-CHECKIN-001
---

# 打卡行为规格

## SPEC-CHECKIN-001 — 提交唯一日打卡

- Source: PRD-CHECKIN-001
- State: confirmed（能力）；唯一/不可补签 provisional
- Actors: 已登录会员
- Preconditions: 当前联网；会员确认本地时区。
- Requirement: 会员可为当前训练日提交一条有效打卡；相同幂等键或并发重复提交只产生一条记录，无计划日也可标记自主训练。
- Acceptance method: 幂等、并发、跨时区和无计划日 API/端到端验收。

### Scenario: 正常打卡

- **GIVEN** 当日尚无有效打卡
- **WHEN** 会员提交完成状态和可选感受
- **THEN** 系统返回唯一记录、训练日和确认时间，并立即在历史中可见

### Scenario: 重复提交

- **GIVEN** 首次提交已成功但客户端未收到响应
- **WHEN** 客户端使用相同幂等键重试
- **THEN** 返回原记录，不增加连续天数或第二条打卡

### Scenario: 当日已有打卡

- **GIVEN** 当日已有有效打卡
- **WHEN** 使用新幂等键再次提交
- **THEN** 系统返回已有记录并引导编辑，不创建重复记录

## SPEC-CHECKIN-002 — 查看与编辑历史

- Source: PRD-CHECKIN-001
- State: provisional；MVP 允许 24 小时内编辑文字/照片，不允许改训练日
- Actors: 已登录会员、获授权教练
- Preconditions: 存在打卡记录。
- Requirement: 会员可按日查看自己的记录，并在提交后 24 小时内编辑感受/附件；教练只读查看授权会员历史。
- Acceptance method: 权限、编辑窗口、分页和空态自动化/手工验收。

### Scenario: 窗口内编辑

- **GIVEN** 打卡提交不足 24 小时
- **WHEN** 会员修改感受
- **THEN** 更新后内容可见并保留修改时间，不改变训练日和首次确认时间

### Scenario: 超过窗口

- **GIVEN** 打卡已超过 24 小时
- **WHEN** 会员尝试修改
- **THEN** 系统拒绝修改并清楚说明记录已锁定

### Scenario: 越权查看

- **GIVEN** 教练未被分配该会员
- **WHEN** 请求其打卡历史
- **THEN** 系统返回通用无权/不存在结果，不显示任何记录或会员信息

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| `(member, local_date)` 最多一条有效记录 | 连续统计不重复 | provisional |
| 时区变化不回写历史训练日 | 历史稳定 | provisional |

## 待决定事项

无；补签和编辑窗口以 Beta 数据作为重评输入。

