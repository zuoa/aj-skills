# Prototype UI Style

Use this reference when generating `03.prototype.html/*.html` or `03.prototype.prompt/*.md`.

The prototype should look like a bespoke software system made for the target industry. Do not default every project to the same dark cockpit UI. First infer the software type, recommend the best style, ask the user to confirm, and generate all prototype pages with the confirmed style.

## Style Confirmation Workflow

Before creating `03.prototype.html/*.html` or `03.prototype.prompt/*.md`:

1. Read `01.spec/spec.md`, the 10 files in `02.modules/`, and any local `reference/style.md`.
2. Infer the software category from the software name, business objects, user roles and main workflows.
3. Recommend one best style and 1-2 alternatives. Explain the reason in 2-4 short sentences.
4. Ask the user to confirm the style before generating prototypes. Do not proceed to prototype generation until the user confirms, unless the user has explicitly requested unattended generation; in that case use the recommended style and record the reason.
5. After confirmation, create:

```text
03.prototype.style/selection.md
```

Use this format:

```markdown
# Prototype Style Selection

软件名称: {SOFTWARE_NAME}
推断类型: {software_category}
推荐风格: {style_id} - {style_name}
用户确认: {confirmed_style_id} - {confirmed_style_name}
本地风格参考: {style.md path or 未提供}

## 推荐理由
...

## 生成约束
- All HTML pages use `<meta name="prototype-style" content="{confirmed_style_id}">`.
- All prompts explicitly mention `{confirmed_style_name}` and its visual tokens.
- Local `style.md` is treated as an overlay, not as permission to ignore the confirmed style.
- Prototype screens must not include copyright notices, developer company names, technical support units, producer names, contractor names or similar company attribution.
```

## Style Library

### `custom-command-system` - High-End Command System

Best for: public safety, monitoring, emergency dispatch, IoT supervision, environmental monitoring, logistics command, risk warning, smart city and systems that need a strong command-center feel.

Visual language:
- Deep navy or blue-black full-screen canvas.
- Angular technical frame, top title/navigation strip and dense command workspace.
- Cyan, teal and amber accent lights with luminous borders.
- Tables, maps, alarms, status chips, KPI panels and right-side detail drawers.

### `gov-service-light` - Formal Government Service System

Best for: government affairs, approval handling, public service, administrative licensing, civil service, government reporting and formal institutional systems.

Visual language:
- Clean white and light-blue page background with restrained official blue accents.
- Strong header, breadcrumb-like path, clear module tabs and policy-style information grouping.
- Dense but readable forms, approval timelines, official status seals and document preview areas.
- Minimal decoration; the page should feel reliable, organized and suitable for Word screenshots.

### `enterprise-data-station` - Enterprise Operations Workbench

Best for: CRM, ERP, asset management, inventory, contract management, procurement, inspection, after-sales, office workflow and general enterprise operations.

Visual language:
- Neutral light or soft dark workspace with compact top toolbar and data-first layout.
- Balanced table, filter, detail drawer and task panel composition.
- Subtle blue/green status indicators, clear action hierarchy and practical information density.
- Avoid decorative hero styling; this should feel like a daily work system.

### `industrial-iot-cockpit` - Industrial IoT Cockpit

Best for: equipment monitoring, production scheduling, energy management, warehouse automation, safety inspection, sensor data and plant operations.

Visual language:
- Dark steel, graphite and electric cyan/orange accents.
- Equipment topology, sensor cards, trend charts, alarm strips and device state tables.
- Strong grid structure with left summary rail and central monitoring area.
- Use technical depth, but keep field labels and operation buttons readable.

### `medical-research-clean` - Medical / Research Clean Terminal

Best for: medical management, laboratory systems, clinical data, health follow-up, research sample management and life-science workflows.

Visual language:
- Clean white, pale teal, blue-green and soft gray palette.
- Patient/sample cards, timeline panels, risk tags, record tables and structured forms.
- Clinical clarity over decoration; use generous spacing and calm status colors.
- Avoid overly futuristic dark visuals unless the user explicitly wants a command center.

### `education-campus-portal` - Campus Service Portal

Best for: campus asset inspection, teaching affairs, student services, dormitory management, training platforms and school operations.

Visual language:
- Fresh blue, green and white palette with a friendly but still formal interface.
- Campus map/list split views, timetable-like panels, role-based cards and task lists.
- Softer corners and clearer navigation, without becoming a marketing site.
- Suitable for education administrators and campus operation staff.

### `finance-risk-terminal` - Finance Risk Terminal

Best for: audit, finance, contract risk, credit review, compliance, invoice control, banking-like workflows and analysis-heavy systems.

Visual language:
- Dark graphite or deep ink background with restrained gold, cyan or red risk accents.
- Risk score cards, review queues, evidence panels, comparison tables and audit trail timelines.
- Conservative, precise and data-heavy; avoid flashy cyberpunk styling.
- Button labels and risk status must be highly legible.

### `mobile-business-console` - Mobile / Field Work Console

Best for: mobile-first systems, field inspection, delivery, patrol, maintenance, collection, on-site reporting and apps where screenshots need to show mobile or tablet behavior.

Visual language:
- 1080p screenshot can show a tablet or mobile shell inside a clean operational background.
- Large touch controls, bottom actions, scan/upload widgets, GPS/task status and photo evidence blocks.
- Use mock device dimensions with stable layout; do not make a generic phone app landing page.

## Category Recommendation Hints

- Software names containing `监管`, `监测`, `预警`, `指挥`, `态势`, `调度`, `应急`, `安防`, `物联网` usually fit `custom-command-system` or `industrial-iot-cockpit`.
- Names containing `设备`, `传感`, `生产`, `能耗`, `仓储`, `巡检`, `工厂` usually fit `industrial-iot-cockpit`; campus or office inspection can fit `enterprise-data-station` or `education-campus-portal`.
- Names containing `政务`, `审批`, `公共服务`, `申报`, `档案`, `民政`, `住建` usually fit `gov-service-light`.
- Names containing `合同`, `审查`, `风控`, `审计`, `财务`, `发票`, `合规`, `授信` usually fit `finance-risk-terminal`.
- Names containing `医院`, `医疗`, `健康`, `检验`, `实验`, `样本`, `科研` usually fit `medical-research-clean`.
- Names containing `校园`, `教学`, `学生`, `教务`, `培训`, `宿舍` usually fit `education-campus-portal`.
- Names containing `客户`, `资产`, `库存`, `采购`, `工单`, `协同`, `办公` usually fit `enterprise-data-station`.
- Names containing `移动`, `外勤`, `巡检`, `采集`, `拍照`, `上报`, `现场` may fit `mobile-business-console`, especially when the user wants mobile screenshots.

When multiple styles fit, recommend the one that best matches the most important workflow and list alternatives. For example, `校园资产巡检管理软件` can be `education-campus-portal` if the focus is campus service, or `enterprise-data-station` if the focus is asset ledger and work orders.

## Mandatory HTML Markers

Every HTML prototype must include the confirmed style id:

```html
<meta name="prototype-style" content="{confirmed_style_id}">
```

Every module page must include:

```html
<meta name="module" content="02.modules/01.md">
```

The login page uses:

```html
<meta name="module" content="login">
```

Allowed `prototype-style` values are:

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

## Shared Layout Rules

Use the confirmed style, but keep these rules for every style:

- The system title must be prominent and domain-specific.
- Navigation, active tab, user/status area and primary action buttons must be visible.
- Screenshots must show operable product depth: filters, tables, forms, charts, status tags or detail panels.
- All buttons, fields, menus, status labels and prompts later described in the operation manual must be visible in the corresponding screenshot.
- Design for a 1920x1080 screenshot. Keep the primary UI within the first viewport.
- Use stable dimensions for nav, toolbar, cards, tables, forms and dialogs.
- Avoid text overlap, tiny unreadable labels, empty panels and decorative-only layouts.
- Do not use CDN, external images, remote fonts or backend requests.
- Do not use default Ant Design / Element / Bootstrap visual language.
- Do not place copyright notices, developer company names, technical support units, producer names, contractor names or similar company attribution anywhere in the prototype, including footer areas, login pages, title bars, watermarks and about dialogs.
- Show only the software name, business modules, roles, mock data and operation controls.

## Login Rules

When the software has an authentication flow, create a real login screenshot:

- Show the software name prominently.
- Include visible account, password, optional organization/code fields, remember-login checkbox and login button.
- Use the confirmed style's visual language.
- Do not use a generic centered white card unless the confirmed style is a formal light style and the card has domain-specific framing and details.

## Local `style.md`

If local `reference/style.md`, `refence/style.md` or `refrence/style.md` exists:

- Treat it as an overlay for color, typography, spacing or brand preference.
- Still recommend and confirm one of the style ids above.
- If the local style conflicts with readability, screenshot quality or the confirmed style, prioritize readability and copyright-material usefulness.

## Manual Consistency Rule

Before writing the operation manual, compare each module's intended operation text with its screenshot.

If the manual says:

- 点击「新增」
- 点击「保存」
- 选择「设备类型」
- 查看「状态」
- 点击「导出」
- 切换至「告警中心」

Then the corresponding screenshot must visibly contain these exact or very close labels. If it does not, revise the HTML prototype first.

## Quality Bar

The final screenshot should pass these checks:

- At first glance it reads as a custom system matching the software type, not a generic backend.
- The confirmed style is consistent across the real entry/login page, module overview pages and function-point pages.
- Key operation buttons are visible.
- Field names and table headers are readable at 1920x1080.
- No text overlaps borders, icons or adjacent controls.
- The image can be inserted into a Word manual without looking like a placeholder.
