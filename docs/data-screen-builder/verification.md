# 琉光展厅与内容层次核验（2026-10-13）

用户反馈强光效已有改善，但还不够精致，展示可以更饱满。本轮增加 `luminous-gallery`，动态样例默认进入此方向，共十五类风格。采用曲面玻璃、细高光与柔和投光；重点补齐指标上下文、图表摘要/分类明细及完整场景，四类夸张方向继续可选。

新增 `MetricMedallion.vue`（百分比环仅接受真实 0–100 百分比）、`PanelSummary.vue`（当前结果的最新点/峰值/有效点数，多系列不合并）、`ExhibitionScene.vue`（统一等距投影的十二栋概念建筑、立面/道路/绿化/区域标签）、`luminous-gallery.css` 与 ECharts rich 配方。最新点按时间字段选择，null 不转为零；构成明细只在非负、最多四类时展示。顶部概览行 144px 在框架与完整页保持一致。

概念建筑只在明确标记的 mock 动态比较入口使用。绑定的正式页面继续渲染已有 geography，未将地理资产替换为虚构建筑。空框架不加载数据摘要、徽记、建筑、图表或 WebGL。

| 核验 | 本轮实际结果 |
| --- | --- |
| 代码与契约 | build:demo、validate:framework、Python validate_screen、skill 格式校验通过；Vitest 69 项、Python 16 项通过 |
| 三套配色 | 深海冰蓝/曜黑香槟/夜紫信号完整页截图，实际测量面板裁切和 head/body/summary/footer 相互关系，通过 |
| 数据细节 | 指标 368、86.4、89,000 来自原查询；用电摘要 639/655/23、构成合计 368 与分类占比从当前结果推导；窗格高度与道路流光无数值语义 |
| 视觉修订 | 首版摘要压缩曲线、构成明细最后项裁切；缩减摘要高度、增加实际绘图区、重设环中心及分类逐行定位，实际复看截图 |
| 联动 | 点击北部智造区后指标 368→132，标签按筛选剩一项，重置恢复；徽记/摘要不拦截操作 |
| 动效 | 实际检查暂停/恢复/off/值守/系统减少动效；off 保留建筑与数值，装饰动画停止 |
| 尺寸 | 另测 1280×720、2560×1080、390×844 无横向溢出；手机重排截图保存 |
| 框架隔离 | 六套空框架比较无图表/徽记/摘要/建筑/WebGL，零业务 API/地理资源/provider/metrics 请求 |
| 正式页面 | 绑定配置选琉光时使用原有地理组件；不出现概念建筑，保持正式资源入口 |
| 动态证据 | 12 帧真实浏览器截图形成 WebP 短循环，完整运动可在本地动态入口观察 |

[三种配色与动态对照](../../outputs/data-screen-builder/refined-gallery/index.html) · [浏览器记录](../../outputs/data-screen-builder/refined-gallery/browser-results.json) · [可复核脚本](../../outputs/data-screen-builder/refined-gallery/browser-verification.mjs)。截图与样例只用于设计评审，未取得用户视觉认可。实际墙屏、长期性能与新的真实 API 接入未执行。本次新增第 13 个技能行为场景作为后续评审输入，未另行执行独立代理行为评测。

---

# 展陈强化光效与异形边框核验（2026-10-13）

用户反馈上一版偏实用、缺乏夸张效果。本轮增加机甲指挥舱、全息反应堆、星穹剧场、鎏金殿堂四套高强度方向，共十四套风格。实现自适应 SVG 多层边框/角件/金属嵌槽、独立题头、路径流光、固定坐标粒子、全屏结构、场景光环与聚光。风格、色板、布局仍独立；四套默认高强度，明确请求极致视觉时在技能中优先推荐这些方向。

`effectIntensity` 在框架中支持 off/low/medium/high 并通过 Schema/TypeScript/Python 校验；空框架可比较并导出，绑定完整页复用配置。`/?view=showcase` 是 mock 专用动态演示入口，可切十四套风格、配色、推荐配色、强度、空间引擎；HTTP 模式不启用该演示分支。暂停装饰与暂停数据分别控制，off 保留静态形态和数据。

| 核验 | 实际结果 |
| --- | --- |
| 代码与配置 | npm validate、build:demo、Python validate_screen、skill-creator quick_validate 通过；Vitest 69 项、Python 16 项通过 |
| 四套成品 | 1920×1080：SVG 渐变实例 ID 唯一，十个面板框与题头可见，指标保留，容器无内容裁切；截图实际复核 |
| 真实动画 | 浏览器测量标题 stroke-dashoffset 随连续动画帧变化；每套存在 55 个持续 CSS 动画实例（图表自身过渡另有短时实例，不用此数量声称性能） |
| 动效控制 | 暂停/恢复、off、值守、系统减少动效实际通过；off 隐藏环境层/场景光环、关闭辉光，数据仍可读 |
| 数据联动 | 装饰不截获交互；区域筛选时入驻指标从 368 更新为 132，重置正常 |
| 结构组合 | 四套 × 六布局共 24 个空框架检查通过，无业务 API/GeoJSON/provider/metrics 加载，无图表或 WebGL；导出保留 effectIntensity 且 bindings 为空 |
| 尺寸 | 每套另测 1280×720、2560×1080、390×844，无横向溢出；窄屏实际查看并调整场景环的位置 |
| 视觉修订 | 初版中央光环被裁、鎏金角花侵入标签附近；调整光环与角件尺寸，复看截图；移动视图对标题换行和光环位置再调整 |
| 动态证据 | 星穹剧场 16 帧真实浏览器截图生成 WebP 短循环；可暂停，本地对照页另提供完整动态入口 |

[四套效果与动态实录](../../outputs/data-screen-builder/showcase-effects/index.html) · [浏览器检查记录](../../outputs/data-screen-builder/showcase-effects/browser-results.json) · [可复核脚本](../../outputs/data-screen-builder/showcase-effects/browser-verification.mjs)。同一虚构园区只是视觉比较数据，装饰光环/粒子不代表真实业务流向或地理。真实墙屏、长期运行和硬件帧率未测量，未取得用户视觉认可。模型层沿用已有空间组件，本轮重点为 UI 形态/材质/光效系统。

---

# 多风格提炼与实现核验（2026-10-13）

本次在原有制作流程上扩展 UI 风格。读取用户指定的 EasyV 客户案例、DataEase V3 模板市场及 EasyV 素材广场，实际查看 33 个静态原图样本；[来源与观察](../../skills/data-screen-builder/references/easyv-dataease-research.md) 区分直接观察、本项目转译和未验证内容。

新增 10 套独立 `styleId`、6 套色板（共 9 套），复用 6 套布局。风格选择同步到初建脚本、空框架预览、候选导出、Schema/TypeScript/Python 校验、完整页及主题确认记录。标题、面板形态、数字和图表线宽/柱宽/面积填充共用规则；旧 `visualStyle` 保留为兼容入口。自定义风格允许扩展 CSS/组件，实景/地球/工业模型/文化素材仍是按项目配置的资产条件。

| 核验 | 实际结果与证据 |
| --- | --- |
| Skill 格式与本地引用 | skill-creator quick_validate 通过；本地 Markdown 引用、十套 CSS 选择器和推荐色板引用完整 |
| 配置与绑定 | npm validate:framework / validate、Python validate_screen 通过 |
| TypeScript 与构建 | npm build:demo 通过；构建仍提示既有 Three.js/ECharts chunk 大小，未在本次执行性能或生产 API 验收 |
| 自动测试 | Vitest 68 项、Python 16 项通过；包含 540 种风格/布局/色板独立解析、旧配置兼容、自定义/未知选择与初建脚本诊断 |
| 浏览器切换 | Chromium：90 次风格/配色切换、60 种风格/布局几何、候选导出保留 styleId；风格切换不改变槽位或配色 |
| 空框架隔离 | 无 chart/canvas/业务组件，无 API、GeoJSON、业务 provider 或 metrics 请求；浏览器以减少动效环境运行 |
| 完整页 | 单独复制的验证项目：十套风格复用同一批明确标记的虚构园区指标、10 个绑定槽位和框架配置，数值可见、无页面异常 |
| 目标尺寸 | 1920×1080 完整截图；1280×720 与 390×844 的十套空框架无横向溢出；完整页窄屏另保存截图。未宣称重测全部历史尺寸或实体墙屏 |
| 色彩 | 9 套色板的 text/muted/accent 在基础 surface 上的 sRGB 对比均至少 4.5:1；半透明覆盖层、真实照片/场景和实际设备需项目内另核对 |
| 视觉复核 | 同配色/同布局空框架与推荐配色完整页截图实际查看，确认标题、线框、圆角、表面、图表规则有差异。未取得用户视觉认可 |

[十类风格对照页](../../outputs/data-screen-builder/style-research/index.html) 支持切换推荐配色完整示例/同配色空框架、放大截图并查看来源拼图；对照页切换、放大与窄屏实际验证通过。[浏览器记录](../../outputs/data-screen-builder/style-research/browser-results.json) 与 [33 个来源清单](../../outputs/data-screen-builder/style-research/manifest.json) 保留本地证据，调研图片不随技能模板分发。完整示例统一使用虚构园区地图以比较 UI 形态，不表示实景、地球或文化主视觉已建成。

以下保留此前各轮核验记录，历史计数/截图不作为本轮新增功能已执行的证据。

---

# 数据大屏流程重构与验证

日期：2026-10-13。范围：八阶段交互流程、独立布局/配色、无内容框架预览及完整页复用。环境：macOS、Node 25.2.1、Python 3.12.10、Chromium（完整页三维使用软件渲染）。

## 本次变化

[入口](../../skills/data-screen-builder/SKILL.md) 按主题、配色、布局、自定义、空框架确认、内容分析、整合、核验组织；已指定决定复用，明确代决记录 delegated，未回复不当作确认。新增阶段记录和验收模板，支持变更回退。

布局提供中心地图、主图分析、均衡三列、双列值守、四列对比、超宽全景六套结构；色板独立提供暖铜、雾白、墨绿，均支持手动配置。空框架单独加载，不引用指标、provider 或地图模块；候选导出不自动写文件、不自动确认。完整页通过一对一槽位映射复用框架，历史 designs.json 不覆盖新流程。

## 已执行与证据

| 检查 | 结果与范围 |
| --- | --- |
| Skill 与文档 | quick_validate.py 通过；入口与相关设计/接入/验收指南同步；详细使用见 [README](README.md) |
| 配置 | Node 的空框架/完整页校验通过；Python 的空框架和绑定项目校验通过；使用同一结构 JSON Schema |
| 前端测试 | 65 项通过；新增 19 项覆盖 18 种布局/配色组合、自定义、非法几何、未知选择与缺失/重复/地图角色/未填槽位 |
| Python 测试 | 16 项通过；包含创建选项、复制记录模板、无 metrics 文件时的空框架校验、重叠与映射诊断 |
| 构建与复制 | 新建 /tmp/data-screen-workflow-final-20261013；npm ci --offline 安装 117 包；配置、65 项测试、demo 及 HTTP 生产模式的类型检查/构建通过 |
| 浏览器空框架 | 18 种独立组合切换；6 布局 × 7 尺寸 = 42 个几何快照；390×844 重排；候选导出保留选择、清空旧 bindings、无确认状态；零业务/地图请求、无 page error |
| 几何 | 1280×720、1366×768、1920×1080、2560×1440、3840×2160、2560×1080、1024×768；标题/动作与槽位/标签实测包含、分离、裁切通过 [几何记录](../../outputs/data-screen-builder/workflow/geometry.json) |
| 自定义 | 浏览器验证 7:5 两列无地图与自定义墨绿色板，没有业务/地图加载；单行两列配置在空框架与完整页都填满可用高度，修正 repeat(0) 导致的无效网格定义，见 [单行记录](../../outputs/data-screen-builder/workflow/single-row-results.json) |
| 完整页复用 | 浏览器验证自定义主题标题、雾白色板与全部 10 个槽位；旧方案控制不覆盖框架；区域筛选 KPI 368 → 132，未改变查询协议 |
| 首轮行为对比 | 新/旧各执行两用例：新建主题确认、自定义布局续接。新版先确认主题且保留手写；两版都能复用已确认主题/配色。仅四次首轮模拟，不是端到端或统计稳定性证明 |

空框架截图：[主图分析](../../outputs/data-screen-builder/workflow/analysis-wide.png)、[中心地图](../../outputs/data-screen-builder/workflow/map-center.png)、[自定义两列](../../outputs/data-screen-builder/workflow/custom.png)、[手机](../../outputs/data-screen-builder/workflow/mobile.png)。[框架复用后的完整示例](../../outputs/data-screen-builder/workflow/final-bound.png) 仍为明确标记的虚构园区数据，不是用户业务交付。以上实际同尺寸查看，框架仅有结构标签与留白。

[行为对比审阅页](../../outputs/data-screen-builder/workflow/eval-review.html) 可查看新版/旧版回复和逐项判断。耗时和 Token 未采集，聚合工具中零值为缺失占位，不用于效率比较。注册场景扩充到 12 个，只有两个首轮场景实际执行，其余未执行。

## 限制

真实生产 API、真实本地业务文件分析、在线检索与公开数值核对、多轮真人确认、实体墙屏及长期 GPU/内存运行：not-run。本次核验的是技能流程和模板能力，不代表用户已经确认主题、色板或框架。构建仍提示完整页/三维 chunk 较大，需按实际硬件评估。

自定义通过交互引导后写配置，不含拖拽编辑器；当前槽位为不重叠的矩形，精确任意比例和叠层布局需要扩展后再验收。

---

以下是此前空间扩展的验证记录，用于保留已有能力与限制，不作为本次全部重新执行的结论。

# 历史：空间渲染扩展验证

日期：2026-10-13。对象：`skills/data-screen-builder` 的内容方案与空间渲染扩展。环境：macOS、Node 25.2.1、Python 3.12.10、Chromium（WebGL 验收使用软件渲染）。固定指标协议 v1 与已有数据调度继续复用；h4 是参考吸收案例，布局、配色与中心内容由新任务决定。

## 最新交付

- [技能入口](../../skills/data-screen-builder/SKILL.md)、[按内容确定设计](../../skills/data-screen-builder/references/content-driven-design.md)：讨论业务目的、布局与色彩，而不是统一皮肤。
- [设计配置](../../skills/data-screen-builder/assets/vue-screen/src/config/designs.json)：暖铜空间、雾白分析、墨绿监测三个可替换示例，共用同一组指标查询；布局与颜色均可继续扩展。
- [空间指南](../../skills/data-screen-builder/references/spatial-rendering.md)：Three.js 拉升/Bloom/同相机标签，OpenLayers 地图与可选 XYZ 底图，SVG 边界降级；自定义 GeoJSON、道路/水系/点位/照片资源层与坐标声明。
- [高德导入](../../skills/data-screen-builder/scripts/fetch_district_geojson.py)：服务端环境 Key 查询，或读取保存的 API 响应；明确 GCJ-02，按 adcode 选择，输出 Polygon/MultiPolygon 与孔洞。
- [指标契约](../../skills/data-screen-builder/references/metric-contract.md)、[接入说明](../../skills/data-screen-builder/references/integration.md)：统一结果、HTTP adapter、服务端鉴权和业务口径映射。

最新本地预览：[暖色三维](../../outputs/data-screen-builder/preview-v4-spatial.png)、[浅色分析与二维地图](../../outputs/data-screen-builder/preview-v4-analysis.png)、[墨绿三维](../../outputs/data-screen-builder/preview-v4-ecology.png)、[720p](../../outputs/data-screen-builder/preview-v4-720.png)、[手机重排](../../outputs/data-screen-builder/preview-v4-mobile.png)。[实测几何](../../outputs/data-screen-builder/visual-geometry-v4.json) 保存 20 个视口记录。截图为本地验证产物，不随 skill 分发；历史参考截图单独保存在 references/visual-baselines。

## 本次已执行

| 检查 | 结果与证据 |
| --- | --- |
| Skill 校验 | quick_validate.py 通过；新增参考可从入口发现；不再要求默认实现 h4 |
| 配置 | Node 与 Python schema/语义校验通过；Node 另检查三个方案的绑定和布局；检查底图/附加层与边界的坐标一致性 |
| Vitest | 46 项通过：原有协议/调度 18 项、分辨率适配 14 项、空间数据及设计解耦 14 项 |
| Python | 14 项通过：复制/契约/几何 6 项，高德转换与 CLI 8 项（多地块/孔洞、闭环、同名选择、无街道边界、无 Key、异常、离线执行及拒绝隐式覆盖） |
| 新项目复制 | create_screen.py 生成 /tmp/data-screen-spatial-starter-20261013；npm ci --offline 安装 117 个包；校验、46 项测试、demo 类型检查/构建通过 |
| 构建 | 当前模板 HTTP 类型检查/构建通过；独立复制目录的最新 demo 构建通过；三维和 OpenLayers 分别按需拆包 |
| 分辨率与几何 | 暖色三维与浅色二维各测 1280×720、1366×768、1920×1080、2560×1440、3840×2160、2560×1080、1280×1024、1024×768、3440×1440、1920×900；合计 20 个快照，经 check_visual_geometry.py 检查包含、分离、裁切与刻度/图例重叠通过；390×844 无横向溢出 |
| 渲染与联动 | Three.js/OpenLayers/SVG 三种引擎及三套内容方案切换；Three 在缩放后的 720p 下鼠标拾取与 HTML 标签均选择正确区域，OpenLayers 点击选择正确；KPI 368 → 132 → 重置 368；无 page error |
| 控制与卸载 | 数据与光效分别暂停/恢复，值守减少动效，详情不撑大画布；引擎切换后只有当前视图，卸载代码释放 RAF、controls、几何/材质、后处理、WebGL 上下文和地图 target；未做长期内存监测 |
| 冷缓存首次切换 | 独立复制目录以 --force 启动开发服务，完整交互流程通过；断言在主动故障重载前只有首次导航，首次二维/三维切换不触发页面重载；修正 Vite 延迟发现依赖造成的方案重置 |
| 资源失败 | 浏览器拦截边界返回 404，面板显示错误、业务 KPI 保留，重试恢复；道路返回 503 显示缺层提示，三维边界继续可读；恢复资源后正常渲染 |

2026-10-12 的 HTTP fixture 基线曾实际验证 POST、10 组件共用 8 个查询、503 保留最后成功值及恢复、无 mock 回退。本次没有实际生产接口，不能将该历史测试视为生产验收。

## 视觉评议与限制

实际同尺寸查看三个方案，修正了空余布局行压缩热力图、刻度间距、三维投影下标签靠近和按钮前景/背景相同的问题。当前暖色预览呈现面、厚度、Bloom 边缘、道路、水系和服务站标签；浅色方案把空间视图移到左侧并采用二维图，证明布局与配色可独立于数据更换。

示例几何、道路、水系、点位均为虚构资源，不能当作实际行政边界。与用户参考图仍有真实卫星影像、精细道路纹理、实际机构照片和空间细节的差别；这些需要项目资源，不能从边界文件自动生成。Three.js 当前未实现影像铺面，OpenLayers 已提供可选底图入口。MapLibre 是文档中的可选引擎，未安装或实现。

真实高德 Key 查询、生产 API、指标口径核对、私网鉴权、真实边界与底图点位核对：not-run。高德转换和 CLI 使用脱敏离线响应测试。用户视觉认可、实体墙屏观看距离、长时间运行和目标 GPU 性能：not-run。自动几何通过不能证明审美达到用户要求。

主要 JS chunk 约 947 KB（gzip 318 KB），Three.js 约 616 KB（gzip 156 KB），OpenLayers 约 336 KB（gzip 97 KB）；构建仍有大 chunk 提示，尚未评估目标设备性能预算。evals/evals.json 包含七个真实任务案例，独立模型前向评估未执行。

## 使用

```bash
python3 skills/data-screen-builder/scripts/create_screen.py /path/to/new-screen
cd /path/to/new-screen
npm ci
npm run dev
```

预览中展开“显示设置”可切换内容方案及空间视图。项目定稿后可只保留业务需要的方案和控制项。生产设置 HTTP provider，并按指南接入真实指标、边界和资源；高德服务端 Key 不进入 VITE_* 或浏览器 bundle。
