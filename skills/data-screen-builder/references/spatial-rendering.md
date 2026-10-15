# 三维辖区与地图渲染

## 根据主视图选择引擎

| 需求 | 实现 | 注意点 |
| --- | --- | --- |
| 区域拉升、发光轮廓、侧壁、定制灯光/材质、模型 | Three.js | GeoJSON Polygon/MultiPolygon → Shape/holes → ExtrudeGeometry；标签来自同一相机投影，不能独立百分比定位 |
| 二维辖区、瓦片、点位、选择/缩放、空间图层 | OpenLayers | GeoJSON + VectorLayer；显式 dataProjection/featureProjection；瓦片来自可用配置 |
| 矢量瓦片、倾斜地图、楼宇拉升 | MapLibre GL JS | 可以使用 fill-extrusion 或自定义 Three 图层；只在选择后引入依赖 |
| 轻量示意，无需真实三维 | SVG | 保留为无 WebGL 时的明确降级或简单空间展示 |

OpenStreetMap 是地理数据与地图生态，不是与 Three.js 对等的渲染器。用户说 openmap 时结合需求判断是 OSM 底图还是 MapLibre 等引擎；可先采用 OpenLayers 渲染自有 GeoJSON，不因名称歧义阻塞其他工作。

## 将用户提供的立体辖区图拆层

暗色上下文底图 → 顶部辖区面 → 挤出侧壁 → 发光轮廓 → 道路/水系纹理 → 机构/业务点位 → 照片或说明标签。模板实现面、侧壁、Bloom 发光轮廓、指标标签和可配置的道路/水系/点位层；真实道路、卫星影像、照片和机构点位必须使用真实资源，不能从行政边界推导或编造。内置边界、网格路网和湖面均为明确标注的虚构演示。

几何拉升是展示厚度，不自动表示某个数值。需要高度编码时先说明单位、比例尺和零点。光效颜色从内容方案获取，不能将所有辖区默认为橙色，也不能将所有中心模块默认为地图。

## 边界来源与坐标

支持用户提供的 GeoJSON 文件/同源地址，记录来源、获取时间、区域 ID、名称字段和坐标系统。当前基础支持 Polygon/MultiPolygon、内环孔洞与多个离散部分；检查闭环、有限坐标、ID 唯一和可用面积。边界只是范围，不含路网和兴趣点。

高德通过 Web 服务行政区域查询获取：`GET https://restapi.amap.com/v3/config/district`，参数 `keywords`（建议行政区 adcode）、`subdistrict=0`、`extensions=all`、服务端 key。`all` 返回当前查询对象的 polyline，不同时返回子级边界；多地块以 `|` 分隔。街道/乡镇边界不可由该接口取得，使用自定义边界文件或其他适用来源，不能承诺任何辖区都能搜到。[官方说明](https://lbs.amap.com/api/webservice/guide/api/district)

使用 `scripts/fetch_district_geojson.py` 在线查询或从保存的响应离线导入；key 从环境读取，错误不打印完整请求 URL。返回同名候选时要求用 adcode 明确选择，不自动取第一个。不提供真实 key 时用脱敏响应 fixture 验证转换，真实调用记未执行。

```bash
# 在服务端环境设置 AMAP_WEB_SERVICE_KEY 后执行，Key 不写入命令或前端。
python3 <skill-path>/scripts/fetch_district_geojson.py --keywords 310115 --adcode 310115 --output ./public/pudong.geo.json
# 或使用已保存的响应，无须 Key：
python3 <skill-path>/scripts/fetch_district_geojson.py --keywords 310115 --response-json ./district-response.json --output ./public/pudong.geo.json
```

每次查询只导入所选对象；多辖区需分别获取并合并为 FeatureCollection，保留各自 adcode。模板业务维度值也必须使用这些 adcode，不能继续使用演示的 north/east 等 ID。

高德边界按 GCJ-02 数据处理，在导出元数据中明确标注；不能将其改名为 WGS84。标准 GeoJSON 通常采用 WGS84，经纬度数组相同不代表坐标一致。高德边界与 WGS84/OSM 底图混用前必须显式转换并核对，不由“转为 Web Mercator”解决偏移。模板无底图时可以独立展示 GCJ-02；配置底图时要求坐标体系一致。转换方式与数据使用范围按实际服务文档核对。

## 组件与生命周期

`binding.geography` 配置 renderer、GeoJSON source、coordinateSystem、idProperty/nameProperty、depth；指标结果按 ID 关联，不按显示名称猜测。可选 `basemap` 是 OpenLayers XYZ 瓦片入口，必须声明 URL、attribution 与 coordinateSystem；Three.js 当前未实现影像铺面，项目需要时增加同投影纹理或选择地图引擎承载三维层。生产 tile key 使用合适的受限客户端 key 或服务端网关，不把 Web 服务私密 key 放入 bundle。

```json
{
  "renderer": "three",
  "source": "pudong.geo.json",
  "coordinateSystem": "GCJ02",
  "idProperty": "adcode",
  "nameProperty": "name",
  "depth": 5,
  "overlays": [
    { "kind": "roads", "source": "roads.geo.json", "coordinateSystem": "GCJ02" },
    { "kind": "water", "source": "water.geo.json", "coordinateSystem": "GCJ02" },
    { "kind": "poi", "source": "institutions.geo.json", "coordinateSystem": "GCJ02", "nameProperty": "name", "imageProperty": "photo" }
  ]
}
```

roads 接收 LineString/MultiLineString，water 接收 Polygon/MultiPolygon，poi 接收 Point。三个层采用辖区的同一投影；道路必须已裁到需要显示的范围，模板不会替资源服务执行空间裁剪。Three.js 可显示点位照片标签，OpenLayers 显示点位文字；轻量 SVG 降级只画边界及指标名称，不渲染附加层。图层失败时保留可用边界并显示缺层提示。

引擎按需加载；每个视图管理 ResizeObserver、相机/地图尺寸和渲染循环。暂停/减少动效停止装饰动画，交互后仍可更新画面；离开时释放几何、材质、纹理、renderer、地图 target、事件和观察器。WebGL 不可用时显示清楚的原因并保留可读数据或二维降级，不能伪称三维渲染成功。

Three.js 在局部平面坐标渲染辖区，适合城市尺度的视觉展示；跨日期变更线、极区或大范围精确分析使用适用地图投影/地球引擎，不硬套局部投影。标签、拾取与指标必须共享坐标和稳定 ID。

## 验收

同一 GeoJSON 在二维/三维中范围、孔洞、离散部分和标签一致；主题/布局切换不改变数据查询；容器缩放后选择正确；网络异常与空边界明确显示；图层、坐标、数据来源可追溯；卸载资源释放。真实辖区和底图必须用已知点位核对，不把示例边界当作实际业务辖区。

参考：[Three.js ExtrudeGeometry](https://threejs.org/docs/pages/ExtrudeGeometry.html)、[OpenLayers GeoJSON](https://openlayers.org/en/latest/examples/geojson.html)、[MapLibre 三维楼宇](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/)。
