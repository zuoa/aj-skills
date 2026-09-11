---
blueprint_kind: domain-spec
blueprint_status: draft
owner: security-owner
last_reviewed: 2026-09-10
domain: media
source_prd: PRD-MEDIA-001
---

# 照片行为规格

## SPEC-MEDIA-001 — 上传打卡照片

- Source: PRD-MEDIA-001
- State: confirmed（能力）；数量/大小 provisional
- Actors: 已登录会员
- Preconditions: 用户主动选择相机或相册，并已按平台流程处理权限。
- Requirement: 每次打卡最多接收 3 张 JPEG/PNG/HEIC、单张不超过 10 MiB；逐张显示进度和结果。客户端声明不作为文件类型证据。
- Acceptance method: 格式矩阵、损坏/伪装文件、限额、断点失败和真机权限验收。

### Scenario: 成功上传

- **GIVEN** 合法图片且未超过数量/大小限制
- **WHEN** 会员选择并上传
- **THEN** 每张显示进度，服务端确认后显示缩略图；原始对象地址不暴露

### Scenario: 部分失败

- **GIVEN** 三张中一张损坏
- **WHEN** 上传完成
- **THEN** 两张成功保留，损坏文件明确失败并可单独重试，不重复成功文件

### Scenario: 权限拒绝

- **GIVEN** 用户拒绝相册/相机权限
- **WHEN** 返回打卡页
- **THEN** 仍可无照片打卡，并看到去系统设置的可选指引

## SPEC-MEDIA-002 — 私密访问与删除

- Source: PRD-MEDIA-001
- State: confirmed（私密/删除）；签名链接有效期 provisional
- Actors: 会员、当前获授权教练
- Preconditions: 照片已完成安全处理并与打卡关联。
- Requirement: 本人和当前获授权教练可通过短时授权查看；其他人不可访问；会员删除后立即从界面消失，源文件在 24 小时内进入不可恢复删除，备份按既定周期到期。
- Acceptance method: 对象级授权、过期链接、缓存、删除队列和备份恢复排除测试。

### Scenario: 授权查看

- **GIVEN** 教练当前被分配该会员
- **WHEN** 打开照片
- **THEN** 获得最长 5 分钟有效的受限访问，页面不显示公开永久 URL

### Scenario: 链接过期或越权

- **GIVEN** 链接已过期或访问者无授权
- **WHEN** 请求照片
- **THEN** 对象不可读取，响应不泄露对象是否存在

### Scenario: 用户删除

- **GIVEN** 会员确认删除照片
- **WHEN** 系统受理
- **THEN** 照片立即从会员和教练界面消失，并显示删除状态；24 小时后源对象不可恢复访问

## 领域不变量

| Rule | Observable effect | State |
|---|---|---|
| 照片默认私密 | 无公开列表、永久 URL 或搜索入口 | confirmed |
| 不保留可用 EXIF 定位 | 下载处理后图片不含 GPS 元数据 | provisional |

## 待决定事项

无；对象存储/扫描供应商由部署待决定项统一管理。

