---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# 系统架构

## 约束

3 人 Flutter 团队、TypeScript 后端经验、6 个月、约 2 万日活、每月 8000 元基础设施预算要求少部署单元和低运维。延迟、峰值、照片量、SLO/RTO/RPO 未提供。

## 容器与模块边界

| Unit | Responsibility | State |
|---|---|---|
| Flutter iOS/Android | 学员训练、打卡、照片与推送 | confirmed/provisional implementation |
| Responsive Web | 教练端及学员 Web；TypeScript 框架待选 | provisional |
| TypeScript modular monolith API | auth/training/check-in/media/notification/access | provisional |
| Managed relational DB | 账户、计划、打卡、关系、审计事实 | provisional |
| Object storage + CDN | 私有照片与受控分发 | provisional |
| DB-backed worker | 短信/推送/媒体异步任务与重试 | provisional |

模块为 Identity、Training、CheckIn、Media、Notification、CoachAccess。单册写入式一致性不适用；打卡幂等键和版本处理离线重复/冲突。照片元数据与访问权在数据库，二进制私有存储；短期签名访问须重新鉴权。

## 外部依赖

短信与推送采用适用于中国大陆及目标平台的供应商，尚未选型。定义超时、有限重试、幂等、配额监控、凭据轮换和替代/导出路径；通知失败不回滚业务事务。Apple/Android 厂商推送通道的实际覆盖需真机验证。

## 技术决策

| Decision | Recommendation/tradeoff | State | Revisit trigger |
|---|---|---|---|
| 应用后端 | TypeScript 模块化单体，贴合团队且一次部署；边界先在代码建立 | provisional | 独立团队/隔离/负载证据 |
| 数据库 | 托管关系数据库；迁移和连接管理有成本 | provisional | 已证实不适合访问模式 |
| 异步 | 数据库任务表/简单 worker；避免专用 broker 运维 | provisional | 吞吐、延迟隔离或持久 fan-out 不满足 |
| 缓存 | 初期不引入 Redis | provisional | 测量热点且索引/查询优化不足 |
| 搜索/微服务/Kubernetes | 不引入 | provisional | 明确质量或团队边界成立 |
| 客户端 | Flutter 移动端；Web 技术由无障碍、交付与团队试验确认 | provisional | 原型证明单一技术更低风险 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 确认 Web 栈、峰值/照片量、质量预算、云/短信/推送供应商与容量成本测算 | technical-owner | 架构评审前 | implementation-ready | pending |
