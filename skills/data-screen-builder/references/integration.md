# 从示例到生产 API

## 本地运行

```bash
python3 <skill-path>/scripts/create_screen.py ./operations-screen
cd operations-screen
npm ci
npm run validate
npm test
npm run build:demo
npm run dev
```

需要 Node 22.12+ 或兼容的新版本。项目自带 lockfile。复制命令拒绝已有目标目录，避免覆盖；已有工程只迁入适用模块。阶段 5 用 `npm run dev:framework` 打开 `/?view=framework`，没有业务数据；完整页 `/` 的示例默认 mock 并明确标记。生产构建默认禁止 mock，只有明确的演示构建 `npm run build:demo` 允许示例数据。

独立 Python 校验器需要 `jsonschema`（`python3 -m pip install jsonschema`）；项目内 `npm run validate` 使用相同 Schema，不需要 Python 依赖。自定义组件在 `src/config/component-types.json` 的 custom 清单登记，并在启动前调用 `registerComponent`；静态清单供校验器使用，运行时另检查实际注册结果。组件接收 `binding/metric/result/reduced`，发出 `select(filter, value)`，不直接请求生产接口。

## 替换设计与地理资源

新流程先用 `framework.json` 选择独立 layout/palette，确认空框架，再改 `screen.json` 的业务指标绑定与 geography，在 `framework.json.bindings` 填组件 ID → 槽位 ID。完整页直接复用同一框架的标题、画布、色板和位置；不要再用 `designs.json` 覆盖。`npm run validate:framework` 不读取指标，`npm run validate` 还检查完整绑定。旧示例 bindings 为空时仍支持 designs.json 组合；定稿可删除不需要的演示控制项。

自定义 GeoJSON 放 public 下或通过同源资源网关提供，声明坐标系和 ID/名称字段。高德导入脚本与道路/水系/点位协议见 [空间渲染](spatial-rendering.md)。geo 属性 ID 必须与业务分组结果值一致；演示的 north/east/south/west 不会自动映射到行政 adcode。影像、照片和道路服务与指标服务各有资源接入边界。

## 已符合统一协议

复制 `.env.example` 为 `.env.local`，设置 `VITE_DATA_PROVIDER=http`，`VITE_METRICS_ENDPOINT=/api/metrics/query`。浏览器向该同源网关 POST 查询 JSON，网关返回指标结果 JSON。模板使用同源 cookie；认证由现有应用处理，不在前端保存长期 API 密钥。生产构建必须显式选择 HTTP，缺少配置直接失败。

## 现有字段不同

修改 `src/data/http.ts` 的 adapter，保持对外 `query(query, signal): Promise<MetricResult>` 不变。可按 `metricId` 路由到不同业务 API，在这一层转换请求与响应；支持取消，并在共享客户端执行结果校验后再交给组件。修改记录以“指标 ID → 路由 → 请求参数 → 原字段 → 契约字段 → 单位/时间转换 → 核对证据”组成映射表。

例如已有接口返回 `{updated_at, points:[{timestamp,kwh}]}`：`timestamp` 转为带时区 ISO 字符串映射到 `time`，`kwh` 映射到 `value`，`updated_at` 映射到 `dataAsOf`。不要按字段名称猜测时区或千倍单位，先查接口说明或用业务样本核对。空数据与网络异常分别处理；映射失败应报错，不返回空数组掩盖问题。

模板 `npm run serve:fixture` 在 127.0.0.1:4175 提供测试网关，使用相同 schema 和本地示例数据，可检验 HTTP 路径。开发配置将 `/api` 代理到这个地址；这是测试入口，不能称为生产对接已完成。实际网关地址通过服务端 `METRICS_PROXY_TARGET` 配置，不进入浏览器 bundle。

## 服务端适配边界

若需密钥、数据库或私网，在已有后端新增路由，不从浏览器直连：

```text
POST /api/metrics/query
  复用登录与租户上下文
  校验请求并按指标 ID 选择允许的上游路由
  验证过滤维度与用户数据权限，设置超时/查询限制
  用服务端环境密钥请求上游
  按已核对的字段、单位、时区映射结果并校验
  返回契约 JSON；故障返回合适 HTTP 状态及可追踪请求 ID
```

指标 ID 不应接受用户任意 URL 或 SQL。缓存键包含实际用户授权范围，不能只用浏览器传入的 tenantId。401/403 不自动重试；普通瞬时失败由客户端退避。模板 HTTP 错误仅显示状态码，不把上游响应正文或密钥回显到页面。

项目栈未知时交付上述接口、adapter 及映射文档，不虚构现有后端实现或创建不必要的独立服务。已知后端栈时实现该模块并用脱敏响应 fixture 测试，不将真实凭据写入产物。

## 接入验收

用同一 `screen.json` 先跑 mock，再切换 HTTP fixture，验证组件无须改代码。接真实 API 时核对至少一个总量、一个分组、一个时间序列及单位/时间窗口；记录来源、日期和可复核样本。未取得接口权限或资料时明确 `not-run`。

## 隐藏指标填报

所有生成项目默认包含 [REPORTING.md](../assets/vue-screen/REPORTING.md)。完整页用 `Ctrl/⌘ + Shift + E` 或 `?view=report` 打开 `MetricReport.vue`，不在常规大屏、显示设置或空框架放填报按钮。表单从目录与查询生成字段，不硬编码示例指标名；新增指标、维度或组件后仍可填报。

`src/data/local-reports.ts` 负责版本化存储、作用域隔离、结果校验和写入失败处理；`QueryClient` 在共享查询层优先应用主动保存的本地结果，取消该范围进行中的请求并立即发布状态，避免迟到响应和自动刷新覆盖。移除填报后恢复原 provider。HTTP 故障本身不会创建本地值或切换 mock。

缓存只在同一查询范围及同长度滚动窗口复用，保留真实的 `dataAsOf`，不跨区域/粒度聚合、不伪造新鲜时间。大屏面板标明“本地填报”；查看数据与口径时显示实际来源。缓存包括指标定义签名；口径或结构变化后旧值失效。`storage` 事件用于同源标签页同步。表单锁定打开时的筛选范围，轮询结果不覆盖已修改的草稿。

既有工程迁入时同时接入存储层、共享查询更新、隐藏入口、来源提示和恢复操作，不能只迁移一个无效按钮。前端缓存不承担后端填报、跨设备共享或鉴权；需要这些能力时再接现有服务。
