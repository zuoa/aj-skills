# 数据大屏制作流程

主题与风格确认 → 配色确认 → 布局选择 → 自定义细化（如需）→ 空框架预览确认 → 内容分析 → 整合交付 → 核验修正。

每阶段给出推荐，同时接受手写。用户已经明确指定的内容直接沿用；明确授权助手决定时记录授权范围。未回复不会视为确认。

## 风格、布局和配色

内置中心地图、主图分析、均衡三列、双列值守、四列对比、超宽全景六套结构，独立搭配九套色板与十五套 UI 风格。可直接描述自定义主题、品牌色、列数、比例、中间地图、侧栏和底部区域，由助手转换为配置。

风格包括科技指挥、极光运维、黑金经营、清爽报表、柔和卡片、工业蓝图、实景通透、人文图志、节庆盛典、星轨传播。另增机甲指挥舱、全息反应堆、星穹剧场、鎏金殿堂四套展陈强化风格，带异形 SVG 框、金属/玻璃材质、标题舱、流光、粒子与场景光环。每类有标题、面板、排版、数字和图表规则，三维模型/地球/文化图片按业务另配。见 [风格目录](../../skills/data-screen-builder/references/style-catalog.md) 和 [案例提炼](../../skills/data-screen-builder/references/easyv-dataease-research.md)。

见 [布局目录与自定义示例](../../skills/data-screen-builder/references/layout-catalog.md)。没有地理需求可选择无地图方案。

## 空框架预览

```bash
python3 skills/data-screen-builder/scripts/create_screen.py /path/to/new-screen --style editorial-light --layout analysis-wide --palette mist-indigo --title "经营分析"
cd /path/to/new-screen
npm ci
npm run validate:framework
npm run dev:framework
```

访问 `/?view=framework`。此页只呈现标题、区域边框、结构标签和留白，不加载业务数据、图表或地图。通过“比较方案”独立切换风格、布局与配色，“导出候选配置”下载 JSON。导出不代表确认，也不会自动覆盖文件；确认后由助手核对并写入 `src/config/framework.json`。

自定义不是网页拖拽功能。先在对话中描述，由助手填写 customLayout/customPalette，再用同一页面预览。`panorama-wide` 初建自动采用 3840×1080，其余默认 1920×1080；页面中切换布局只比较结构，不会擅自改变目标屏幕。

## 精致饱满的展示

新增 `luminous-gallery`（琉光展厅），动态比较入口默认采用此方向。曲面玻璃、指标徽记、真实数据摘要、完整构成图明细和建筑概念场景形成层次。摘要从当前结果推导，比例环只用于百分比；建筑只用于明确标记的 mock 展示，正式项目继续使用已配置地图。

同一方向可搭配深海冰蓝、曜黑香槟和夜紫信号。初建示例：`--style luminous-gallery --palette midnight-cyan --layout map-center`。

## 高强度动态样例

四套展陈风格已分别精修：机甲使用装甲内衬、螺钉刻线与机械台座；全息使用折射棱框、悬浮晶核、纵光与反应环；星穹使用大弧光学框、球形星图与轨道；鎏金使用浮雕双镶边、卷草角花、徽章与建筑展台。共用可靠的指标摘要，独立保留材质和构图。见 [精修配方](../../skills/data-screen-builder/references/four-style-refinement.md) 与 [四套对照预览](../../outputs/data-screen-builder/four-style-refinement/index.html)。

可用 `/?view=showcase&style=astral-theater` 直达某风格，追加 `palette=midnight-cyan` 做同色对照。全息、星图和建筑展台为明确标记的 mock 概念示意；正式项目使用原地理资源。

`/?view=showcase` 仅在 mock 模式启用动态比较，可通过“显示设置”切换十五套风格、九套色板、推荐配色和光效强度，支持暂停与关闭。四套展陈风格默认高强度；静态形态与数据在关闭光效后保留。这里的虚构园区是样例，不代替用户项目框架确认。

例如初建：`--style hologram-reactor --palette midnight-cyan --layout map-center`。独立的空框架仍访问 `/?view=framework`；其中可比较异形框/标题/留白并导出 `styleId` 与 `effectIntensity`。

## 填充和交付

空框架确认后提供本地文件，或要求检索生成指标体系，也可结合两者。助手登记来源、时间、单位和口径，再建立 `framework.json.bindings` 的组件 ID → 槽位 ID 映射。完整页复用该框架的标题、画布、位置、风格和配色；少填、重复、地图角色不符都会报错。候选配置中的 bindings 为空，防止换布局后遗留旧映射。

默认 `/` 是历史园区成品示例，bindings 为空时仅用于演示，不是阶段 5 的框架预览，也不是项目已完成。完成内容和映射后 `/` 才作为本项目完整页验收。

`screen-brief.json` 保存阶段和确认依据，`acceptance.md` 保存需求、内容与页面验收证据；创建脚本会复制这两个模板。完整页运行：

```bash
npm run validate
npm test
npm run build:demo
```

交付包括代码、入口、框架与完整页截图、来源清单、指标/API 映射和验收记录。真实接口未接通时明确交付为演示/待接入；检索生成体系不能冒充私有经营数据。

[技能入口](../../skills/data-screen-builder/SKILL.md) · [详细流程](../../skills/data-screen-builder/references/workflow.md) · [验证记录](verification.md)
