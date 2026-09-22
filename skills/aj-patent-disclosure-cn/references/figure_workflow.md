# 附图输入与一次性交付

`generate_docx.py` 自动处理 `figure_plan.drawings`，顺序与 `figures` 一一对应。每个图可单独是架构或流程，支持任意数量的子流程；只画真实存在的关系。需要 Graphviz `dot`，生成黑白 PNG、SVG 及 DOT 源文件。不上传项目技术资料到在线绘图服务。

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

架构图格式：`{"kind":"architecture","components":[{"name":"采集模块100","connections":["处理模块200"]},{"name":"处理模块200","connections":[]}]}`。

节点 id 唯一，每个步骤显式给出 `next`，终点为 `[]`；判断出口有条件标签，循环引用目标节点。节点文字带正文步骤编号。并行节点和汇合关系显式连线，不能串行化。图过长时按正文逻辑拆分子图，勿缩成不可读的小字。

旧版 `figure_plan.components/steps` 仍可用；只有显式 `sequential: true` 才允许从 `invention.solution_steps` 自动导出顺序流程。该标志必须以实际顺序依据为前提。

时序图、数据结构图等可由本地工具绘制；已有图像模式不提供 drawings，给每个 `figures` 条目提供 `file`，支持 PNG/JPEG/SVG，路径相对于输入 JSON。绘制模式中也可先将所有图生成完，再统一使用已有图像模式。不能只给代码而声称已完成图片。

输出放在 `<Word文件名>_figures/`，包含 manifest.json；Markdown 使用相对图像链接，Word 嵌入图片。移动 Markdown 时需带上同名附图目录。不要把 `--demo` 图用作真实交底书附图。

交付前打开全部图，核对文字、连线、条件、循环、终点及正文对应关系；再查看 Word 渲染页，确认图片与图题没有裁切或跨页分离。自动校验无法证明图的技术语义正确。
