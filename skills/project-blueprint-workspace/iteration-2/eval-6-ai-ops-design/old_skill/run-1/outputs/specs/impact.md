---
blueprint_kind: domain-spec
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
domain: impact
source_prd: PRD-IMPACT-001
---

# 影响范围领域行为规格

## SPEC-IMPACT-001 — 建立可追溯的影响视图

- Source: PRD-IMPACT-001
- State: provisional
- Actors: 值班工程师、事件指挥者
- Preconditions: 用户选择一个告警；至少存在告警本身的来源记录。
- Requirement: 系统必须按“已观察事实、确定性关系、AI 推断、人工确认、未知”展示相关服务、环境、部署、用户面与时间线；每一项包含来源、数据时间和可用的源系统入口。
- 验收方法：固定关系图和来源样本的自动化测试；人工核对每种证据类型、无障碍名称与深链。

### Scenario: 查看多来源影响证据

- **GIVEN** 告警与服务目录、部署记录及观测信号存在关联
- **WHEN** 用户打开影响范围
- **THEN** 系统按证据类型展示相关实体，能从每项定位来源，并明确哪些关系仍未确认

### Scenario: 关系数据缺失

- **GIVEN** 服务目录无对应关系或数据过期
- **WHEN** 系统构建影响视图
- **THEN** 缺失区域显示“未知”与缺失原因，不自动推断为“无影响”，并提供人工记录路径

## SPEC-IMPACT-002 — 人工确认与纠正影响判断

- Source: PRD-IMPACT-001
- State: provisional；允许修改的角色 pending（TBD-IDENTITY-001）
- Actors: 具备事件编辑权限的工程师
- Preconditions: 影响视图已加载；用户已认证。
- Requirement: 系统必须允许授权用户确认、排除或补充影响项，并记录操作者、时间、理由和原始建议；人工判断不得静默改写来源事实。
- 验收方法：权限与状态转移自动化测试；审计时间线人工检查。

### Scenario: 确认一个 AI 推断

- **GIVEN** AI 将某服务标记为“可能受影响”且提供证据
- **WHEN** 授权用户选择“确认受影响”并填写理由
- **THEN** 该项显示为“人工确认”，保留原推断与证据，审计时间线新增不可变事件

### Scenario: 无权限用户尝试纠正

- **GIVEN** 用户只有查看权限
- **WHEN** 用户尝试确认或排除影响项
- **THEN** 系统不改变状态，说明所需权限并记录被拒绝的敏感操作尝试

## 领域不变量

| 规则 | 可观察结果 | 状态 |
|---|---|---|
| 来源事实不可被 AI 或人工覆盖 | 原始事实保留，判断以新增事件表示 | provisional |
| 未知不是无影响 | 缺数据处明确显示未知 | provisional |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IDENTITY-001 | 确认谁可以确认、排除和补充影响 | 安全/事件管理负责人 | 权限模型冻结前 | implementation-ready | pending |
| TBD-INTEGRATION-001 | 确认可关联实体与记录源 | 平台负责人 | 架构评审前 | implementation-ready | pending |
