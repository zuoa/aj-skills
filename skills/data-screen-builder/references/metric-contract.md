# 指标契约 v1

机器定义见 `assets/vue-screen/src/contracts/contract.schema.json`，对应类型在同目录 `types.ts`。Schema 管结构，`validate.mjs` 管跨引用与语义，不能分别维护互不兼容的“文档协议”。业务指标登记在生成项目 `src/config/metrics.json`，查询及组件在 `src/config/screen.json`。

## 目录、查询、结果、绑定

- 目录以稳定 `metric.id` 标识业务度量，包含定义、单位、精度、聚合性质、正向方向、允许维度/粒度、刷新/过期毫秒、来源和负责人。允许维度不要求每次查询全部返回。
- 查询包含 `metricId`、所选 `dimensions`、`filters`、`timeRange`、`granularity`，可带排序与限制。时间范围为带偏移的 ISO 8601，区间采用 `[from,to)`；时区采用 IANA 名称，用于分桶解释。`none` 表示不做时间分桶，不表示可以忽略时间过滤。
- 结果包含 `version`、`metricId`、`fields`、`rows`、`dataAsOf`、`fetchedAt` 和 `quality`。数值字段固定名为 `value`，时间分桶字段固定为 `time`；其余字段与已选维度一致。`quality` 为 `ok/partial/stale`，接口失败用 HTTP 错误或 provider 异常表达，不伪造有效结果。
- 绑定通过 `queryId` 和 `fields` 连接组件与结果，配置 `layout`、可选阈值及 `interaction`。新组件通过注册表接入，仍消费相同查询状态。

结果中每行只能包含声明字段，字段必须存在但可为 `null`；数值必须是有限 JSON number。`null` 是未知，`0` 是已知零，`rows: []` 是没有记录。表格可以呈现 null，折线保留断点。单位换算仅在 adapter 执行并记录，百分比示例使用 0–100，不能再乘 100。

示例查询：

```json
{
  "metricId": "energy.consumption",
  "dimensions": [],
  "filters": {"area": "north"},
  "timeRange": {"from": "2026-10-11T00:00:00+08:00", "to": "2026-10-12T00:00:00+08:00", "timezone": "Asia/Shanghai"},
  "granularity": "hour"
}
```

结果字段为 `time:timestamp` 与 `value:number`。`dataAsOf` 是数据实际覆盖的截至时间，不能用浏览器接收时刻冒充；`fetchedAt` 是此次读取时刻。过期判断以 `dataAsOf` 为准，因此快速重复收到旧数据仍显示过期。部分结果可展示，但必须标记不完整。

## 兼容性与口径

协议用 `version: "1"` 显式版本化；破坏性变更升级版本。新增业务指标无需改协议。改计算定义、单位或聚合性质时新增指标 ID 或明确迁移影响，不悄悄重用旧 ID。

`aggregation` 是口径说明及审查依据，不授权前端重新计算。`ratio` 需服务端使用正确分子/分母，`distinct` 跨分组不可直接相加，`last` 需要明确快照时刻。同比环比由服务端指标或明确的比较查询提供；分母为零或窗口不完整时用 null 与说明，不显示虚假零增长。

刷新参数是请求建议，生产缓存与频控仍由后端保证。多个组件引用同一完整查询共享请求，缓存键包含指标、维度、筛选、时间/时区、粒度、排序和 limit。不同权限的缓存隔离由服务端保证；浏览器登录身份变化应重建查询客户端。
