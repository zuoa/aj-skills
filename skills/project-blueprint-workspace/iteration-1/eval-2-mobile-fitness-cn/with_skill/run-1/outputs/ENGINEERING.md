---
blueprint_kind: engineering
blueprint_status: draft
owner: tech-lead
last_reviewed: 2026-09-10
---

# 工程规则

## 工作原则

- 编码前读取关联 PRD、领域 SPEC、DESIGN/ARCHITECTURE/SECURITY/DEPLOY；发现冲突先提出，不在代码里发明行为。
- 每个变更关联 PRD/SPEC/缺陷 ID；先写或更新可观察验收，再实现最小范围。
- provisional 是可实现默认，不是事实；重评触发发生时先记录证据和文档决策。
- 不引入 Redis、broker、搜索、微服务或 Kubernetes，除非 ADR 给出量化证据和退出路径。
- 不记录手机号、验证码、token、照片 URL/内容或请求 body；生产数据不得复制到非生产。

## 仓库地图（初始化目标）

| Area | Path | Responsibility | Read before changing |
|---|---|---|---|
| Blueprint | `/PRD.md`, `/SPEC.md`, `/specs`, design/architecture/security/deploy | 权威约束 | 对应领域文件 |
| Flutter apps | `/apps/client` | iOS/Android/member Web/coach Web、design system | DESIGN.md; specs/* |
| API/worker | `/apps/server` | NestJS API 与 worker entrypoint | ARCHITECTURE.md; SECURITY.md |
| Shared API | `/packages/api-contract` | OpenAPI schema/generated clients | SPEC.md; compatibility rules |
| Database | `/apps/server/prisma` | schema/migrations/seeds | ARCHITECTURE.md#数据与一致性; DEPLOY.md |
| Infrastructure | `/infra` | IaC、dashboards、runbooks | DEPLOY.md; SECURITY.md |
| ADR | `/docs/adr` | durable decisions | relevant blueprint docs |

实际仓库尚未创建；以上均为 provisional 目标，不授权本蓝图生成业务脚手架。

## Canonical commands（仓库初始化后必须映射为脚本）

| Purpose | Command | Scope/notes |
|---|---|---|
| Install | `corepack pnpm install --frozen-lockfile && flutter pub get` | Node workspace + Flutter |
| Dev API | `pnpm dev:server` | API/worker local adapters |
| Dev client | `flutter run` | 在 `/apps/client` 选择 target |
| Unit tests | `pnpm test && flutter test` | backend + Flutter |
| Integration tests | `pnpm test:integration` | PostgreSQL/provider fake；禁止生产依赖 |
| E2E | `pnpm test:e2e` | staging synthetic personas + device matrix |
| Typecheck/lint | `pnpm lint && pnpm typecheck && flutter analyze` | 0 error/warning policy在仓库冻结 |
| Build | `pnpm build && flutter build web && flutter build appbundle && flutter build ipa --no-codesign` | CI unsigned iOS，release job 签名 |
| Blueprint validation | `python3 <project-blueprint-skill>/scripts/validate_blueprint.py .` | 文档结构/追踪 |

命令名称是 provisional；TBD-ENGINEERING-001 在首个垂直切片完成时以 CI 实际可运行结果确认。

## 代码与依赖规则

- TypeScript `strict`；输入先 schema 验证；领域错误映射稳定代码；不跨模块 import 私有 repository/model。
- NestJS 模块按 ARCHITECTURE 边界；数据库事务留在 use case；外部 provider 全部经 adapter；超时、重试和幂等显式。
- Flutter 按 feature 划分 presentation/application/domain/infrastructure，避免为了分层创建空抽象；平台权限经单一 adapter；UI 只消费生成 API client。
- OpenAPI 为客户端契约源；生成文件不得手改，生成命令与源 commit 入头部；破坏性 API 用新路径/字段迁移并保持两个移动版本窗口。
- PostgreSQL migration 只追加/兼容；索引变更评估锁；backfill 可恢复/限速；原始 SQL 需说明为何 ORM 不足并有测试。
- 依赖需写用途、维护状态、许可证、二进制/SDK 数据流、替代/移除成本；移动 SDK 还需权限/域名/启动时机审查。锁文件必提交，不用 floating tag/action。
- 结构日志使用事件名、correlation ID、actor pseudonymous ID 和结果码；用户可见错误用稳定 code + 中文信息，内部原因只入脱敏日志。

## 测试与审查闸门

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|
| PRD/SPEC behavior | Given/When/Then 对应 contract/E2E；追踪矩阵更新 | product-owner |
| OTP/session/authz | unit + integration + replay/rate/IDOR negative cases；threat review | security-owner |
| Plan/checkin | timezone/property、unique/idempotency/concurrency、migration | backend-lead |
| Photo | magic byte/limits/malicious corpus、object auth、EXIF、delete/backup | security-owner |
| Reminder | timezone/DST、dedupe、失效 token、provider outage fake/真机 | mobile-lead |
| Coach UI | keyboard/AA、role matrix、分页/20k DAU synthetic perf | design + backend |
| DB migration | dry-run、锁/时长、backfill resume、forward rollback plan | backend + ops |
| Release/IaC | scan、SBOM/provenance、staging smoke、canary/rollback evidence | release-owner |

测试金字塔：领域规则 unit；PostgreSQL/adapter contract integration；每个 SPEC 至少一个正常和一个相关失败 E2E；权限边界全部自动化。不能用 mock 验证 SQL 唯一约束、对象策略或 provider contract。

## Definition of done

- 关联 PRD/SPEC/ADR 保持当前状态，验收证据可定位；没有未声明行为变化。
- format/lint/typecheck/unit/integration 和相关 E2E/安全检查通过；失败/边界/权限/弱网得到验证。
- schema/配置/feature flag/日志/指标/runbook/成本和回滚影响已处理；移动变更验证旧版本兼容。
- 隐私字段、权限、SDK、数据地域或保留变化已更新数据清单/PIPIA；日志与分析无敏感数据。
- 只保留意图内 diff；generated files 可复现；发布制品带 commit、SBOM、签名和迁移版本。

## 分支、评审与发布纪律

- 短生命周期分支、small PR；主分支持续可发布。禁止直接推 production tag。
- 行为/架构/安全高影响变更至少 2 人（作者外 1 人）审查；生产迁移、权限和密钥双人审批。
- 缺陷修复先加失败测试；紧急修复 2 个工作日内补齐文档/测试/复盘。
- 性能结论必须附数据集、环境、命令、时间和 p50/p95/p99；“看起来更快”不作为证据。

## 待决定事项

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 仓库垂直切片后确认实际目录、pnpm/Flutter 命令、CI 门禁、coverage baseline 与 code owners | tech-lead | M1 末 | production-ready | pending |

