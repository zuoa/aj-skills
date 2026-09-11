---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# 系统架构

## 约束与系统上下文

两个 Web 表面共享时段和预约事实，并须防止容量超订。团队、规模、延迟、可用性、预算与地区未知，不创建数字预算。

教练/学员浏览器经 HTTPS 访问响应式 Web 与模块化单体；关系型数据库是时段、预约、账户和审计的事实来源。支付、短信/邮件、日历同步与视频服务不在确认范围。

## 模块边界

| Module | Responsibility | Related SPEC |
|---|---|---|
| Scheduling | 课程、时段、容量和发布状态 | SPEC-SCHEDULE-001 |
| Booking | 预约状态机、容量占用与取消 | SPEC-BOOKING-001, SPEC-BOOKING-002 |
| Identity | 教练会话和资源所有权 | SPEC-ACCESS-001 |
| Public catalog | 安全公开可预约投影 | SPEC-BOOKING-001 |

## 数据与一致性

时段与预约在同一关系事务内检查容量并写入；唯一/容量约束由数据库可执行控制及并发测试保证。状态写入使用预期版本，冲突不静默覆盖。公开投影不含学员资料。

## 技术决策

| Decision | Recommendation | State | Revisit trigger |
|---|---|---|---|
| 应用形态 | 一个可部署的模块化单体 | provisional | 独立团队、隔离或扩展边界出现 |
| 存储 | 一个事务关系数据库 | provisional | 已证实的非关系访问需求 |
| 缓存 | 不引入 | provisional | 测量热点且数据库优化不足 |
| 队列/Kafka | 不引入；确认持久通知后再评估简单 worker | provisional | 需要持久重试或突发吸收 |
| Elasticsearch | 不引入 | provisional | 已确认复杂检索和数据库能力不足 |
| Kubernetes/微服务 | 不引入 | provisional | 平台团队与独立部署需求成立 |

依赖不可用时不声称预约成功；未来通知失败不得回滚已提交预约，而应显示可核对状态并重试通知。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 确认技术栈、团队、规模、性能/可用性预算、通知与日历集成 | technical-owner | 实现前 | implementation-ready | pending |
