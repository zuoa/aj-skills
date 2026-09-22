# 附图输入与一次性交付

`generate_docx.py` 自动处理 `figure_plan.drawings`，顺序与 `figures` 一一对应。支持架构、流程和交互时序图；只画真实存在的关系。使用本地 Graphviz（架构/流程为 `dot`，时序为 `neato`），生成黑白 PNG、SVG、PDF、DOT 及可编辑 `.drawio` 副本，无须安装 draw.io 即可导出副本。不上传项目技术资料到在线绘图服务。

## 先选择图种和层级

- 总体架构图表达组成、边界与数据/控制关系；端、边、云及内部子系统使用有依据的分组，不把全部模块排成一条流程。
- 主流程只保留核心步骤、条件和结果；训练/推理、异常恢复或核心模块细节需要时另画子图，通过图号及步骤号与正文对应。
- 多主体交互用时序图，参与者横向排列、消息按实际发生顺序自上而下。不要根据架构连线自动推定消息时序。
- 使用短标签和稳定标记；实现细节写入正文，不能为了短标签删掉决定流程走向的条件。优先黑线白底，颜色不承载必要信息。

样例集见 [figure_gallery.sample.json](../assets/examples/figure_gallery.sample.json)，含架构分组、条件分支、反馈线和消息往返。仅用于演示，不得复制其技术关系到真实案件。

## 流程图

```json
{
  "figure_plan": {
    "drawings": [
      {"kind": "flowchart", "steps": [
        {"id": "S1", "label": "S1 接收输入", "next": ["S2"]},
        {"id": "S2", "label": "S2 校验是否通过", "type": "decision", "next": ["S3", "S4"], "edge_label": {"S3": "是", "S4": "否"}},
        {"id": "S3", "label": "S3 处理并输出", "next": []},
        {"id": "S4", "label": "S4 返回错误", "next": []}
      ]}
    ]
  },
  "figures": [{"num": 1, "caption": "输入校验与处理流程图"}]
}
```

节点类型支持 `process`、`decision`、`start`、`end`、`input`、`output`、`storage` 和 `subprocess`。`ref` 可单列正文已有的部件标记，避免拼在长标签中；脚本不会自行发明编号。

每一步可用 `edge_options` 为指定出口补充布局控制，例如：

```json
{"id":"S5","label":"S5 更新阈值","next":["S2"],
 "edge_label":{"S2":"供后续任务使用"},
 "edge_options":{"S2":{"feedback":true,"tailport":"e","headport":"e"}}}
```

`feedback` 仅解除该边的层级布局约束，不创造反馈语义、不自动改成虚线。必须由真实技术关系确定后填写。

## 架构图与嵌套分组

旧格式继续支持：`{"kind":"architecture","components":[{"name":"采集模块100","connections":["处理模块200"]},{"name":"处理模块200","connections":[]}]}`。

需要分组与连接标签时：

```json
{"kind":"architecture",
 "groups":[{"id":"edge","label":"边缘节点200"},
           {"id":"scheduler","label":"调度子系统","parent":"edge"}],
 "components":[
   {"id":"router","name":"任务分流","ref":"210","group":"scheduler",
    "connections":[{"to":"cache","label":"暂存任务"}]},
   {"id":"cache","name":"任务缓存","ref":"220","type":"storage","group":"edge","connections":[]}
 ]}
```

有 `id` 时连接引用该 id；未提供 id 时继续引用 `name`。分组的 `parent` 可嵌套，节点的 `group` 必须存在，父组不能循环。架构 `type` 用 `process/storage/input/output/subprocess` 表达形状；旧数据的领域类型名称仍按普通模块绘制。

## 布局选择

每幅图可提供：

```json
{"layout":{"direction":"TB","routing":"spline","label_columns":24,
           "nodesep":0.55,"ranksep":0.6,"same_rank":[["S3","S4"]]}}
```

- `direction`：`TB` 自上而下或 `LR` 自左向右；流程默认 TB，架构默认 LR，可按页面比例调整。
- `routing`：默认 `spline`；`polyline` 为折线，`ortho` 为直角线。Graphviz 的直角布局对端口和边标签支持有限，标签使用外部标签，要求精确端口时优先 spline。不要为追求直角而牺牲箭头语义。
- `same_rank`：节点对齐，不代表并行执行。列表里的每个节点必须存在。
- `label_columns`：12–48 的显示列宽，中文按两列计，保留显式换行；不是字号。
- `nodesep/ranksep`：节点/层间距，0.2–2 英寸。增大间距后应重查打印字号，不能靠扩大画布无限疏散。
- 连线支持 `tailport/headport`（n/s/e/w/ne/nw/se/sw）和 `style`（solid/dashed）。同层边指定端口在部分 Graphviz 版本上会产生断箭头，脚本检测到时阻止生成；移除不必要端口或调整对齐后重试。

## 时序图

```json
{"kind":"sequence",
 "participants":[{"id":"edge","label":"边缘节点200"},{"id":"cloud","label":"云端300"}],
 "messages":[{"from":"edge","to":"cloud","label":"上传待复核样本"},
             {"from":"cloud","to":"edge","label":"返回复核结果","style":"dashed"}]}
```

消息顺序严格使用输入数组顺序，不自动添加确认、重试或返回。当前支持不同参与者间的消息；自调用、激活框、嵌套循环/条件片段尚未实现，需用其他本地工具生成后走已有图像模式，不能伪装成普通跨主体消息。

节点 id 唯一，每个步骤显式给出 `next`，终点为 `[]`；判断出口有条件标签，循环引用目标节点。节点文字带正文步骤编号。并行节点和汇合关系显式连线，不能串行化。图过长时按正文逻辑拆分子图，勿缩成不可读的小字。

旧版 `figure_plan.components/steps` 仍可用；只有显式 `sequential: true` 才允许从 `invention.solution_steps` 自动导出顺序流程。该标志必须以实际顺序依据为前提。

复杂 UML、数据结构图等可由本地工具绘制；已有图像模式不提供 drawings，给每个 `figures` 条目提供 `file`，支持 PNG/JPEG/SVG，路径相对于输入 JSON。绘制模式中也可先将所有图生成完，再统一使用已有图像模式。不能只给代码而声称已完成图片。

输出放在 `<Word文件名>_figures/`，包含 manifest.json；Markdown 使用相对图像链接，Word 嵌入图片。移动 Markdown 时需带上同名附图目录。不要把 `--demo` 图用作真实交底书附图。

每张图同时输出 `.layout.json`：打印尺寸、估算最小字号、几何检查结果和未检查项。生成图按最大宽14cm、高18cm等比适配，不放大小图；PNG 为300dpi，SVG/PDF保留矢量。小于7.5pt是本项目可读性提醒阈值，不是法定标准。出现提醒时拆分主/子流程、缩短标签或调整方向后重绘；不得靠增大 PNG 分辨率消除排版问题。

`.drawio` 包含原生节点、连线与嵌套容器，可打开后微调，不是嵌入一张不可编辑图片。它复用 Graphviz 坐标；曲线转折线与标签定位可能不同，不承诺像素一致。修改副本不会自动回写输入 JSON 或刷新 PNG；用本地 draw.io 导出并重新验图后，再走已有图像模式交付，避免重生成覆盖人工调整。

交付前打开全部图，核对文字、连线、条件、循环、终点及正文对应关系；再查看 Word 渲染页，确认图片与图题没有裁切或跨页分离。自动校验无法证明图的技术语义正确。

脚本自动检查节点引用、分组循环、节点框重叠和箭头与线段断开；不会自动确认连线穿框、边标签重叠、缺字、语义与 Word 分页。`.layout.json` 的 `visual_review: required` 不因生成成功改成通过。实际看图发现问题时修改输入并重渲染，保留人工/代理审阅记录；没有 Word 渲染能力时明确说明该项未完成。
