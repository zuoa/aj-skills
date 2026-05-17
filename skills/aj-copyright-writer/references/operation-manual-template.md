# Operation Manual Template

Use this template when generating `06.manual/${SOFTWARE_NAME}_操作手册.md`. The output should read like a formal government or enterprise project delivery document, and should be ready to convert into Word.

## Writing Style

- Use a formal, standardized product manual tone.
- Prefer the pattern: function description → operation path → field explanation → button explanation → user steps.
- Every primary function module must describe purpose, page entry, key indicators, buttons and actual use flow.
- Function sections should not be too short. Explain what the user sees, why the operation matters, what should happen after the operation, and what common exception messages mean.
- Use numbered headings such as `1、`, `1.1、`, `2.2.1、` only for chapters and sections. Avoid repeated numbered lists inside every function; body text should be natural paragraphs.
- Reserve screenshot positions for every main page and important child page using `图X 页面名称`.
- Write for operators, not developers. Avoid database, API and implementation details unless they directly affect user operation.
- Keep module names, button names and field names consistent with `02.modules/*.md`, `03.prototype.html/*.html` or `03.prototype.prompt/*.md`, and screenshots.
- Do not expose internal numbering labels from source files. Avoid wording such as `模块01`, `模块 01`, `01模块`, `功能点01` and `第01功能点`; use the real module/function name with normal chapter numbering.
- Do not use rigid labels such as `页面内容说明：`, `页面区域说明：`, `功能说明：`, `操作前提：`, `字段说明：`, `按钮说明：`, `操作步骤：`, `操作过程：`, `预期结果：` or `异常提示：` in the final manual. These aspects must be blended into regular paragraphs.
- After the draft is complete, apply [operation-manual-humanizer.md](operation-manual-humanizer.md). Keep the tone formal and professional; only reduce repetitive AI-like phrasing and template traces. Do not change any software name, module name, UI label, button, field, status tag, prompt, figure caption or image path.

## Required Structure

```markdown
# {SOFTWARE_NAME} V1.0

## 1、系统阐述

### 1.1、系统说明
[说明系统面向的业务场景、建设目标、核心技术、解决的问题和总体价值。]

### 1.2、主要功能
[按模块列出系统主要功能，每个功能写一段说明。]

### 1.3、目标用户
[说明管理人员、业务人员、技术员、运维人员、科研人员等角色如何使用系统。]

### 1.4、术语定义
[解释系统中的重要业务术语和技术术语。]

### 1.5、软件开发目的
[说明业务价值、管理价值、技术价值和建设必要性。]

## 2、实操指引

### 2.1、登录
[说明登录入口、账号密码填写、验证码或组织选择、点击按钮、登录成功后的页面效果。]

![图1 登录页面](../04.prototype/00-login.jpg)

### 2.2、{一级功能模块名称}
[先用一段话说明该模块的总体作用。]

用户在导航栏进入「{一级功能模块名称}」后，页面上方展示{字段A}、{字段B}、{字段C}等核心指标，便于用户快速判断当前业务状态；页面中部以列表、图表或业务面板展示{数据对象}，右侧或底部展示详情、处理记录和系统提示。用户可根据{筛选条件}缩小范围，再通过页面中的主要按钮完成查询、录入、审核、导出或状态处理。

![图2 {模块首页}](../04.prototype/01.jpg)

#### 2.2.1、{子功能名称}
用户点击功能区的「{子功能名称}」按钮后，系统进入{子功能名称}页面。该页面主要用于{业务作用}，适用于已登录且具备{角色或权限}权限的用户；在操作前，用户需要确认系统中已有可处理的{业务对象}，或已准备好需要录入、核对、审批、导出的业务信息。

进入页面后，顶部显示当前筛选条件、状态标签和常用操作按钮，中部展示{数据对象}列表、统计卡片或趋势图，右侧或底部显示选中记录的详情、处理记录和校验提示。{字段A}用于标识……，{字段B}用于反映……，{字段C}用于判断……，用户可结合这些字段完成核对和筛选。

用户可先按{筛选条件}查询目标数据，再点击「{按钮A}」进行{主要动作}；系统会检查必填项、格式、重复数据和权限范围，校验通过后显示“保存成功”“提交成功”或相应业务提示，并刷新列表、更新状态标签或生成处理记录。需要批量处理时，用户可点击「{按钮B}」按当前筛选条件执行{辅助动作}，完成后可在页面结果区查看导出文件、审批结果、告警处置记录或计算结果。

若用户未填写必填信息、选择了无效数据、权限不足或当前条件下暂无记录，系统会在字段旁、弹窗或页面右上角显示明确提示。用户应根据提示补充信息、调整筛选条件、重新选择记录或联系管理员处理。

![图3 {子功能名称}](../04.prototype/01.jpg)
```

## Section Rules

### 1、系统阐述

`1.1、系统说明` should include:

- Business scenario.
- Construction goal.
- Core technology or architecture in user-facing language.
- Problems solved.
- Overall value.

`1.2、主要功能` should list the 10 modules from `02.modules`, using this format:

```markdown
{模块名称}用于{一段功能说明}。

{模块名称}用于{一段功能说明}。
```

`1.3、目标用户` should describe roles and purposes:

```markdown
管理人员主要用于查看全局数据、审批关键流程并掌握系统运行状态。业务人员主要用于录入、处理、查询和导出日常业务数据。运维人员主要用于维护基础配置、查看运行异常并处理系统告警。
```

`1.4、术语定义` should use concise paragraph entries. Keep entries short, but do not force lettered numbering:

```markdown
{术语}是指{定义}。

{术语}是指{定义}。
```

`1.5、软件开发目的` should cover:

- Why the software was developed.
- What management problem it solves.
- What efficiency, quality or traceability value it creates.
- What technical value it provides.

### 2、实操指引

`2.1、登录` should include:

- Login address or entry.
- Account, password and optional verification input.
- Login button behavior.
- Successful login effect.
- Failed login tips.

For each module section:

- Start with one paragraph explaining the module's overall role.
- When the page has statistics, filters, status tags, list columns or card metrics, explain them in the opening paragraph instead of adding a separate rigid label.
- Add a screenshot caption and image link.
- Expand the module's 3-5 function points as child sections.

For each child function section:

- Use 2-4 natural paragraphs instead of rigid subheadings.
- Blend in where to click, what page opens, what the user sees, which fields matter, which buttons are available, and what business problem the function solves.
- Explain the operation flow in prose: user action, system validation, success feedback, data refresh, status change, file output or processing record.
- Mention common exceptions in the same narrative: missing required fields, duplicate data, insufficient permissions, no query results or network errors.
- Screenshot caption: `图X 子功能名称`.

## Screenshot Rules

- Use increasing figure numbers from `图1`.
- The figure caption is the image alt text and must appear below the image, centered, after Word conversion.
- Every main module should reference one prototype image if available.
- Cover `40%-60%` of all function points with dedicated screenshots, in addition to login and module overview screenshots.
- Prioritize screenshots for complex workflows, data-entry forms, chart/data visualization functions, monitoring/alert pages, audit handling, report export and configuration pages.
- Image markdown must use paths relative to the manual file:

```markdown
![图X 页面名称](../04.prototype/01.jpg)
```

- If a function point has no separate screenshot, reuse the module screenshot and write the caption for the visible area.
- `2.1、登录` must use `../04.prototype/00-login.jpg`; never reuse `01.jpg` or another module screenshot as the login page.
- Any button, field, tab, menu or prompt mentioned in the operation steps must be visible in the referenced screenshot. If it is not visible, revise the prototype first or remove the operation text.

## Module Expansion Pattern

For 10 modules, write:

```markdown
### 2.2、模块一名称
#### 2.2.1、功能点一
#### 2.2.2、功能点二
#### 2.2.3、功能点三

### 2.3、模块二名称
#### 2.3.1、功能点一
#### 2.3.2、功能点二
#### 2.3.3、功能点三
```

Continue until all modules from `02.modules/01.md` to `02.modules/10.md` are covered.

## Language Patterns

Use these phrases:

- `用户在左侧导航栏点击「{模块名称}」，进入{模块名称}页面。`
- `页面上方为条件筛选区，用户可按{字段}进行查询。`
- `页面中部为信息展示区，系统按列表形式展示{数据对象}。`
- `页面右侧展示当前选中记录的详情信息，便于用户核对处理结果。`
- `用户完成填写后，系统会对必填项、格式和重复数据进行校验。`
- `点击「新增」按钮后，系统弹出新增窗口，用户填写必填信息后点击「保存」。`
- `点击「导出」按钮后，系统按照当前筛选条件生成文件。`
- `操作完成后，系统在页面右上角显示处理结果，并刷新列表数据。`
- `若查询条件下暂无数据，系统显示空状态提示，用户可调整筛选条件后重新查询。`

Avoid these patterns:

- Do not say "此处展示截图" without an image or figure number.
- Do not copy module analysis sections such as "代码生成提示" into the manual.
- Do not use developer-only wording such as "调用接口", "写入数据库", "返回 JSON".
- Do not leave generic placeholders like "字段A" in final output; replace them with software-specific fields.
- Do not write internal labels such as "模块01", "模块 01", "01模块", "功能点01" or "第01功能点" in headings, paragraphs, captions or tables.
- Do not write rigid labels such as "页面内容说明：", "页面区域说明：", "功能说明：", "操作前提：", "字段说明：", "按钮说明：", "操作步骤：", "操作过程：", "预期结果：" or "异常提示：".
- Do not fill the body with repeated `1、2、3、` or `a）、b）、c）` lists. Keep numbering mainly in headings and use connected paragraphs for operation details.
