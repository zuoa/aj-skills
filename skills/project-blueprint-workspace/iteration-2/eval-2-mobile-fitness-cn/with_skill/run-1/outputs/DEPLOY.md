---
blueprint_kind: deploy
blueprint_status: draft
owner: TBD-DEPLOY-001
last_reviewed: 2026-09-10
---

# 部署与运行

## 拓扑与预算

暂定中国大陆适用区域的托管应用运行时、托管关系数据库、私有对象存储/CDN和一个 worker。云、短信和推送供应商待官方能力、合同、区域、商店兼容与成本压测后选定。每月 8000 元是硬护栏，应用、数据库、照片存储/流量、短信和推送分别计量并设预算告警。

环境为 local、preview/test、production；非生产使用合成/去标识数据。CI 一次构建可追溯服务端与已签名移动构建物，测试后按渠道提升。秘密由托管 secret store 提供。

## 发布与移动商店

- 服务端迁移采用 expand/contract，滚动发布前验证兼容；失败停止/回滚，数据回滚限制写入 runbook。
- iOS/Android 分别管理 bundle/application ID、证书/签名、商店账号、隐私材料、SDK/权限清单、测试轨与分阶段发布。
- 后端保留移动版本兼容窗口；最低版本、远程关闭高风险能力和紧急修复流程 pending。
- 中国大陆域名、备案及商店渠道要求由 `TBD-COMPLIANCE-001` 在提交前以官方材料核验。

## 观测、备份与恢复

用户信号包括验证码成功路径、计划读取、打卡同步、照片处理、推送尝试和教练授权。结构化日志/指标/追踪使用关联 ID，不记录照片或完整手机号；按用户影响设置告警和负责人。

数据库和照片元数据/对象需加密备份或版本保护；定义 RPO/RTO、保留、跨故障域、删除传播、恢复顺序与定期恢复演练。短信/推送故障允许提醒降级但不影响计划/打卡事实。当前目标与责任未确认，production-ready blocked。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DEPLOY-001 | 确认云/区域、成本测算、商店/签名、SLO/告警、发布回滚、备份与 RTO/RPO | operations/release owner | 生产与商店提交前 | production-ready | pending |
