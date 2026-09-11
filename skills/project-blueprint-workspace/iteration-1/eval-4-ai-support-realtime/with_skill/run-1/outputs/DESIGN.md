---
blueprint_kind: design
blueprint_status: draft
owner: design-lead
last_reviewed: 2026-09-10
---

# 产品设计约束

## 体验原则

| 原则 | 用户后果 | 禁止模式 | State |
|---|---|---|---|
| 人类掌控 | 发送按钮始终对应坐席可见的最终文本 | 生成完成即自动发送 | confirmed |
| 故障可绕过 | AI 不可用时输入框、历史和发送保持可用 | AI 错误遮挡整个会话 | confirmed |
| 来源可核对 | 草稿旁显示引用和不确定状态 | 把无来源模型文本伪装成企业事实 | provisional |
| 高密度低干扰 | 一屏完成选会话、读上下文、编辑和发送 | 频繁弹窗或装饰性动效 | provisional |

## 信息架构

| 区域/页面 | 用户目标 | 入口/退出 | Related SPEC | State |
|---|---|---|---|---|
| 登录/租户选择 | 进入授权工作区 | 身份入口/控制台 | SPEC-CHAT-001 | provisional |
| 会话队列 | 发现待接待、处理中会话 | 控制台/会话工作台 | SPEC-CHAT-001 | confirmed |
| 会话工作台 | 查看历史、生成/编辑草稿、确认发送 | 会话队列/下一会话 | SPEC-CHAT-001, SPEC-AI-001, SPEC-AI-003 | confirmed |
| 知识库 | 上传、发布、撤回和检查状态 | 管理导航/详情 | SPEC-KB-001 | provisional |
| 运营与审计 | 查看 AI 状态、成本和确认记录 | 管理导航/详情 | SPEC-AI-004, SPEC-AI-005 | provisional |

## 会话工作台

- 三栏桌面布局：会话队列、消息时间线、上下文/AI 面板；窄屏下队列与侧栏折叠为抽屉。
- 草稿编辑器与人工输入共用最终发送区，但用明显的“AI 草稿”标签和引用区分来源。
- `生成草稿` 与 `确认发送` 是两个独立动作；生成中可以取消，未完成文本标记为不可直接发送，坐席编辑或显式确认后才发送。
- 连接、模型和知识库状态分别显示，避免把 AI 故障误报成聊天故障。

## 知识库

- 资料列表显示版本、处理状态、发布状态、更新时间和失败原因。
- 发布/撤回需要确认；处理失败可重试且不得改变当前已发布版本。

## 视觉方向

- Direction: restrained / utilitarian / dense（受控、工具型、偏高信息密度）。
- References: 借鉴成熟客服工作台的三栏操作结构，不复制品牌视觉。
- Explicitly avoid: 对话气泡过度拟物、彩色渐变、把 AI 塑造成自主角色、用颜色作为唯一状态线索。
- Typography: 系统无衬线字体；正文 14–16px；状态与时间 12–13px；代码/ID 使用等宽字体。
- Color semantics: 中性底色；蓝色表示坐席动作；绿色表示已发送；琥珀表示待确认；红色仅用于失败/危险。
- Spacing/grid/radius/elevation: 4px 基础网格，控件最小高度 36px，6–8px 圆角，仅浮层使用阴影。
- Motion: 150–200ms 状态过渡；尊重 `prefers-reduced-motion`；流式文本不使用逐字动画。

## Design tokens and components

| Topic | Source/decision | Override policy | State |
|---|---|---|---|
| 组件 | 采用成熟、可访问的 Web 组件库 | 仅为客服密度和语义状态封装，不 fork 基础控件 | provisional |
| Tokens | CSS 变量统一颜色、间距、字号和层级 | 不在页面写硬编码品牌色 | provisional |
| 图标 | 单一线性图标集并配文本/tooltip | 关键动作不只显示图标 | provisional |

## Responsive and platform behavior

| Context | Layout/input behavior | Related SPEC | State |
|---|---|---|---|
| ≥1280px | 三栏；消息区保持主要宽度 | SPEC-CHAT-001 | provisional |
| 768–1279px | 两栏；AI/上下文用抽屉 | SPEC-AI-001 | provisional |
| <768px | 只保证应急人工接待；单栏切换 | SPEC-CHAT-002 | provisional |
| 键盘 | Enter 发送需可配置；Shift+Enter 换行；生成与发送快捷键不同 | SPEC-AI-003 | confirmed |

## UI 状态矩阵

| Flow/screen | Loading | Empty | Error | Offline | Permission | Destructive action |
|---|---|---|---|---|---|---|
| 会话队列 | 骨架与连接状态 | “暂无待接待” | 可重试且保留已加载项 | 显示断线/重连 | 隐藏不可见队列 | 不适用 |
| 会话工作台 | 历史分页加载 | 引导选择会话 | 聊天与 AI 错误分离 | 禁用新发送并保留输入 | 只读并说明原因 | 结束会话需确认 |
| AI 草稿 | 首 token 指示器、可取消 | 未请求时不占屏 | 提示人工继续/重试 | 不发起请求 | 隐藏生成入口 | 清空草稿需确认 |
| 知识库 | 展示逐阶段处理状态 | 引导首个资料 | 失败原因与重试 | 禁止变更 | 只读/拒绝 | 发布与撤回需确认 |
| 成本限制 | 不适用 | 正常状态 | AI 限额提示 | 不适用 | 仅管理员见配置 | 提高硬限额需二次确认 |

## 可访问性与内容

- Accessibility target: Web 按 WCAG 2.2 AA 设计和测试。
- Keyboard/focus: 所有接待与发送动作可键盘完成；焦点不因流式 token 跳动；新消息提供非打断式 live region。
- Contrast/non-color: 状态同时使用文本、图标和颜色；正文/控件满足 AA 对比度。
- Screen reader: 消息包含发送者、时间和状态语义；草稿、引用、已发送消息有明确标签。
- Localization: MVP 使用 UTF-8，布局允许 30% 文本扩展；时间显示用户时区并保留机器时间。
- 内容口吻：简短、可行动，不用“AI 正在思考”；统一使用“草稿”“确认发送”“人工模式”。

## 内容与信任提示

- 草稿旁固定提示“请核对后发送”；引用可展开到来源标题和版本。
- AI 不可用时说明影响仅限草稿，不暗示消息丢失。
- 未找到知识时直说，无置信度百分比等伪精确信号。

## 待决定事项

无；品牌视觉可在不改变交互语义的前提下后续补充。
