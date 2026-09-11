# 数据与 API 契约

## 1. 数据原则

- PostgreSQL 是账户、计划、打卡、授权和提醒规则的事实源。
- ID 使用 UUIDv7/同类时间有序随机 ID；对外不可暴露自增规模信息。
- 所有业务表含 `created_at`、`updated_at`；可编辑事实含 `version`。
- 时间戳以 UTC 存储，业务日额外保存 `local_date` 与计算时使用的 IANA `timezone`。
- 删除分为业务软删除和隐私擦除；软删除不是履行个人信息删除请求。
- 任何分析事件不得包含手机号、照片 URL、自由文本备注或精确身份标识。

## 2. 核心实体

| 实体 | 关键字段 | 约束/索引 |
|---|---|---|
| users | id, phone_ciphertext, phone_hash, status, timezone | phone_hash 唯一；手机号应用层信封加密 |
| consents | user_id, purpose, policy_version, granted, occurred_at, evidence | `(user_id,purpose,occurred_at)` 索引，不覆盖历史 |
| sessions | id, user_id, refresh_hash, device_id, expires_at, revoked_at | refresh token 仅存哈希 |
| coach_profiles | user_id, organization_id, status | 教练身份需后台审核 |
| coach_memberships | coach_id, member_id, status, accepted_at, ended_at | 活跃关系唯一 |
| exercise_catalog | id, title, instructions, media_id, status | 发布后版本化 |
| plan_templates | id, coach_id, title, status, current_version | coach/status 索引 |
| plan_template_versions | id, template_id, version, snapshot_json | `(template_id,version)` 唯一，不可变 |
| plan_assignments | id, member_id, coach_id, template_version_id, start_date, status | member/start/status 索引 |
| plan_days | id, assignment_id, local_date, content_snapshot | `(assignment_id,local_date)` 唯一 |
| checkins | id, member_id, plan_day_id, local_date, duration_min, feeling, note, version | 业务唯一约束；note ≤ 1000 字 |
| media_assets | id, owner_id, purpose, object_key, status, sha256, bytes, mime | object_key 唯一；owner/status 索引 |
| checkin_media | checkin_id, media_id, position | 每打卡最多 3 张 |
| reminder_rules | id, user_id, weekdays, local_time, timezone, enabled, next_at | enabled/next_at 索引 |
| notification_deliveries | id, rule_id, occurrence_at, channel, status, provider_code | `(rule_id,occurrence_at,channel)` 唯一 |
| device_tokens | user_id, platform, provider, token_ciphertext, status, last_seen_at | token 哈希去重 |
| audit_events | actor_id, action, resource_type/id, reason, ip_prefix, occurred_at | 按月分区；仅追加 |
| outbox_events | aggregate_type/id, type, payload, published_at | unpublished 部分索引 |
| privacy_requests | user_id, type, status, due_at, completed_at | user/status 索引 |

### 2.1 状态机

- `plan_template`: `draft -> published -> archived`；published 版本不可编辑，只能生成新版本。
- `plan_assignment`: `scheduled -> active -> completed | cancelled`；取消不删除历史打卡。
- `media_asset`: `initiated -> uploaded -> processing -> ready | rejected -> deleted`。
- `privacy_request`: `requested -> identity_verified -> processing -> completed | rejected`；拒绝需原因和复核记录。
- `user`: `active -> suspended | deletion_pending -> deleted`；删除待定期间可撤销，执行后不可恢复登录。

## 3. API 通用规范

- Base path：`/api/v1`；HTTPS only；JSON 使用 `application/json; charset=utf-8`。
- 字段使用 `camelCase`，枚举使用 `snake_case`，时间使用 RFC 3339 UTC，日期为 `YYYY-MM-DD`。
- 请求头：`Authorization: Bearer`、`X-Request-Id`、写请求 `Idempotency-Key`、更新请求 `If-Match`。
- 列表使用 cursor 分页：`?limit=20&after=opaque`，默认 20、最大 100；返回 `pageInfo.nextCursor`。
- API 版本在 URL；新增可选字段兼容，删除/改义必须升大版本并至少提前一个移动端强制升级周期。
- 所有响应携带 `requestId`；服务端拒绝未知枚举但容忍未知响应字段。

### 3.1 成功与错误封装

```json
{
  "data": { "id": "01J..." },
  "meta": { "requestId": "req_..." }
}
```

```json
{
  "error": {
    "code": "CHECKIN_VERSION_CONFLICT",
    "message": "打卡已在其他设备更新",
    "fieldErrors": [],
    "retryable": false
  },
  "meta": { "requestId": "req_..." }
}
```

状态码：400 格式错误；401 未认证；403 无权限；404 不存在或无权感知；409 状态/版本冲突；422 业务校验；429 限流；500/503 服务异常。客户端只按稳定 `code` 分支，不解析 message。

## 4. 端点目录

### 4.1 身份

| 方法与路径 | 作用 | 关键规则 |
|---|---|---|
| `POST /auth/otp/challenges` | 发起验证码 | IP/设备/手机号频控；统一响应防枚举 |
| `POST /auth/otp/verifications` | 校验并登录 | 返回 access token；Web 设置 refresh cookie |
| `POST /auth/tokens/refresh` | 轮换 token | 旧 refresh 复用则撤销 token family |
| `POST /auth/logout` | 撤销当前会话 | 幂等 |
| `GET /sessions` | 查询设备会话 | 手机型号需粗化 |
| `DELETE /sessions/:id` | 踢出设备 | 资源所有权校验 |

验证码限流基线（**provisional**）：同手机号 1 次/60 秒、5 次/小时、10 次/日；同 IP 30 次/小时；风险命中要求人机验证。重评：短信攻击成本 > 预算 5%、误拦截 > 1%，或供应商风控能力变化。

### 4.2 会员与计划

| 方法与路径 | 作用 |
|---|---|
| `GET /me` / `PATCH /me` | 本人资料读取/更新 |
| `GET /me/plan-days?from=&to=` | 日期范围计划日 |
| `GET /plan-days/:id` | 计划日详情 |
| `GET /me/checkins?from=&to=` | 本人打卡列表 |
| `POST /checkins` | 创建打卡 |
| `PATCH /checkins/:id` | 乐观锁编辑 |
| `DELETE /checkins/:id/media/:mediaId` | 删除照片关联并排队擦除 |

创建打卡示例：

```json
{
  "planDayId": "01J...",
  "localDate": "2026-09-10",
  "timezone": "Asia/Shanghai",
  "durationMinutes": 45,
  "feeling": 4,
  "note": "状态不错",
  "mediaIds": ["01J..."]
}
```

### 4.3 媒体

| 方法与路径 | 作用 |
|---|---|
| `POST /media/upload-sessions` | 创建受限直传会话 |
| `POST /media/upload-sessions/:id/complete` | 声明上传完成并排队处理 |
| `GET /media/:id` | 元数据及短期读取 URL（授权后） |
| `DELETE /media/:id` | 删除本人媒体 |

创建会话必须提交 `purpose=checkin_photo`、`contentType`、`contentLength`、`sha256`；服务端返回不可预测 object key，绝不使用原文件名。

### 4.4 提醒与设备

| 方法与路径 | 作用 |
|---|---|
| `PUT /me/device-tokens/:deviceId` | 注册/更新推送 token |
| `DELETE /me/device-tokens/:deviceId` | 注销 token |
| `GET /me/reminder-rules` | 查询提醒 |
| `POST /me/reminder-rules` | 创建提醒 |
| `PATCH /me/reminder-rules/:id` | 修改/停用提醒 |
| `POST /notification-deliveries/:id/click` | 记录点击；不接受任意用户 ID |

### 4.5 教练

| 方法与路径 | 作用 | 授权 |
|---|---|---|
| `GET /coach/members` | 名下会员列表/筛选 | active membership |
| `GET /coach/members/:id/summary` | 会员完成汇总 | active membership |
| `GET /coach/members/:id/checkins` | 打卡详情 | active membership；照片另校验同意 |
| `POST /coach/plan-templates` | 创建草稿 | coach role |
| `POST /coach/plan-templates/:id/versions` | 保存新版本 | owner/organization policy |
| `POST /coach/plan-templates/:id/publish` | 发布 | 完整性校验 |
| `POST /coach/plan-assignments` | 分配计划 | 最多 100 人；逐人关系校验 |

## 5. 幂等、并发与事件

- 所有创建、上传完成、批量分配和隐私请求必须支持 `Idempotency-Key`；key 绑定用户 + 路径 + body hash。
- 相同 key/body 返回首次结果；相同 key/不同 body 返回 409。
- `PATCH` 携带资源版本；服务端 `UPDATE ... WHERE id=? AND version=?`。
- outbox 事件至少投递一次；消费者按 event ID 幂等，不能假设恰好一次。
- 领域事件示例：`checkin.created.v1`、`checkin.updated.v1`、`media.ready.v1`、`plan.assigned.v1`、`user.deletion_requested.v1`。
- 事件载荷仅含所需 ID 和非敏感派生值，不含手机号、备注或照片 URL。

## 6. 数据质量与迁移

- 数据库迁移向前兼容：先加可空字段/双写，再回填/切读，最后移除旧字段；禁止发布时长事务全表改写。
- 每日校验孤儿媒体、重复提醒、无对应关系的教练查询模型、outbox 积压。
- 生产修数必须通过审计脚本、双人复核、限定行数和回滚方案；禁止直接手工更新无记录。
- OpenAPI、数据库 schema 和事件 schema 进入版本库；CI 做 breaking-change 检测。

