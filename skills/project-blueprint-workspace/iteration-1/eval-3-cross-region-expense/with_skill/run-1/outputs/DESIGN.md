---
blueprint_kind: design
blueprint_status: draft
owner: TBD-DESIGN-001
last_reviewed: 2026-09-10
---

# 产品设计约束

## 体验原则

| 原则 | 用户后果 | 禁忌 | State |
|---|---|---|---|
| 状态先于装饰 | 每个费用、审批、支付都显示当前状态与下一步 | 只用颜色或模糊“处理中”掩盖差异 | provisional |
| 高风险操作可复核 | 支付、拒绝、预算发布前显示对象、金额和影响 | 一键不可逆且无确认 |
| 租户与身份清晰 | 页头/账户区持续显示企业，上下文切换需确认 | 仅凭相同邮箱混合租户 |
| 移动优先采集，Web 优先管理 | 拍摄和补录在移动端短路径；批量管理在 Web 高信息密度 | 强求三端像素一致 |

## 信息架构与旅程

| Area/screen | User goal | Entry/exit | Related SPEC | State |
|---|---|---|---|---|
| 企业登录与权限 | 进入正确企业并理解无权限原因 | 租户入口 → SSO → 角色首页 | SPEC-IDENTITY-001, SPEC-IDENTITY-002 | provisional |
| 员工提交费用 | 上传、补齐、校验、确认提交 | 新建 → 草稿 → 预览 → 提交结果 | SPEC-EXPENSE-001, SPEC-EXPENSE-002 | provisional |
| 经理审批 | 查看证据、预算影响并作出决定 | 待办 → 详情 → 确认 → 新状态 | SPEC-APPROVAL-001 | provisional |
| 预算配置 | 编辑、检查冲突、发布版本 | 预算列表 → 编辑 → 预览 → 发布 | SPEC-BUDGET-001 | provisional |
| 支付状态 | 区分待确认、处理中、成功、失败、复核 | 费用详情/支付队列 → 状态与历史 | SPEC-PAYMENT-001, SPEC-PAYMENT-002 | provisional |
| 审计检索 | 按时间/对象/操作者查证并导出 | 管理后台 → 筛选 → 导出 | SPEC-AUDIT-001 | provisional |
| 区域透明度 | 管理员确认租户数据区域 | 企业设置 → 数据区域（只读） | SPEC-REGION-001 | provisional |

## 关键流程

### 员工提交费用

移动端默认“拍摄/选择文件 → 上传与扫描 → 补字段 → 复核 → 提交”；Web 支持拖放与键盘录入。提交确认展示金额、币种、日期和附件数。

### 经理审批

详情页将发票预览、关键字段、预算影响和审批历史放在同一任务上下文；批准、退回、拒绝语义与理由规则不同，不用通用确认框替代。

### 预算配置

编辑态与已发布态明显分离；发布前展示适用组织、期间、类别、金额、冲突和生效时间。

### 支付状态

明确区分“未发起、待确认、处理中、成功、失败、人工复核”，并给出最后更新时间和下一步，不将供应商接单显示为到账。

### 审计检索

默认最小字段；敏感导出二次确认并说明审计记录与文件过期时间。

### 区域透明度

租户区域为管理员只读属性；任何迁移请求进入人工支持和审批流程，不能在界面即时切换。

## 视觉方向

- Direction: 暂定为克制、任务导向的企业工具；桌面端中等密度，移动端单列与大触控区。
- References: 无品牌或参考产品输入，暂不制造品牌语言。
- Explicitly avoid: 用国旗表达数据区域、仅颜色区分状态、伪造银行/支付成功感、装饰性仪表盘。
- Typography roles: 系统无衬线；数字金额使用等宽数字特性；至少区分页面标题、字段标签、正文、辅助说明。
- Color semantics: 中性色承载结构；成功/警告/失败必须同时有图标与文字。
- Spacing/grid/radius/elevation: 4px 基础间距；Web 12 栏内容网格，移动单列；层级主要靠边界与间距而非重阴影。
- Motion and imagery: 动效仅解释状态变化并尊重减少动态效果设置；发票预览不是装饰图。

## 设计 token 与组件

| Topic | Source/decision | Override policy | State |
|---|---|---|---|
| 颜色/文字/间距/圆角 | 语义 token，不直接在业务页面写原始值 | 例外需设计系统评审 | provisional |
| 表单、表格、对话框、通知 | 共享组件覆盖 Web；移动遵循平台交互惯例 | 高风险流程不得私自改确认语义 | provisional |
| 发票预览、金额、状态时间线 | 产品专用组合组件 | 需覆盖缩放、无障碍和脱敏 | provisional |

## 响应式与平台行为

| Context | Layout/input/safe-area behavior | Related SPEC | State |
|---|---|---|---|
| Web ≥1024px | 双栏详情、键盘可操作表格与批量入口 | SPEC-APPROVAL-001, SPEC-BUDGET-001 | provisional |
| Web 600–1023px | 单主栏，次要信息折叠，不隐藏关键状态 | SPEC-EXPENSE-001 | provisional |
| iOS/Android | 遵循安全区、原生返回、相机/文件权限与 ≥44×44pt 等效触控目标 | SPEC-EXPENSE-002 | provisional |
| 文本放大/长语言 | 不截断金额、状态、操作；允许控件换行和页面增长 | 全部 | provisional |

## UI 状态矩阵

| Flow/screen | Loading | Empty | Error | Offline | Permission | Destructive action |
|---|---|---|---|---|---|---|
| 费用草稿 | 字段骨架+上传进度 | 新建引导 | 保留输入、字段级错误 | 明示本地草稿/未提交 | 禁止进入并给支持路径 | 删除草稿确认 |
| 审批待办 | 列表骨架 | 明示无待办 | 可重试且不丢筛选 | 只读缓存须标旧 | 不泄露对象 | 拒绝/退回确认 |
| 预算 | 版本骨架 | 新建预算入口 | 显示冲突范围 | 禁止发布 | 只读或拒绝 | 发布/弃改确认 |
| 支付 | 状态骨架 | 无可支付费用 | 待确认/复核而非笼统失败 | 禁止新发起 | 隐藏操作并解释 | 发起支付二次确认 |
| 审计 | 查询进度 | 明示无结果 | 保留筛选 | 不提供旧缓存导出 | 通用拒绝 | 敏感导出确认 |

## 无障碍与内容

- Accessibility target: Web 以 WCAG 2.2 AA 作为设计与测试清单目标，不表示已认证；移动端同时遵循平台无障碍语义。
- Keyboard/focus/touch targets: 全流程键盘可达、焦点可见、对话框焦点管理；移动触控目标使用平台推荐尺寸。
- Contrast and non-color cues: 状态不只依赖颜色；错误与图表提供文本。
- Screen reader/semantic behavior: 上传进度、验证错误、状态变化可被播报；发票图像提供文件名和替代描述路径。
- Localization and text expansion: 简体中文、英语为暂定首发语言；日期、数字、货币按 locale 格式化但不改变存储金额；至少预留 30% 文本扩展。
- Content voice: 直接说明发生了什么、是否已保存、下一步和责任方；避免“应该没问题”等不确定表述。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DESIGN-001 | 确认品牌、设计负责人、首发语言、移动最低 OS 与组件库 | 产品/设计负责人 | UI 实现前 | implementation-ready | pending |

