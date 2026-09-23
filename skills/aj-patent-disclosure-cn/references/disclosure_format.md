# 新版专利申请信息及技术交底书

唯一格式依据是用户提供的 [专利申请信息及技术交底书.doc](../assets/templates/专利申请信息及技术交底书.doc)。同名 `.docx` 是用于 Pandoc 和版式回填的转换副本；禁止修改原件，禁止套用旧五问模板或 `cnipa-reference.docx`。模板更新后必须重新转换并更新摘要记录，不能仅改文件名。

## 字段映射

输出保留原模板标题、填写说明和以下栏目原文，顺序由 `scripts/template_contract.py` 定义。模板正文是八行单列表格，保留表格结构、边框、单元格及高亮。不得另增正文标题层级；技术内容内可以使用段内加粗标签、步骤、列表和实际附图。

| 原模板栏目 | 输入字段与填写要求 |
| --- | --- |
| 待申报专利的主题名称 | `title` |
| 申请人以及发明人名称 | `applicant`、`inventors` 分别填写；任何一项未知写“代理确定” |
| 第一，现有技术的名称 | `existing_technology.name`，不得凭空给已有方案命名 |
| 第二，现有技术的来源 | `existing_technology.source`，实际文献或材料来源；检索计划不充当来源 |
| 第三，现有技术的技术方案 | `background` 中除 `limitations` 外的内容，以及 `existing_technology.solution` |
| 第四，现有技术的缺陷/不足 | `background.limitations`、`existing_technology.limitations` |
| 发明人认为要解决的技术问题 | `invention.technical_problem` |
| 发明人认为可实现的技术效果 | `invention.effects`；区分已验证结果与预期效果 |
| 具体技术内容 | 技术领域、术语、保护点、`invention.purpose` 技术目标、方案输入/步骤/输出、实施例、参考资料、替代实现和其他用途 |
| 实现原理 | `invention.principle`；说明技术手段为何解决问题，不以效果口号代替 |
| 附图 | `figures` 的实际图片、图名、标记说明；确实不适用时使用 `drawings_not_applicable` |
| 实验数据 | `verification` 的真实状态、方法、条件、基线、结果及依据；无材料写“代理确定” |
| 特定软件分析结果 | `software_analysis`；没有执行的软件分析不得写成已完成 |
| 专利申报目的，可多选 | `application_purposes`；不使用 `invention.purpose`，不自动选择模板列出的例子 |
| 产品种类、工作内容、所属领域 | `applicant_profile`，可用字符串或包含 `product_types`、`work_content`、`field` 的对象 |

所有末级栏目不得为空。没有材料时填模板指定的“代理确定”，不是“无”、星号或自创占位符；已经明确未做实验或某项不适用时如实说明。不得以占位值冒充事实。已有技术内容不因迁移模板而丢失。部门与身份证号不属于本模板，不输出这些旧行政字段。

## 版式与检查

Word 在原八行单列表格内回填内容，保留转换副本中的原始标题段落、栏目段落、黄色高亮及节设置，填写内容沿用模板 Normal 字体，黑色、单倍行距和零段前后距，避免继承文件中未使用的蓝色 BodyText 样式；原有文档网格保持。空白填写行随内容扩展，不固定原空模板页数。图片与图名合并在不可拆分的同一段落内，保留完整附图及图名，缩放到可打印区域；不得把图片挪到模板外新增章节。

导出前后都运行覆盖校验：检查所有栏目文字与顺序、模板说明、非空字段、已有内容所在栏目及真实图片嵌入。另以原 `.doc` 提取文本验证模板契约，防止生成器与检查器共同偏离源模板。模板兼容不等于技术充分，核心技术链、事实依据和图文一致性继续独立检查；“代理确定”项列入外部质量报告。

示例 JSON 的新字段只演示结构，不得复制成实际申请事实。正式交付前用 Word/LibreOffice 渲染并逐页核对，不仅看 XML。

转换模板示例（在临时目录转换、核对后再替换副本）：

```bash
soffice --headless --convert-to docx --outdir /tmp/patent-template assets/templates/专利申请信息及技术交底书.doc
```

转换后先核对文字、八行单列表格、边框、高亮及页面设置，再将 DOCX 放入资源目录，用 SHA-256 更新 `template_provenance.json` 的 `source_sha256` 和 `reference_sha256`，保留实际转换工具及版本。替换原 `.doc` 而未同步副本会阻止导出，避免继续使用旧模板。
