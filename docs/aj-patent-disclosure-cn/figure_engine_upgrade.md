# 附图引擎升级记录

日期：2026-09-22。目标是改善软件类专利附图的结构组织、可读性和可编辑性，不改变原技术内容，也不靠装饰、配色或随机生成图增加“专业感”。

## 借鉴与取舍

- [Claude-Patent-Creator 的 patent-diagram-generator](https://github.com/RobThePCGuy/Claude-Patent-Creator/blob/main/skills/patent-diagram-generator/SKILL.md)：参考图种、部件编号及矢量输出思路；本地不引入其美国申请规则或整个 MCP 系统。
- [Drawio Skill](https://github.com/Agents365-ai/drawio-skill/blob/main/skills/drawio-skill/SKILL.md)：参考原生可编辑节点与连线、保留布局以及渲染后审阅；用标准库独立实现 `.drawio` 导出，不依赖其代码或安装流程。
- [Paper-to-patent 附图指南](https://github.com/snipp-zha/Paper-to-patent-Skill/blob/main/references/patent-figure-guide.md)：参考总图与细节分图、简明节点及正文对应；仅按真实技术关系选择图种。
- 实现参考 [Graphviz JSON 输出格式](https://graphviz.org/docs/outputs/json/) 和 [splines 属性说明](https://graphviz.org/docs/attrs/splines/)。使用布局坐标做打印适配、几何检查及可编辑副本，300dpi 只用于 PNG，SVG/PDF 保留正常物理尺寸。

新增代码均为本地实现，未复制第三方代码、图样或模板。

## 实现

- 新增 `scripts/figure_layout.py`，复用 Graphviz，未增加 Python 包依赖。
- 架构支持独立 id、正文标记、带标签连接、父子分组；流程支持节点形状、对齐、方向、间距与反馈端口。
- 新增时序图，固定参与者列和消息行，严格保持输入消息顺序；不自动补确认消息。
- 保留 DOT、300dpi PNG、SVG/PDF，输出具有原生节点、连线和嵌套容器的 `.drawio`。
- 根据图形宽高生成 `display_width_cm`，不把每幅图强行撑到14cm；现有 DOCX 排版的14×18cm上限继续保留。
- `.layout.json` 保存字号估算、节点框重叠及断箭头检查和未检查项；小于7.5pt提示拆图，该数值是项目选择而非法定标准。

实际看图发现当前 Graphviz 的部分同层端口组合产生断开箭头，补充箭头三角形与末端路径的距离检查，出现此类异常则阻止生成并提示调整端口。视觉审阅仍负责发现连线穿框、标签挤压、缺字和错误技术关系。

## 验证

- 新增9项测试；完整46项回归通过，覆盖三类出图、分组嵌套、消息顺序、可编辑副本引用、异常输入、字号提醒、Word嵌图及尺寸。
- 三张演示 PNG 已逐张打开检查，修正了断箭头、时序生命线绕行及架构标签位置。最终估算最小打印字号分别约8.16pt、9.56pt、11pt；无字号提醒。
- 运行已有示例的 DOCX 导出与内容覆盖校验通过。调用 documents 的 `render_docx.py` 时因本机缺少 `soffice` 失败，所以未完成 Word 实际分页的视觉验收。
- `.drawio` 已校验 XML、原生图元和父子引用，本机无 draw.io，尚未在其编辑器中做视觉验收。副本曲线转折线、标签位置与 Graphviz 图像不承诺像素一致，编辑后需要重新导出检查。
- Skill 结构校验、资源链接和 `git diff --check` 通过。

## 使用与边界

输入示例：[figure_gallery.sample.json](../../skills/aj-patent-disclosure-cn/assets/examples/figure_gallery.sample.json)。完整说明：[figure_workflow.md](../../skills/aj-patent-disclosure-cn/references/figure_workflow.md)。

本轮未实现自动拆图、自调用时序、激活框、循环/条件片段和任意机械制图。复杂图仍可由其他本地工具制作后以 `figures.file` 导入。布局报告始终保留 `visual_review: required`；代理打开图之后的审阅记录单独保存，不把程序运行成功自动写成视觉通过。
