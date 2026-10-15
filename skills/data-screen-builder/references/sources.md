# 来源与适用边界

调研基线：2026-10-13。以下为可追溯的官方资料；库版本及支持范围随时间变化，升级时重新核对。本文的分层架构、协议字段和目录结构是本技能的工程选择，不宣称为行业统一标准。

| 来源 | 吸收的实践 | 适用边界 |
| --- | --- | --- |
| [用户提供的 h4 校园能耗驾驶舱](http://h4.appcase.cn/) | 标题/品牌/时钟关系、低强度光照、紧凑数字、面板 head/body/foot、场景标签、矩阵与异常区 | 历史参考案例，不是通用外观；页面截图在 references 中，具体提取与转译见 h4-reference.md |
| [EasyV 客户案例](https://easyv.cloud/customer-case?categorie=5&tabIndex=1)、[DataEase V3 模板](https://templates.dataease.cn/?de-version=V3)、[EasyV 素材广场](https://easyv.cloud/market) | 多类构图、标题/面板配方、浅色报表、主题与场景表达 | 33 个原图样本的静态观察，详见 easyv-dataease-research.md；风格命名和代码为本项目转译，未验证平台交互 |
| [EASYV 智慧园区案例](https://easyv.cloud/case-detail/2.html) / [产品介绍](https://easyv.cloud/product-advanced) | 中心场景与数据覆盖层、空间层次、光照氛围 | 参考公开风格；不复制专有素材，不声称集成其引擎 |
| [Grafana 大屏实践](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/) | 问题驱动、认知负担、刷新匹配数据变化、变量复用 | 借鉴方法，不要求部署 Grafana |
| [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) | 配置版本化、可复现变更 | 本技能配置不是 Grafana 配置 |
| [ECharts Dataset](https://echarts.apache.org/handbook/en/concepts/dataset/) | 数据与图形映射分离 | 不把图表 option 当作业务协议 |
| [ECharts Event and Action](https://echarts.apache.org/handbook/en/concepts/event/) | 事件、钻取和动作联动 | 跨组件先转换成业务语义 |
| [ECharts Data Transition](https://echarts.apache.org/handbook/en/how-to/animation/transition/) | 稳定身份与差量更新 | 不强制每次数据刷新执行入场动画 |
| [ECharts Canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/) | 按数据与终端评估渲染器 | 没有通用的性能胜者 |
| [Cube 数据建模](https://docs.cube.dev/reference/data-modeling/cube) | 集中度量、维度与计算口径 | 首版不部署 Cube 或重建计算平台 |
| [GOV.UK 数据可视化](https://brand.design-system.service.gov.uk/data/) | 统计关系选图、准确和一致 | 不照搬政府品牌色 |
| [GOV.UK 图表颜色](https://brand.design-system.service.gov.uk/colour/charts/) | 分类、连续、发散色与多通道表达 | 实际颜色仍由项目与设备决定 |
| [CSS Color 4](https://www.w3.org/TR/css-color-4/) | OKLCH、感知均匀性与色域映射 | token 转为兼容颜色后再用于图表 |
| [WCAG 2.2 暂停/停止/隐藏](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide) | 持续动态及自动更新可控制 | 结合内容和必要性判断，不把所有刷新一律禁用 |
| [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 有意图的构图与视觉实现 | 可选伴随能力，无跨仓库硬依赖 |

检索到社区 `creating-dashboards` 等通用 dashboard 技能，未完成生产接入能力及维护质量核验，不作为模板依赖或质量背书。安装量不能替代协议测试和真实数据核对。

空间扩展依据：[Three.js ExtrudeGeometry](https://threejs.org/docs/pages/ExtrudeGeometry.html)、[OpenLayers GeoJSON](https://openlayers.org/en/latest/examples/geojson.html)、[MapLibre fill-extrusion](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/)、[高德行政区域查询](https://lbs.amap.com/api/webservice/guide/api/district)。2026-10-13 核对并固定模板依赖 Three.js 0.186.1、OpenLayers 10.11.0；MapLibre 作为可选方案，模板未安装。高德支持范围与 key 类型以当前官方说明为准。
