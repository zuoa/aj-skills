---
blueprint_kind: design
blueprint_status: draft
owner: design-owner
last_reviewed: 2026-09-10
---

# 产品设计约束

## 体验原则

| Principle | User consequence | Anti-pattern | State |
|---|---|---|---|
| 今日优先 | 打开即看今天练什么和一个主动作 | 首页堆排行榜、资讯和营销卡片 | provisional；任务完成率验证 |
| 一次一决策 | 每屏一个明确主操作，打卡不超过两步 | 提交前强迫填体重、照片或长问卷 | provisional |
| 成功可证明 | 只在服务端确认后显示完成时间 | 网络超时先显示绿色成功 | confirmed by SPEC |
| 私密可预期 | 照片旁持续显示“仅你和教练可见” | 用含糊图标代替可见范围 | provisional |
| 权限克制 | 在用户触发功能时解释并申请 | 首次启动连弹相册、相机、通知权限 | provisional |
| 教练高密度 | 桌面端用筛选、表格和侧栏减少跳转 | 把移动大卡片机械放大到桌面 | provisional |

## 信息架构

| 区域/页面 | 用户目标 | 入口/出口 | Related SPEC | State |
|---|---|---|---|---|
| 体验训练 | 未登录先理解价值并完成一次训练 | 启动页→体验；可转登录 | SPEC-PLAN-001 | provisional |
| 登录 | 获取/验证验证码 | 启动或受保护入口→今日 | SPEC-IDENTITY-001, SPEC-IDENTITY-002 | confirmed scope |
| 今日 | 查看当日动作、开始并打卡 | 移动底栏首项/Web 侧栏 | SPEC-PLAN-001, SPEC-CHECKIN-001 | confirmed scope |
| 计划 | 查看周/月安排和版本 | 底栏/侧栏→训练详情 | SPEC-PLAN-001, SPEC-PLAN-002 | confirmed scope |
| 历史 | 查看打卡、感受和照片 | 底栏/侧栏→日期详情 | SPEC-CHECKIN-002 | confirmed scope |
| 我的/设置 | 提醒、时区、隐私、退出/注销 | 底栏/头像菜单 | SPEC-REMINDER-001, SPEC-PRIVACY-002 | confirmed scope |
| 教练工作台 | 搜索/筛选会员 | 教练 Web 登录→会员详情 | SPEC-COACH-001, SPEC-COACH-002 | confirmed scope |
| 计划编辑器 | 草稿、预览、发布版本 | 会员详情→确认发布 | SPEC-COACH-003 | confirmed scope |

移动会员端底栏为“今日 / 计划 / 历史 / 我的”；会员 Web 使用左侧导航；教练 Web 是独立角色入口，不在会员导航暴露。

## 关键页面与旅程

1. **首次使用**：价值说明→“先体验”或“手机号登录”；隐私摘要在发送验证码前可见。
2. **打卡**：今日动作→“完成训练”→可选感受/照片→确认；上传未完成时说明哪些照片尚未附加。
3. **提醒**：设置解释→用户主动开启→系统权限→时间/星期→保存；被拒绝时保留系统设置入口。
4. **教练跟进**：默认“今日未完成”筛选→会员详情抽屉→历史/照片→未来计划草稿→预览→发布确认。
5. **注销**：说明影响→再次短信验证→最终确认→受理编号与退出。

## 视觉方向

- **Direction**：克制的训练日志工具；高对比中性色为底，单一能量橙作主操作色，进度使用数字与文字而非装饰环。
- **Borrow**：日历的日期可扫描性、训练清单的步骤感、专业教练表格的密度；不复制具体品牌资产。
- **Avoid**：霓虹健美海报、全屏渐变、玻璃拟态、身体羞辱文案、把红/绿作为唯一状态线索、无意义连续动画。
- **Typography**：中文优先系统字体（iOS PingFang SC、Android/Web Noto Sans SC/系统回退）；标题 24/32、页面标题 20/28、正文 16/24、辅助 14/20、数据等宽数字特性。
- **Color semantics**：Brand `#E85D04`；文本 `#171717`；背景 `#F7F7F5`；成功 `#147D3F`；警告 `#9A5A00`；错误 `#B42318`；各状态同时配文字/图标。正式品牌到位或 AA 对比失败即重评。
- **Spacing/grid/radius/elevation**：4 px 基元；间距 8/12/16/24/32；移动 4 列 16 px 边距，桌面 12 列最大内容宽 1280 px；圆角 8/12；仅浮层使用两级阴影。
- **Motion/imagery**：150–220 ms 状态过渡并尊重 reduced motion；动作示意优先内容团队审核的静态图，不用未经同意的用户照片作装饰。

## Design tokens 与组件

| Topic | Source/decision | Override policy | State |
|---|---|---|---|
| 语义 token | 单一 JSON/Dart token 源生成 Flutter Theme；Web 也用同一 Flutter token | 页面不得写裸色值；可新增语义 token | provisional |
| 基础组件 | Flutter Material 3 能力作无障碍基线，品牌层仅改 token/有限外观 | 保留原生焦点、语义和点击反馈 | provisional |
| 表单 | 统一字段、帮助、错误、OTP、日期/时间选择器 | 不以 placeholder 代替 label | provisional |
| 反馈 | inline message、snackbar、banner、dialog 按严重度 | 关键失败不得只用短暂 snackbar | provisional |
| 数据表 | 桌面教练端专用，可排序列、分页、筛选条 | <768 px 转列表，不强塞横向表格 | provisional |

## 响应式与平台行为

| Context | Layout/input/safe-area behavior | Related SPEC | State |
|---|---|---|---|
| 手机 `<600` CSS px | 单列、底部导航、主按钮在安全区上方；最小触控目标 44×44 pt / 48×48 dp | SPEC-PLATFORM-001 | provisional |
| 平板 `600–1023` | 导航栏或窄侧栏；计划详情可双栏 | SPEC-PLATFORM-001 | provisional |
| 桌面 `≥1024` | 侧栏 + 主内容；教练列表/详情 7:5 分栏，键鼠完整操作 | SPEC-COACH-002 | provisional |
| iOS | 遵循 safe area、系统返回手势、APNs 权限和照片选择器 | SPEC-REMINDER-001, SPEC-MEDIA-001 | confirmed platform / provisional detail |
| Android | 系统返回、运行时通知/媒体权限、OEM 省电导致的提醒限制可解释 | SPEC-REMINDER-002 | provisional |
| Web | 360–1440 px 无水平页面溢出；可刷新/深链，敏感页不进共享缓存 | SPEC-PLATFORM-001 | provisional |

首个支持矩阵 provisional：iOS 当前主版本及前 2 个大版本；Android API 26+；Web 最近两个稳定大版本 Chrome/Edge/Safari。M2 真实设备覆盖或商店数据显示 >2% 目标用户不在矩阵内时重评。

## UI 状态矩阵

| Flow/screen | Loading | Empty | Error | Offline | Permission | Destructive action |
|---|---|---|---|---|---|---|
| 今日/计划 | 骨架保留布局 | “今日未安排”+下一步 | inline 重试 | 缓存+时间戳 | N/A | N/A |
| 打卡 | 按钮进度且防重 | 无感受/照片也可提交 | 保留输入，说明未提交 | 存草稿，明确未提交 | 照片拒绝不阻断 | 删除照片二次确认 |
| 照片 | 逐张进度/模糊占位 | 可选，不催促 | 逐张重试 | 不开始上传 | 解释后按需申请 | 明确 24 小时删除语义 |
| 提醒 | 保存中禁重复 | 未开启 | 保存失败保留原设置 | 禁止保存并保留草稿 | 显示系统状态/设置入口 | 关闭无需危险式确认 |
| 教练会员列表 | 表头骨架 | 清筛选/无分配说明 | 保留筛选并重试 | 只读缓存禁止发布 | 越权用通用结果 | 发布计划需确认 |
| 注销 | 验证/受理进度 | N/A | 保留受理上下文 | 不可提交 | N/A | 两步确认+再次验证 |

## 无障碍与内容

- Web 目标为 WCAG 2.2 AA；移动端对齐平台语义、动态字体和屏幕阅读器惯例，发布前以自动扫描加人工键盘/VoiceOver/TalkBack 验证。
- 焦点顺序与视觉顺序一致；所有操作键盘可达；焦点环不移除；触控目标至少 44 pt（iOS）/48 dp（Android）。
- 正文/背景对比至少 4.5:1，大文本至少 3:1；状态不只靠颜色；照片缩略图提供用途描述而非推断身体属性。
- 支持系统字体放大至 200% 时核心任务无内容丢失；上传进度、错误和成功以 live region/语义公告。
- 仅简体中文（MVP）；日期 `YYYY年M月D日`，时间 24 小时制，时区名称可见；文案布局预留 30% 扩展。
- 语气短、具体、无评判：“今天还未打卡”而不是“你又偷懒了”；健康风险用“停止训练并咨询专业人员”，不作诊断。

## 待决定事项

无阻断设计项。正式品牌资产到位后只替换 token 与素材；若改变信息层级，必须回到原型验收。

