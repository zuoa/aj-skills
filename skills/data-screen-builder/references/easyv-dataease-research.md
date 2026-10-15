# EasyV / DataEase 视觉提炼记录

观察日期：2026-10-13。用户给的三个入口：[EasyV 客户案例](https://easyv.cloud/customer-case?categorie=5&tabIndex=1)、[DataEase V3 模板市场](https://templates.dataease.cn/?de-version=V3)、[EasyV 素材广场](https://easyv.cloud/market)。

本次读取入口及其公开列表，在原图中观察 12 个 EasyV 案例、12 个 DataEase 模板、6 个 EasyV 应用模板和 3 个标题素材。不是全站扫描；EasyV 参数 `categorie=5` 对应能源，本次同时采样其他行业以避免只提炼能源大屏。DataEase 列表中有仪表板与数据大屏，两者区分标注；它们是视觉参考，交付仍是现有 Vue 工程。未访问付费资源、未登录、未执行平台内创建/收藏/下载工程。仅核对静态图片，动效、交互、真实接口与平台模板可编辑性未验证。

下列“观察”来自原图；布局占比、字体和 token 是本项目设计选择，没有读取原页面 computed style，不宣称 HEX/字号为平台原值。调研用图片仅保留在本地 `outputs/data-screen-builder/style-research/`，不把完整第三方工程或素材纳入 skill 模板。

## EasyV 客户案例：空间主视觉和业务母题

| 直接来源 | 原图观察 | 转译规则 |
| --- | --- | --- |
| [31 电力营销](https://easyv.cloud/case-detail/31.html) | 黑底、绿色业务带、分位数字、橙金拉升辖区 | 状态条和紧凑指标可归运维；地图材质与 UI 强调色不必同色 |
| [9 智能风电](https://easyv.cloud/case-detail/9.html) | 青色发光边界、地域总览与场站分屏、底部趋势 | 总屏和设备屏分层，地图轮廓而非厚框承担重点 |
| [7 李宁消费者](https://easyv.cloud/case-detail/7.html) | 超宽中国地图、区域点位、两端辅助数据 | 横向空间阅读与密集地理点位，地图比例随业务决定 |
| [12 银行金融](https://easyv.cloud/case-detail/12.html) | 黑金图形、中心焦点、多区比较；展示图带透视 | 吸收材质和层级；准确数据图维持平面坐标，避免透视误差 |
| [78 高速综合管控](https://easyv.cloud/case-detail/78.html) | 绿色线框、地形底图、红色状态带、地图覆盖层 | 常态绿色与异常红分开，直线框和状态条支持值守 |
| [38 机房运维](https://easyv.cloud/case-detail/38.html) | 写实园区、蓝色透明侧栏、空间覆盖标签 | 通透 UI 为场景留视线，需要真实模型/影像资产 |
| [109 园区智慧运营](https://easyv.cloud/case-detail/109.html) | 大面积园区模型、窄侧栏、顶部工具/底部场景切换 | 资产成为主体；模块切换围绕业务，不必摆满图表 |
| [95 地下矿山](https://easyv.cloud/case-detail/95.html) | 地下实景与车辆主体、灰色状态列表、金色题头 | 场景材质与视角本身形成风格；不统一套蓝色沙盘 |
| [97 产线增效](https://easyv.cloud/case-detail/97.html) | 浅灰机械模型、轻蓝标题与局部信息覆盖 | 工业也可浅色；模型/工序逻辑决定空间关系 |
| [34 红色旅游](https://easyv.cloud/case-detail/34.html) | 金色文化题头、红色章节、区域地图、图文弹层 | 章节和地域叙事母题；正文可读性与文化标题分开 |
| [86 融媒体](https://easyv.cloud/case-detail/86.html) | 中心蓝色地球、轨道、两侧业务/传播列表 | 网络传播适合轨道视觉；需要独立地球/关系组件 |
| [1 福州政务](https://easyv.cloud/case-detail/1.html) | 公共资源画面中心为发光榕树结构，周围统计图 | 地方母题可以替代地图；不要固定所有政府屏为行政地图 |

## DataEase V3：报表、卡片和专题表达

| 模板详情 | 原图观察 | 转译规则 |
| --- | --- | --- |
| [JumpServer 运维审计](https://templates.dataease.cn/store/apps/app-tLcQe) | 深绿、直框、中心趋势、底部审计列表 | 极光运维的直线表面和密度，不以粒子动效提升值守 |
| [冰品进销存](https://templates.dataease.cn/store/apps/app-KFyCW) | 蓝色装饰题头、中心地图、底部明细 | 科技指挥可以服务经营，但先判断地理是否解释问题 |
| [电商运营](https://templates.dataease.cn/store/apps/app-tiSeU) | 浅蓝圆角卡片、宽松图表、左右辅助区 | 柔和卡片与轻量驾驶舱，无须暗色大屏 |
| [年度销售总结（仪表板）](https://templates.dataease.cn/store/apps/app-AzNPt) | 白底、平面图表、上部指标、橙/蓝系列 | 开放报表、目标比较和单位/时间说明 |
| [能源年度业绩（仪表板）](https://templates.dataease.cn/store/apps/app-pTEbE) | 淡紫卡片、顶排业务指标、下排柱图和列表 | 能源也可柔和浅色，不强制科技蓝/绿色 |
| [金融数据](https://templates.dataease.cn/store/apps/app-HqGGR) | 白色分组表面、两层横向业务区、紧凑统计 | 报表分组以业务层级为依据，避免默认三栏地图 |
| [新能源销量](https://templates.dataease.cn/store/apps/app-krnbU) | 浅色蓝白、区域地图、左右排行、底部趋势 | 平面统计地图与清晰对比，不需要三维拉升 |
| [智慧城市](https://templates.dataease.cn/store/apps/app-ghZfR) | 深蓝技术底纹、中心楼宇、发光设备/指标 | 科技指挥/工业蓝图；装饰密度需按观看条件降低 |
| [企业 500 强](https://templates.dataease.cn/store/apps/app-vKXtx) | 深紫金属外框、中心地域、底部总量 | 细金属框和展示层级；不通用采用其业务数值 |
| [春节大数据](https://templates.dataease.cn/store/apps/app-ntHIp) | 红金、飘带/放射、主数字、对称区域 | 节庆母题集中一处，节庆红与告警红分离 |
| [圣诞消费报告](https://templates.dataease.cn/store/apps/app-BsaMQ) | 米白纸面、红绿主题头、平面世界地图与条图 | 专题可以明亮、叙事与统计兼容；节日素材需另行取得 |
| [巴黎奥运战绩](https://templates.dataease.cn/store/apps/app-KgFBX) | 绿色底、金色奖牌主区、比赛列表与趋势 | 事件主视觉由奖牌/赛程决定，不用装饰地图占中心 |

## EasyV 素材广场：整屏到组件的组合规则

实际访问公开列表与预览图。[素材广场](https://easyv.cloud/market) 区分应用模板、设计素材、主题资源；本次没有确认深链详情地址，以下通过名称、资源 ID 和原图链接追溯，避免虚构详情 URL。

| 样本 / 原图 | 观察 | 吸收 |
| --- | --- | --- |
| [企业进销存经营看板 1240](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/qauD8GHWyTmrMjA5AJtyR.jpg) | 浅色分区、彩色图标指标、较少封闭边框 | 左对齐题头、浅色指标带与平面业务图 |
| [集团经营态势驾驶舱 1244](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/jtfC91V_b74fGJtskxWVc.jpg) | 黑金、中央地域、星形成果标记、两侧证据 | 识别点围绕经营成果；金属细线为统一组件语言 |
| [数据中心运维监控平台 1246](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/nBd1auUqHigkjfyzj9kxe.jpg) | 暗绿控制台、中心设备节点、两侧状态和底部趋势 | 告警/设备状态与次级趋势分层，避免装饰压住告警 |
| [电商销售经营分析看板 1247](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/X1K2dGazXH3nNpW45eb82.jpg) | 明亮蓝白、通透圆角、主柱图与侧边排名 | 同布局也能通过表面、题头、图表尺寸改变气质 |
| [港口全球业务可视化系统 1253](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/L8-HVYDByFlBQQcfjcdg5.jpg) | 世界空间、航线、下部统计区、玻璃覆盖层 | 横向全景和航线阅读；实际路线需真实来源 |
| [炼焦煤重介浮选联合全流程 1254](https://assets.easyv.cloud/easyv-market/templates/preview-thumb/dJeSbQpkFlLZmINwwg8Dm.jpg) | 暗色设备组态、工序连线、两侧小图 | 工业主视觉可为流程拓扑，不强制中心地图 |
| [大标题背景框-7 347](https://assets.easyv.cloud/data/assets/8yanp2dly_1630496914061_7rv78fz63.png) | 两端细轨道、中部下凹、蓝色局部光带 | 标题字与框共享宽度约束，轨道需随长标题调整 |
| [大标题背景框-2 344](https://assets.easyv.cloud/data/assets/y74032v0gs_1630496746389_ez153l0vx.png) | 圆滑金色顶部框、中央低凹、细金属高光 | 金属风集中题头和少量细边，不在每张卡叠同素材 |
| [小标题背景框-4 343](https://assets.easyv.cloud/data/assets/nsewy2rdd3_1630579545070_tzgvepuxys.png) | 顶部细线、两端标记、暗色渐隐面 | head/body 分开，标题条重量小于主体内容 |

应用模板与标题素材的精确原图地址保存在本地 `manifest.json`；以上从观察归纳的规则自己以 CSS/SVG 实现。标题背景不是整屏布局，素材图像不是可交互组件，样式模板也不自动提供业务协议或模型。

## 本次形成的工程选择

10 套 `styleId`、9 套 `paletteId`、6 套 `layoutId` 可以独立组合；主视觉由业务与资产选择。空框架支持形态比较和导出，不显示业务内容；成品复用配置。三维实景、工业模型、地球、文化图文等保留为明确的组件/资产扩展条件，不因选了风格就宣称已经实现。

优先实施能跨项目复用的标题、表面、框线、数字和图表 token；场景特色在具体业务项目实现。持续动效只有明确目的才添加，长期值守关闭装饰动画。最终通过同色同布局对照、目标尺寸截图、完整页数据状态和用户评审检验，不能用平台品牌或案例数量作为质量背书。
