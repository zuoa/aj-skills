---
blueprint_kind: domain-spec
blueprint_status: draft
owner: coach-lead
last_reviewed: 2026-09-10
domain: coach
source_prd: PRD-COACH-001
---

# 教练工作台行为规格

## SPEC-COACH-001 — 教练访问边界

- Source: PRD-COACH-001
- State: confirmed
- Actors: 教练、运营管理员
- Preconditions: 教练账号由运营管理员邀请并启用。
- Requirement: 教练仅能查看当前分配给自己的会员及其计划、打卡和照片；角色/分配变化最迟 5 分钟内生效，敏感读取与写入均审计。
- Acceptance method: 角色/对象级授权矩阵自动化测试与审计抽查。

### Scenario: 授权访问

- **GIVEN** 会员当前分配给该教练
- **WHEN** 教练打开会员详情
- **THEN** 显示该会员计划与允许范围内的打卡/照片，并记录敏感读取审计

### Scenario: 越权访问

- **GIVEN** 会员不属于该教练
- **WHEN** 教练通过修改 URL 或请求参数访问
- **THEN** 返回通用无权/不存在结果，不泄露会员姓名、手机号、记录或照片

## SPEC-COACH-002 — 筛选与查看进度

- Source: PRD-COACH-001
- State: confirmed；默认筛选 provisional
- Actors: 教练
- Preconditions: 至少分配一名会员。
- Requirement: 工作台可按姓名/脱敏手机号搜索，并按“今日未完成、连续缺卡、全部”筛选；详情展示计划版本和按日历史。
- Acceptance method: 2 万 DAU 对应教练样本数据的性能、分页、空态和权限验收。

### Scenario: 查找未完成会员

- **GIVEN** 教练有多名会员且部分今日未打卡
- **WHEN** 选择“今日未完成”
- **THEN** 仅显示当前授权且未完成者，结果带数据更新时间

### Scenario: 无结果

- **GIVEN** 筛选条件没有匹配会员
- **WHEN** 查询完成
- **THEN** 显示可清除筛选的空态，不展示其他教练的数据

## SPEC-COACH-003 — 发布计划版本

- Source: PRD-COACH-001
- State: confirmed；单教练归属 provisional
- Actors: 教练
- Preconditions: 教练获授权管理该会员。
- Requirement: 教练可创建草稿、预览并发布未来生效的计划版本；发布需显式确认；并发冲突不得静默覆盖。
- Acceptance method: 草稿、发布、版本冲突、权限和审计端到端验收。

### Scenario: 成功发布

- **GIVEN** 有完整计划草稿和未来生效日期
- **WHEN** 教练确认发布
- **THEN** 系统生成不可原地修改的版本，会员在生效日看到它，操作进入审计日志

### Scenario: 草稿不完整

- **GIVEN** 训练日缺动作剂量
- **WHEN** 教练尝试发布
- **THEN** 系统定位缺失字段并保持草稿，不产生会员可见版本

### Scenario: 并发冲突

- **GIVEN** 基础版本已被另一会话更新
- **WHEN** 教练发布旧草稿
- **THEN** 系统拒绝覆盖并要求比较新版本后重试

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 默认拒绝跨会员访问 | 枚举 ID 不获得数据 | confirmed |
| 发布是显式动作 | 自动保存草稿不会影响会员 | confirmed |

## 待决定事项

无；协作教练需求触发 PRD/SPEC 变更。

