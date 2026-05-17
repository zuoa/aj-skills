---
name: aj-copyright-writer
description: 编写中国计算机软件著作权登记申请材料的技能。用户提供软件名称并要求生成软著、软件著作权、计算机软件著作权登记、操作手册、功能模块说明、界面原型图、HTML 原型、原型图片、源代码文档、代码 docx 或完整申请材料时必须使用。按固定流程产出 01.spec/spec.md、02.modules/*.md、03.prototype.html 或 03.prototype.prompt、04.prototype/*.jpg、05.code/01-模块名称.txt 到 10-模块名称.txt、06.manual/*_操作手册.md/.docx、07.code.full/${SOFTWARE_NAME}_代码.docx；原型图默认用 HTML+headless 浏览器截图，必须包含登录页、10 个模块首页，并覆盖 40%-60% 的功能点截图，优先覆盖复杂功能和数据图表功能。
---

# AJ Copyright Writer

面向软件著作权申请材料的全流程写作技能。目标不是生成宣传稿，而是把一个软件名称扩展成可用于申请准备的操作手册、核心代码材料和配套界面图。

## 先读什么

- 执行完整流程前，读 [references/workflow-contract.md](references/workflow-contract.md)。
- 写 `spec`、模块、手册和代码前，读 [references/material-writing-rules.md](references/material-writing-rules.md)。
- 生成界面原型前，读 [references/prototype-ui-style.md](references/prototype-ui-style.md)。
- 生成操作手册前，读 [references/operation-manual-template.md](references/operation-manual-template.md)。
- 操作手册初稿完成后，读 [references/operation-manual-humanizer.md](references/operation-manual-humanizer.md)，做保守的书面专业化去 AI 味处理。
- 写申请材料格式和边界前，读 [references/software-registration-rules.md](references/software-registration-rules.md)。
- 使用国家版权局参考材料时，读 [references/ncac-2025-copyright-policy.md](references/ncac-2025-copyright-policy.md)，并优先联网读取原始 URL。
- HTML 原型截图时，运行 [scripts/screenshot_html_prototypes.py](scripts/screenshot_html_prototypes.py)。
- Gemini 生图时，运行 [scripts/generate_gemini_prototypes.py](scripts/generate_gemini_prototypes.py)。
- 校验编号产物时，运行 [scripts/validate_outputs.py](scripts/validate_outputs.py)。
- 生成 Word 文档时，运行 [scripts/markdown_to_docx.py](scripts/markdown_to_docx.py) 和 [scripts/build_code_docx.py](scripts/build_code_docx.py)。

## Script Directory

`{baseDir}` = 当前 `SKILL.md` 所在目录。执行脚本时先解析 `{baseDir}`，命令中始终使用 `{baseDir}/scripts/...`，不要假设当前工作目录一定是仓库根目录。

## 输入和默认值

必需输入：
- `SOFTWARE_NAME`：软件名称。

可选输入：
- 输出目录：默认创建 `copyright-materials/{software_slug}-{YYYYMMDD-HHMM}/`，所有指定路径都位于该目录内。
- 本地参考目录：默认在输出目录、当前目录和 `~/aj-skills` 中依次查找 `reference/`、`refence/`、`refrence/`。
- 图片风格文件：默认查找 `reference/style.md`、`refence/style.md`、`refrence/style.md`。
- 操作手册模板：默认查找 `reference/操作手册模版.docx`、`refrence/操作手册模版.docx`、`reference/操作手册模板.docx`、`refrence/操作手册模板.docx`。
- 原型图生成模式：默认 `html`，生成 `03.prototype.html/*.html` 后通过 headless 浏览器截图；用户明确要求 AI 生图、Gemini 生图、图片模型、纯 prompt 时才使用 `image` 模式。
- Gemini 配置：默认读取 `~/aj-skills/.env` 中的 `GEMINI_API_KEY`；可用 `GEMINI_IMAGE_MODEL` 或 `GOOGLE_IMAGE_MODEL` 覆盖图片模型。默认模型为 `gemini-3.1-flash-image-preview`，失败时依次尝试 `gemini-3-pro-image-preview`、`gemini-2.5-flash-image` 和 `imagen-4.0-generate-001`。

如果用户只给软件名称，不要反复追问；按软件名称、公开资料和合理行业假设继续，但必须在 `01.spec/spec.md` 标明“公开资料事实”和“基于名称的扩展设定”。

## 输出结构

在输出目录内生成：

```text
01.spec/spec.md
02.modules/01.md ... 10.md
03.prototype.html/00-login.html
03.prototype.html/01.html ... 10.html
03.prototype.html/01-01.html ...        # 默认 html 模式，按需覆盖功能点
03.prototype.style/selection.md
03.prototype.prompt/00-login.md
03.prototype.prompt/01.md ... 10.md
03.prototype.prompt/01-01.md ...        # image 模式，按需覆盖功能点
04.prototype/batch.json
04.prototype/00-login.jpg
04.prototype/01.jpg ... 10.jpg
04.prototype/01-01.jpg ...              # 与功能点原型对应
05.code/01-模块名称.txt ... 10-模块名称.txt
06.manual/${SOFTWARE_NAME}_操作手册.draft.md
06.manual/${SOFTWARE_NAME}_操作手册.md
06.manual/${SOFTWARE_NAME}_操作手册.docx
07.code.full/${SOFTWARE_NAME}_代码.docx
```

可额外生成 `source-log.md`、`qa.md` 等辅助文件，但不要改变上述核心文件名。

## 工作流

### Step 1: 调研并生成 `01.spec/spec.md`

1. 用软件名称联网检索公开资料，优先官网、产品文档、应用商店、公司公告、政府/行业网站和权威媒体。
2. 联网读取国家版权局参考页：`https://www.ncac.gov.cn/xxfb/tzgg/202507/t20250723_923374.html`。如果访问失败，使用内置参考摘要并记录失败原因。
3. 按 [references/software-registration-rules.md](references/software-registration-rules.md) 固定材料边界：申请表、软件鉴别材料、证明文件；源程序和文档普通交存按前后各连续 30 页、不足 60 页全部提交等规则理解。
4. 生成 `01.spec/spec.md`，内容包括：软件定位、目标用户、使用场景、业务流程、角色权限、系统架构、数据对象、功能总览、非功能要求、边界假设和材料写作口径。
5. 对没有公开证据的内容，用“为形成申请材料，本文按以下业务设定扩展”这类表述，不要伪装成已核验事实。
6. 面向交付的规格说明不要出现“模块01”“模块 01”“01模块”“功能点01”等内部编号标签；只能使用真实模块名称、章节号和自然语言说明。

生成后运行：

```bash
python {baseDir}/scripts/validate_outputs.py \
  --spec-md 01.spec/spec.md
```

### Step 2: 生成 10 个核心功能模块

基于 `01.spec/spec.md` 选出最能体现软件独创性和业务复杂度的 10 个模块，生成：

```text
02.modules/01.md
...
02.modules/10.md
```

每个模块必须拆出 `3-5` 个功能点，并写清：模块名称、用户目标、功能点清单、入口页面、关键流程、输入输出、数据字段、业务规则、异常处理、权限控制、界面要点、可生成代码的核心逻辑。

### Step 3: 生成界面原型

遍历 `02.modules/*.md`，挑选复杂功能或最能展示产品能力的界面。优先使用 `html` 模式；只有用户明确要求 AI 生图、Gemini 生图或只要 prompt 时，才使用 `image` 模式。

生成原型前必须先读取 [references/prototype-ui-style.md](references/prototype-ui-style.md)，根据软件名称、`01.spec/spec.md` 和 `02.modules/*.md` 判断软件类型，推荐一个最佳页面风格和 1-2 个备选风格，并让用户确认。用户确认后生成 `03.prototype.style/selection.md`，记录推断类型、推荐理由、用户确认的 `style_id`、本地 `style.md` 是否参与覆盖。除非用户明确要求无人值守生成，否则不要在未确认风格时开始写 HTML 或 prompt。

#### 默认：HTML 原型模式

使用用户确认后的风格，再结合本地 `style.md` 的视觉覆盖，生成自包含 HTML 原型。不同软件类型应使用不同视觉体系，例如监管/预警类可使用 `custom-command-system`，政务审批类可使用 `gov-service-light`，企业运营类可使用 `enterprise-data-station`，医疗科研类可使用 `medical-research-clean`。

```text
03.prototype.html/00-login.html
03.prototype.html/01.html
...
03.prototype.html/10.html
03.prototype.html/01-01.html
03.prototype.html/01-02.html
...
```

每个 HTML 文件必须：
- 包含完整 `<!doctype html>`、内联 CSS、内联 JS 和 mock 数据。
- 在 `<head>` 中写入 `<meta name="prototype-style" content="{confirmed_style_id}">`，取值必须来自 `03.prototype.style/selection.md`。
- 使用中文界面文案、真实业务字段、合理的统计卡片、表格、表单、弹窗或详情区域。
- 固定 16:9、1920x1080 首屏布局，截图时不能出现文字重叠、滚动条遮挡、空白主区域或外部资源加载失败。
- 在 `<head>` 中写入 `<meta name="module" content="02.modules/01.md">`，便于脚本记录 module 映射。
- 不依赖 CDN、远程字体、远程图片或后端接口；所有 mock 数据写在页面内。
- 页面应符合用户确认的风格；若选择 `custom-command-system` 或 `industrial-iot-cockpit`，可参考用户提供示例图的顶部系统标题和导航、技术框架、查询/操作区、主内容表格或业务面板、发光边框和状态芯片；若选择轻量政务、医疗、教育或企业风格，则应按对应行业的清晰、正式、可读风格实现，不要强行套深色指挥舱。

必须额外生成 `00-login.html`，截图为 `04.prototype/00-login.jpg`，只用于手册 `2.1、登录`。不要用任意模块截图替代登录截图。

截图覆盖策略：
- 每个模块必须至少有一个模块首页截图：`01.html` 到 `10.html`。
- 统计全部模块的功能点数量后，额外为其中 `40%-60%` 的功能点生成页面截图，命名为 `模块编号-功能点编号.html`，例如 `03-02.html`。
- 优先覆盖复杂流程、数据录入、图表分析、监控态势、审核处理、告警处置、配置管理、报表导出等更容易体现软件能力的功能点。
- 简单查询、帮助、普通详情查看等低复杂度功能点可以只在模块首页截图中覆盖。

界面文案一致性是硬要求：Step 6 操作手册将提到的菜单、按钮、字段、状态、筛选条件和提示语，必须在本步骤生成的 HTML 页面中真实可见。若页面中没有「新增」「保存」「导出」「审核」等按钮，就不要在操作手册中写用户点击这些按钮；应先补齐原型页面，再写手册。

#### 可选：Gemini 生图模式

使用用户确认后的风格，再结合本地 `style.md` 的视觉覆盖生成：

```text
03.prototype.prompt/00-login.md
03.prototype.prompt/01.md
...
03.prototype.prompt/10.md
03.prototype.prompt/01-01.md
...
```

每个 prompt 都要固定 16:9、1920x1080、中文界面、真实业务数据、清晰层级、无重叠文字、可辨认控件和页面状态。prompt 必须明确写入用户确认的 `style_id`、风格名称和视觉要求，避免普通后台管理界面。编号要与后续图片和手册引用保持一致。必须额外生成 `00-login.md`，并要求生成真实登录页面，不得用模块首页代替。功能点截图覆盖同样遵循 `40%-60%` 规则。

### Step 4: 生成原型图片

默认运行 HTML 截图模式：

```bash
python {baseDir}/scripts/validate_outputs.py \
  --module-dir 02.modules \
  --style-selection 03.prototype.style/selection.md \
  --html-dir 03.prototype.html

python {baseDir}/scripts/screenshot_html_prototypes.py \
  --html-dir 03.prototype.html \
  --output-dir 04.prototype \
  --module-dir 02.modules \
  --batch-file 04.prototype/batch.json \
  --viewport 1920x1080

python {baseDir}/scripts/validate_outputs.py \
  --style-selection 03.prototype.style/selection.md \
  --html-dir 03.prototype.html \
  --prototype-dir 04.prototype \
  --batch-file 04.prototype/batch.json
```

HTML 截图模式依赖 Playwright：

```bash
pip install playwright pillow
python -m playwright install chromium
```

脚本会先生成 `04.prototype/batch.json`，每个任务包含 `module`、`html`、`output`、`retry`、`status` 和错误信息；重复运行时会跳过 manifest 中已成功且文件仍存在的图片。

可选 Gemini/Google API 生图模式：


```bash
python {baseDir}/scripts/validate_outputs.py \
  --module-dir 02.modules \
  --style-selection 03.prototype.style/selection.md \
  --prompt-dir 03.prototype.prompt

python {baseDir}/scripts/generate_gemini_prototypes.py \
  --prompt-dir 03.prototype.prompt \
  --output-dir 04.prototype \
  --module-dir 02.modules \
  --batch-file 04.prototype/batch.json \
  --env ~/aj-skills/.env \
  --size 1920x1080

python {baseDir}/scripts/validate_outputs.py \
  --style-selection 03.prototype.style/selection.md \
  --prototype-dir 04.prototype \
  --batch-file 04.prototype/batch.json
```

Gemini 生图脚本会先生成 `04.prototype/batch.json`，每个任务包含 `module`、`prompt`、`output`、`retry`、`status` 和错误信息。两种模式最终生成结果都必须是：

```text
04.prototype/00-login.jpg
04.prototype/01.jpg
...
04.prototype/10.jpg
04.prototype/01-01.jpg
...
```

若缺少 `GEMINI_API_KEY`、Playwright、浏览器依赖或接口报错，先明确阻塞点，不要用空白占位图冒充生成结果。

### Step 5: 生成核心业务代码

对每个模块生成一个代码文件：

```text
05.code/01-模块名称.txt
...
05.code/10-模块名称.txt
```

每个文件包含：
- Java 后端核心业务类、DTO 或控制器片段。
- React 前端核心页面或组件片段。
- 适量中文注释。
- 具体业务逻辑、校验、状态流转、异常处理和数据转换。

代码要像项目中的人工业务代码：不过度分层，不堆模式名，不只写空壳接口，不使用完全相同的模板反复复制。每个代码文件控制在 `120-260` 行；文件名必须使用 `编号-模块名称.txt`，例如 `01-用户权限管理.txt`，不要只命名为 `01.txt`。

### Step 6: 生成 Markdown 操作手册

基于 `02.modules/*.md` 改写成人工操作说明，先生成初稿，再做保守去 AI 味处理后生成最终稿：

```text
06.manual/${SOFTWARE_NAME}_操作手册.draft.md
06.manual/${SOFTWARE_NAME}_操作手册.md
```

手册必须穿插对应图片：

```markdown
![图1 登录页面](../04.prototype/00-login.jpg)
![图2 模块名称](../04.prototype/01.jpg)
![图3 功能点名称](../04.prototype/01-01.jpg)
```

手册口吻面向最终用户，按 [references/operation-manual-template.md](references/operation-manual-template.md) 的政企交付文档结构组织，但正文不要写成模板填空。每个功能点用自然段融合功能用途、操作路径、字段含义、按钮作用、系统反馈和异常处理，不要把需求分析、数据库字段和代码实现原样搬进去。插图说明写在图片 alt 文本里，转换 Word 时会作为图片下方居中的图注。手册中提到的按钮、字段和提示文字必须能在对应截图中找到，否则先回到 Step 3 修改原型页面。

手册是交付给最终用户和登记材料审查人员阅读的文档，不允许出现“模块01”“模块 01”“01模块”“功能点01”这类内部文件编号或标记说明。章节标题应写成 `### 2.2、用户权限管理`，不要写成 `### 2.2、模块01 用户权限管理`；正文也应写“用户在左侧导航栏点击「用户权限管理」”，不要写“进入模块01”。

操作说明不能只写简单点击步骤，也不要在正文中出现 `页面内容说明：`、`页面区域说明：`、`功能说明：`、`操作前提：`、`字段说明：`、`按钮说明：`、`操作步骤：`、`操作过程：`、`预期结果：`、`异常提示：` 这类硬性标签。写作时把这些内容合并成 2-4 个连贯段落：先说明用户从哪里进入、页面展示哪些业务区域和关键字段，再说明用户如何筛选、录入、点击按钮或查看结果，最后自然交代系统如何校验、成功后如何提示和刷新，以及必填缺失、重复数据、权限不足、无查询结果等情况如何处理。

正文不要大量使用 `1、2、3、` 或 `a）、b）、c）` 列表。章节标题保留 `1、`、`1.1、`、`2.2.1、` 这类层级编号即可，功能说明正文优先使用自然段，必要时才使用少量无序短句。

初稿完成后，读取 [references/operation-manual-humanizer.md](references/operation-manual-humanizer.md)，对 `06.manual/${SOFTWARE_NAME}_操作手册.draft.md` 做一次保守的书面专业化去 AI 味处理，并输出最终 `06.manual/${SOFTWARE_NAME}_操作手册.md`。去 AI 味只能调整句式、连接方式和模板痕迹，不能改变软件名称、模块名称、功能名称、页面按钮、字段、状态标签、提示语、章节标题、图注和图片路径。所有 `「...」` 中的页面文字必须原样保留。

处理完成后运行：

```bash
python {baseDir}/scripts/validate_outputs.py \
  --manual-draft-md "06.manual/${SOFTWARE_NAME}_操作手册.draft.md" \
  --manual-md "06.manual/${SOFTWARE_NAME}_操作手册.md"
```

### Step 7: 生成操作手册 docx

优先使用用户提供的模板。运行：

```bash
python {baseDir}/scripts/validate_outputs.py \
  --manual-draft-md "06.manual/${SOFTWARE_NAME}_操作手册.draft.md" \
  --manual-md "06.manual/${SOFTWARE_NAME}_操作手册.md"

python {baseDir}/scripts/markdown_to_docx.py \
  --input "06.manual/${SOFTWARE_NAME}_操作手册.md" \
  --output "06.manual/${SOFTWARE_NAME}_操作手册.docx" \
  --template "refrence/操作手册模版.docx"

python {baseDir}/scripts/validate_outputs.py \
  --manual-docx "06.manual/${SOFTWARE_NAME}_操作手册.docx"
```

`markdown_to_docx.py` 默认会把 Markdown 列表转为普通文本，避免 Word 自动编号在长手册中累积出大量序号。只有用户明确要求保留 Word 自动列表时，才追加 `--auto-lists`。

模板路径不存在时，自动查找 `reference/`、`refence/`、`refrence/` 下的同名模板；仍找不到时生成无模板 docx 并在最终说明中注明。

### Step 8: 生成代码 docx

将 `05.code/*.txt` 合并为：

```text
07.code.full/${SOFTWARE_NAME}_代码.docx
```

运行：

```bash
python {baseDir}/scripts/validate_outputs.py \
  --code-dir 05.code

python {baseDir}/scripts/build_code_docx.py \
  --code-dir 05.code \
  --output "07.code.full/${SOFTWARE_NAME}_代码.docx" \
  --software-name "${SOFTWARE_NAME}"

python {baseDir}/scripts/validate_outputs.py \
  --code-dir 05.code \
  --code-docx "07.code.full/${SOFTWARE_NAME}_代码.docx"
```

如果使用 `--root` 做整体验证，必须同时传入 `--software-name "${SOFTWARE_NAME}"`，这样脚本会检查 `07.code.full/${SOFTWARE_NAME}_代码.docx`，而不是旧的 `code.docx`。

如果用户提供了代码模板，用 `--template` 指定。代码 docx 顶部只显示软件名称，后面直接跟各模块代码；不要加入“软件源代码文档”“本文档由 05.code 目录下……”这类生成说明或内部解释。代码文档要保留模块编号和代码结构，避免把代码改写成说明文。

## 质量检查

交付前检查：
- 核心文件和目录是否全部存在。
- `02.modules` 是否有 10 个模块文件，`05.code` 是否有 10 个代码文件。
- 原型模式为 `html` 时，`03.prototype.html` 是否有 `00-login.html`、`01.html` 到 `10.html`，并额外覆盖 `40%-60%` 功能点；原型模式为 `image` 时同理检查 `03.prototype.prompt`。
- `04.prototype` 是否有 `00-login.jpg`、`01.jpg` 到 `10.jpg`，并额外包含功能点截图。
- `04.prototype/batch.json` 是否存在，且所有截图任务最终均为 `success`。
- 手册中的图片链接是否都能对应到 `04.prototype/*.jpg`。
- 手册中的按钮、字段和提示语是否能在对应截图中看到。
- 操作手册是否用自然段充分解释页面内容、操作前提、操作过程、预期结果和异常提示，且没有写成固定标签分段。
- 操作手册正文是否避免大量 `1、2、3、` 或 `a）、b）、c）` 列表；编号主要保留在章节标题。
- 操作手册最终稿是否已经按 `operation-manual-humanizer.md` 做过保守去 AI 味，且没有改动专有名称、页面按钮、字段、状态标签、图注和图片路径。
- 规格说明和操作手册是否没有“模块01”“模块 01”“01模块”“功能点01”等内部编号标签。
- 是否已生成 `03.prototype.style/selection.md`，并记录推荐风格、备选风格和用户确认结果。
- 原型截图是否符合用户确认的页面风格，不能是普通后台管理页面，也不能把所有软件都套成同一种深色指挥舱。
- `spec` 是否区分公开事实、推断和扩展设定。
- 代码文件是否使用 `01-模块名称.txt` 命名，是否包含 Java 和 React 两部分，是否有实际业务逻辑，是否控制在 `120-260` 行。
- docx 是否成功生成；能渲染检查时，抽查首页、目录附近、图片页和代码页。

## 交付说明

最终回复只列出输出目录、核心文件、使用的模板或缺失模板、未完成项和验证结果。不要把整份手册或全部代码粘贴到聊天中。
