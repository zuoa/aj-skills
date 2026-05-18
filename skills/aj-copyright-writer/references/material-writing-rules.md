# Material Writing Rules

Use these rules when writing the spec, modules, prompts, source-code files and operation manual.

## `01.spec/spec.md`

Recommended structure:

```markdown
# {SOFTWARE_NAME} 软件规格说明

## 1. 编写说明
## 2. 资料来源与事实边界
## 3. 软件概述
## 4. 目标用户与使用场景
## 5. 总体业务流程
## 6. 角色与权限
## 7. 系统架构
## 8. 核心功能总览
## 9. 数据对象与业务口径
## 10. 非功能要求
## 11. 申请材料扩展设定
```

Rules:

- Separate verified public facts from inferred product design.
- Use stable module names that can flow into manual chapters and code files.
- Prefer specific business verbs: submit, review, dispatch, reconcile, archive, export, remind, verify.
- Avoid pure marketing claims such as "industry-leading" unless a cited public source supports them.
- Because this is a user-visible application material, do not write internal labels such as `模块01`, `模块 01`, `01模块` or `功能点01`. Use the real module/function name and normal chapter numbering instead.

## `02.modules/*.md`

Each module file should use:

```markdown
# 01. 模块名称

## 模块定位
## 使用角色
## 功能点清单
## 入口与前置条件
## 主流程
## 输入与输出
## 核心数据
## 业务规则
## 异常与边界
## 权限与审计
## 界面要点
## 代码生成提示
```

Rules:

- Module count is exactly 10.
- Each module must include exactly 3 to 5 function points under `## 功能点清单`.
- Each function point should have a short name and 1 to 2 sentences explaining user action, system behavior and output.
- Select modules that show business complexity, not merely "首页", "设置", "帮助".
- Each module should contain enough logic to generate Java and React code.
- Keep names consistent across all later files.

Function point format:

```markdown
## 功能点清单

1. 功能点名称：说明用户如何触发、系统如何处理、产生什么结果。
2. 功能点名称：说明用户如何触发、系统如何处理、产生什么结果。
3. 功能点名称：说明用户如何触发、系统如何处理、产生什么结果。
```

## `03.prototype.style/selection.md`

Before writing prototype HTML or image prompts, read [prototype-ui-style.md](prototype-ui-style.md), recommend the best style for the software type, ask the user to confirm, and save the confirmed choice:

```text
03.prototype.style/selection.md
```

The selected style id must be one of:

```text
custom-command-system
gov-service-light
enterprise-data-station
industrial-iot-cockpit
medical-research-clean
education-campus-portal
finance-risk-terminal
mobile-business-console
```

Use the confirmed style consistently across login, module overview pages and function-point pages. Local `style.md` can adjust colors or brand details, but should not replace the confirmed style selection.

## `03.prototype.html/*.html`

Default prototype mode is HTML screenshot. Read [prototype-ui-style.md](prototype-ui-style.md) before writing these files. Each HTML file should be self-contained and use:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="prototype-style" content="{confirmed_style_id}">
  <meta name="module" content="02.modules/01.md">
  <title>页面名称</title>
  <style>...</style>
</head>
<body>
  ...
  <script>
    const mockData = [...];
  </script>
</body>
</html>
```

HTML prototype rules:

- Generate `00-login.html` for the login page, 10 module overview files `01.html` to `10.html`, and dedicated function-point files named `模块编号-功能点编号.html` for `40%-60%` of all function points.
- The login page is a required screenshot source for the manual and must not be replaced by a module screenshot.
- Match each file to the same-numbered module.
- Use inline CSS and inline JavaScript only.
- Use the confirmed style from `03.prototype.style/selection.md` and the matching guidance in [prototype-ui-style.md](prototype-ui-style.md).
- Do not use CDN, external images, remote fonts or backend requests.
- Include realistic mock data: names, dates, statuses, counts, amounts, organization names and records that fit the software domain.
- Design for a 1920x1080 screenshot. Keep the primary UI within the first viewport.
- Use stable dimensions for nav, toolbar, cards, tables, forms and dialogs.
- Avoid text overlap, tiny unreadable labels, empty panels and decorative-only layouts.
- Follow local `style.md` when available.
- Do not produce a generic admin page, default dashboard, plain card table, Ant Design clone or Bootstrap-like CRUD screen. Do not force every software type into the dark command-system style.
- All buttons, fields, menus, status labels and prompts later described in the operation manual must be visible in the corresponding HTML screenshot. This consistency requirement belongs here, before screenshots are captured.
- Prefer dedicated function-point screenshots for complex flows, data-entry forms, chart dashboards, monitoring/alert pages, audit handling, export/report features and configuration screens.

## `03.prototype.prompt/*.md`

Use this only when the user selects Gemini/API image generation mode. Read [prototype-ui-style.md](prototype-ui-style.md) first. Generate `00-login.md`, module overview prompts `01.md` to `10.md`, and function-point prompts named `模块编号-功能点编号.md` for `40%-60%` of all function points.

Prompt structure:

```markdown
# Prototype Prompt 01

目标文件: 04.prototype/01.jpg
对应模块: 02.modules/01.md
界面名称: ...

## 生成提示
...
```

Prompt content must specify:

- 16:9, 1920x1080, clean product UI screenshot.
- Chinese UI labels.
- The screen's role, selected menu item, main workflow state and primary data.
- Exact layout: navigation, toolbar, filters, table/form/chart/detail panel, modal or status drawer when needed.
- The user-confirmed style id and visual language from `03.prototype.style/selection.md`, not a generic admin dashboard.
- Visual style from local `style.md` if present.
- No text overlap, no unreadable tiny text, no meaningless placeholder blocks.

## `05.code/*.txt`

Each file should be named with its module number and module name, such as `01-用户权限管理.txt`. Do not use bare names like `01.txt`.

Each file should contain:

```text
// 模块: 01. 模块名称
// 说明: ...
===== Java Backend =====
...
===== React Frontend =====
...
```

Code style:

- Make the Java code concrete: a controller, service-like class, DTO, enum or repository stub can appear in the same file when useful.
- Include validation, state transitions, permission checks, duplicate checks, calculations, sorting, filtering or audit logging where the module needs them.
- Keep React code as a real component with state, effects, event handlers and conditional rendering.
- Do not over-abstract into many empty layers.
- Keep the comment ratio no lower than 10%, calculated from `cloc` as comment lines divided by `comment + code` lines.
- Use Chinese comments to explain business intent, validation rules, state transitions, permission checks and non-obvious logic. Do not pad the ratio with meaningless line-by-line comments.
- It is acceptable that the code is illustrative rather than directly compilable, but it must look like source code, not pseudocode.
- Confirm line counts with `cloc --by-file --force-lang=JavaScript,txt 05.code`; use `comment + code` as the non-empty line count and exclude `blank`.
- The 10 files under `05.code/` must contain at least 4000 `cloc` non-empty lines in total after removing blank lines.
- Target 380-520 non-empty lines per code file; complex modules may be longer when needed. Do not pad the line count with blank lines, meaningless duplicate code or comments that do not explain real business logic.
- Do not leave blank lines in `05.code/*.txt`.
- Do not use the word `copyright` anywhere in source-code files, regardless of case.

## `06.manual/*_操作手册.md`

Use [operation-manual-template.md](operation-manual-template.md) as the detailed template. The shorter structure below is only a navigation summary.

```markdown
# {SOFTWARE_NAME} V1.0

## 1、系统阐述
### 1.1、系统说明
### 1.2、主要功能
### 1.3、目标用户
### 1.4、术语定义
### 1.5、软件开发目的

## 2、实操指引
### 2.1、登录
### 2.2、模块名称
#### 2.2.1、子功能名称
```

Manual style:

- Write for end users: "点击", "选择", "输入", "提交", "查看", "导出".
- Use the formal project-delivery style, but blend function description, operation path, field explanation, button explanation, operation flow, system feedback and exceptions into natural paragraphs.
- `1.4、术语定义` must keep a structured `术语：定义` shape, such as `个体识别：指通过图像特征提取与比对技术，唯一标识每只种鹅的身份信息。` The example only shows the format; generated manuals must replace it with software-specific business or technical terms. Do not turn this section into continuous natural prose.
- After drafting the manual, apply [operation-manual-humanizer.md](operation-manual-humanizer.md) as a conservative professional humanizing pass. This should reduce formulaic AI phrasing without making the manual casual.
- Preserve software names, module names, function names, UI labels, button names, field names, status tags, prompts, figure captions and image paths exactly during the humanizing pass.
- Do not expose internal file labels or planning labels such as `模块01`, `模块 01`, `01模块`, `功能点01`, `第01功能点`. Use business names such as `用户权限管理` and `告警处置` instead.
- Do not write rigid labels such as `页面内容说明：`, `页面区域说明：`, `功能说明：`, `操作前提：`, `字段说明：`, `按钮说明：`, `操作步骤：`, `操作过程：`, `预期结果：` or `异常提示：` in final manual text.
- The rigid-label rule does not apply to `1.4、术语定义`; that section should intentionally use `术语：定义` entries.
- Avoid filling the body with repeated numbered or lettered lists. Keep numbering mainly in headings; use 2-4 connected paragraphs for each function point.
- Include one image per module when available.
- Reserve figure captions as `图X 页面名称`, and keep figure numbers increasing from `图1`.
- Convert business rules into operation tips, not implementation details.
- Keep paragraphs short and procedural.
- Use tables for field descriptions only when they improve clarity.
- Each main module must include 3-5 child function sections derived from `## 功能点清单`.
- The manual should include login screenshot, every module overview screenshot, and dedicated function-point screenshots for `40%-60%` of all function points. Prefer screenshots for complex and data-heavy functions.
- Each function point explanation should cover page content, operation prerequisites, operation process, expected result and common exception prompts in prose, without rigid subsection labels.

Image insertion:

```markdown
![图1 登录页面](../04.prototype/00-login.jpg)
![图2 模块名称](../04.prototype/01.jpg)
![图3 功能点名称](../04.prototype/01-01.jpg)
```

The image alt text is the figure caption. In Word output it must appear below the image and centered.

## `07.code.full/${SOFTWARE_NAME}_代码.docx`

The code document should:

- Contain exactly 60 code pages.
- Use 50 source lines per page, with no blank source lines.
- Use SimSun/宋体, 9 pt (小五), left alignment and single line spacing.
- Put the applied software name and version in the header exactly as they appear in the application form.
- Put page numbers in the upper-right header area.
- Preserve module order in the source stream.
- For source streams longer than 60 pages, use the first 30 pages and last 30 pages so the final page is the program ending page.
- Avoid adding explanatory prose, cover pages, directories, module heading pages or generated-material notes between code lines.
- Do not add generated-material explanations such as `软件源代码文档` or `本文档由 05.code 目录下的核心业务代码文件合并生成`.
- Do not include the word `copyright` anywhere in the code document.

## `08.application-info/${SOFTWARE_NAME}_软著申请表信息.txt`

Generate this final text file after the manual and code document are complete. It supports application-form entry, so keep it concise and directly fillable rather than explanatory.

- Use the field order defined in `SKILL.md` Step 9.
- Remove parenthetical prompt text from the final file.
- Keep hardware environments, operating systems, development tools, runtime support, development purpose and target industry within 50 characters each.
- Keep the main function summary within 200 Chinese characters.
- Pick exactly one software type from the Step 9 list, then describe technical characteristics within 100 Chinese characters.
- Set `源程序量` from `cloc` `comment + code` totals for `05.code` when available; otherwise use the nonblank generated source-line count and record that fallback in the delivery note.
