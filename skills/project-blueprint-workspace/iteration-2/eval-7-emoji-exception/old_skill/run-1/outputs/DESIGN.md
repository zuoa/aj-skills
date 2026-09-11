---
blueprint_kind: design
blueprint_status: draft
owner: design-lead
last_reviewed: 2026-09-10
---

# 产品设计约束

## 体验原则

| Principle | User consequence | Anti-pattern | State |
|---|---|---|---|
| 状态明确 | 不看颜色和图形也知道报名、提交或核验结果 | 仅以绿色、勾号或动画表示成功 | confirmed |
| 操作可恢复 | 网络或校验失败后不丢失输入 | 错误时清空表单 | confirmed |
| 安全优先 | 青少年资料和精确位置最小公开 | 陌生人私信、公开排名 | provisional |
| 语言直接 | 按钮和错误说明具体动作与下一步 | 只写“出错了” | confirmed |

## 信息架构与流程

| Area/screen | User goal | Entry/exit | Related SPEC | State |
|---|---|---|---|---|
| 行动列表/详情 | 找到合适行动并报名 | 首页到详情/我的行动 | SPEC-ACTION-001 | confirmed |
| 我的行动 | 查看报名、待参加、待核验 | 主导航到完成记录 | SPEC-ACTION-001; SPEC-ACTION-003 | confirmed |
| 完成记录 | 填写、保存并理解提交结果 | 已参加行动到我的行动 | SPEC-ACTION-002 | confirmed |
| 举报/审核 | 报告风险或处理记录 | 对象菜单/受控后台 | SPEC-SAFETY-001 | provisional |

## 视觉方向

- Direction: 社区公告式的信息层级，优先显示行动名称、日期、地点范围、主办方和安全说明；避免抽象科技感。
- References and what to borrow: 社区公告的直接标题与系统表单的熟悉行为；未提供视觉资产，具体品牌 token 待定。
- Explicitly avoid: 公开排行榜、无依据环境分数、以动画替代状态、过度装饰的卡片。
- Typography roles: 系统无衬线字体；标题、正文、辅助说明使用稳定字号和字重层级。
- Color semantics: 中性背景与品牌绿色；成功、警告和错误都有文字标签和语义图标。
- Spacing/grid/radius/elevation: 移动端单列、4/8 间距尺度；圆角和阴影只帮助区分可交互区域。
- Motion and imagery: 动效不阻断输入并支持减少动态效果；行动照片需授权和替代文本。

品牌例外：现有品牌规范允许且仅允许在完成线下行动、服务端确认记录保存成功后，于消息“行动已记录，感谢你的参与。”末尾显示一个 🍃。消息文字本身完整表达结果，屏幕阅读器只公告该文字，树叶不作为状态或可访问名称。标题、列表、按钮、导航、错误、加载、待核验及其他系统状态不使用 Emoji。

## Design tokens 与组件

| Topic | Source/decision | Override policy | State |
|---|---|---|---|
| 状态 | success/warning/error/info token 配文字和语义 | 页面不得只改颜色 | confirmed |
| 组件 | 选择经键盘和屏幕阅读器验证的组件库 | 自定义组件必须复用焦点和错误模式 | provisional |
| 排版/间距 | 系统字体和 4/8 尺度 | 200% 文本不截断 | provisional |

## 响应式与平台行为

| Context | Layout/input/safe-area behavior | Related SPEC | State |
|---|---|---|---|
| 手机 | 单列、触控目标留足间距、主操作不遮挡内容 | SPEC-ACTION-001; SPEC-ACTION-002 | provisional |
| 桌面 | 可并排列表/详情，DOM 与焦点顺序保持一致 | SPEC-ACCESS-002 | provisional |
| 键盘 | 跳过链接、可见焦点、弹层关闭后恢复焦点 | SPEC-ACCESS-002 | confirmed |

## 界面状态矩阵

| Flow/screen | Loading | Empty | Error | Offline | Permission | Destructive action |
|---|---|---|---|---|---|---|
| 行动列表 | “正在加载行动” | “暂无可报名行动” | 说明失败与重试 | 标示缓存时间 | 定位拒绝时可手动选择 | not-applicable |
| 报名 | “正在报名”并防重复 | not-applicable | 说明是否报名成功 | 不宣称成功 | 说明资格限制 | 取消报名需确认 |
| 完成记录 | “正在提交” | 说明证据要求 | 保留内容并给出重试 | 保存本地草稿并标明未提交 | 相机拒绝后给替代路径 | 删除草稿需确认 |
| 核验 | “正在读取记录” | “没有待核验记录” | 保留筛选与重试 | 禁止离线处置 | 无权时文字说明 | 拒绝需理由和确认 |

## 无障碍与内容

- Accessibility target: WCAG 2.2 AA（响应式 Web）。
- Keyboard/focus/touch targets: 核心流程仅键盘可完成，焦点顺序与阅读顺序一致；触控目标和间距按平台规范验证。
- Contrast and non-color cues: 文本、控件和焦点通过对比度检查；状态同时有文字和程序化语义，不只依赖颜色或图形。
- Screen reader/semantic behavior: 页面标题和区域语义明确；控件有名称、角色和值；异步成功和错误用礼貌级实时区域公告；装饰符号不进入可访问名称。
- Localization and text expansion: 支持 200% 文本缩放；日期时间按 locale 显示；语言范围待定。
- Content voice and terminology: 用“报名参加”“提交完成记录”“待核验”“已通过”“需补充”等稳定术语；错误说明发生了什么和下一步。
- 验收：VoiceOver/Safari、TalkBack/Chrome、仅键盘和触控核心任务测试；具体支持矩阵由 TBD-ACCESS-001 确认。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DESIGN-001 | 确认品牌色、字体、组件库和品牌文案本地化 | design/brand lead | 视觉定稿前 | implementation-ready | pending |
