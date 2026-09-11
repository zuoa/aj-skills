---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与权威关系

本文件只管理共享行为、术语、领域索引、追踪和就绪度。详细可观察行为位于 `specs/`；内部机制不在此定义。

## 术语

| 术语 | 含义 | 来源 |
|---|---|---|
| Tenant / 租户 | 具有独立成员、配置和数据边界的企业客户 | PRD-IDENTITY-001 |
| Expense / 费用 | 员工提交并参与审批与支付的业务记录 | PRD-EXPENSE-001 |
| Invoice / 发票 | 费用的文件证据，不代表平台已验证其税务真实性 | PRD-EXPENSE-001 |
| Data region / 数据区域 | 租户业务数据允许持久化处理的地理边界 | PRD-REGION-001 |
| Payment status / 支付状态 | 平台基于供应商回调或主动查询展示的付款生命周期 | PRD-PAYMENT-001 |

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | State |
|---|---|---|---|
| GLOBAL-001 | 用户只能看到当前租户内且其角色允许的数据；跨租户标识返回不泄露对象存在性的结果 | PRD-IDENTITY-001 | confirmed |
| GLOBAL-002 | 金额以货币最小单位与 ISO 货币代码展示和传输，不进行隐式跨币种换算 | PRD-EXPENSE-001 | provisional |
| GLOBAL-003 | 所有时间记录使用 UTC，界面按租户时区显示并明确日期边界 | PRD-AUDIT-001 | provisional |
| GLOBAL-004 | 会改变业务状态的重复请求不得产生重复提交、决定或支付 | PRD-EXPENSE-001; PRD-PAYMENT-001 | confirmed |
| GLOBAL-005 | 区域依赖不可用时，系统不得将欧盟租户请求自动路由到非欧盟数据面 | PRD-REGION-001 | confirmed |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Expense | [specs/expense.md](specs/expense.md) | 产品负责人 | draft |
| Approval & Budget | [specs/approval-budget.md](specs/approval-budget.md) | 产品负责人 | draft |
| Identity | [specs/identity.md](specs/identity.md) | 身份/安全负责人 | draft |
| Payment | [specs/payment.md](specs/payment.md) | 支付产品负责人 | draft |
| Region & Audit | [specs/region-audit.md](specs/region-audit.md) | 法务/安全负责人 | draft |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-EXPENSE-001 | SPEC-EXPENSE-001, SPEC-EXPENSE-002 | DESIGN.md#员工提交费用 | ARCHITECTURE.md#费用与文件流 | planned |
| PRD-APPROVAL-001 | SPEC-APPROVAL-001 | DESIGN.md#经理审批 | ARCHITECTURE.md#模块边界 | planned |
| PRD-BUDGET-001 | SPEC-BUDGET-001 | DESIGN.md#预算配置 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-IDENTITY-001 | SPEC-IDENTITY-001, SPEC-IDENTITY-002 | DESIGN.md#企业登录与权限 | ARCHITECTURE.md#身份与授权边界 | planned |
| PRD-PAYMENT-001 | SPEC-PAYMENT-001, SPEC-PAYMENT-002 | DESIGN.md#支付状态 | ARCHITECTURE.md#支付集成流 | planned |
| PRD-REGION-001 | SPEC-REGION-001 | DESIGN.md#区域透明度 | ARCHITECTURE.md#区域拓扑 | planned |
| PRD-AUDIT-001 | SPEC-AUDIT-001 | DESIGN.md#审计检索 | ARCHITECTURE.md#数据与一致性 | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PRODUCT-001 | PRD.md 已确认用户、任务、MVP 和平台；缺验收负责人 |
| implementation-ready | blocked | TBD-PRODUCT-002, TBD-MOBILE-001, TBD-DESIGN-001, TBD-ARCH-001, TBD-IDENTITY-001, TBD-PAYMENT-001, TBD-ENGINEERING-001 | 领域规格、DESIGN.md、ARCHITECTURE.md、ENGINEERING.md |
| production-ready | blocked | TBD-LEGAL-001, TBD-SECURITY-001, TBD-SECURITY-002, TBD-DEPLOY-001, TBD-DEPLOY-002, TBD-SLO-001, TBD-COST-001, TBD-METRIC-001 | SECURITY.md 与 DEPLOY.md；需法务/安全确认及恢复演练 |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 产品负责人逐条确认草案行为与异常处理 | 产品负责人 | 实现排期前 | implementation-ready | pending |

