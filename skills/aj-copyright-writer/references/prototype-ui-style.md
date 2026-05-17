# Prototype UI Style

Use this reference when generating `03.prototype.html/*.html` or `03.prototype.prompt/*.md`.

The target visual language is a custom high-end command system, inspired by the provided reference image's layout: deep blue technical cockpit, angular frame, top title/navigation strip, search/action zone, and dense business table area. Do not copy the reference image pixel-for-pixel; abstract its structure and improve the visual quality.

## Design Goal

The prototype should look like a bespoke industry system delivered for a serious project, not a generic admin dashboard. It should feel closer to a command center / intelligent monitoring platform / specialized business terminal.

Default style direction:

- Deep navy or blue-black full-screen canvas.
- Layered angular frame with beveled corners.
- Top title bar with system name, tab navigation and time/status indicators.
- Search and action command strip near the top of the content area.
- Main workspace with data table, cards, forms, detail drawer, chart or map depending on the module.
- Cyan, blue, teal or amber accent lights, used sparingly for hierarchy.
- Thin luminous borders, glass-like panels, technical grid texture and subtle scanning lines.
- Dense but organized information layout suitable for repeated business operation.

## Mandatory HTML Markers

Every HTML prototype must include:

```html
<meta name="prototype-style" content="custom-command-system">
```

Every module page must include:

```html
<meta name="module" content="02.modules/01.md">
```

The login page uses:

```html
<meta name="module" content="login">
```

## Layout Pattern

Use this structure unless a module has a clearly better domain-specific layout:

```text
Full-screen technical frame
├─ Header cockpit
│  ├─ system title
│  ├─ top navigation tabs
│  ├─ current time / user / status chips
│  └─ right-side action buttons
├─ Query / command strip
│  ├─ segmented filters
│  ├─ search input
│  └─ primary operation buttons
├─ Main workspace
│  ├─ KPI cards or left summary rail when useful
│  ├─ central table / form / chart / monitoring area
│  └─ detail panel / operation area / status drawer
└─ Technical border and bottom status line
```

For data-entry and list modules, keep the reference image's "filter area + action buttons + table" hierarchy, but refine it:

- Filters should look integrated into a command strip, not like plain form controls.
- Tables should use high-contrast row separators, status chips and clear operation links.
- Important buttons should use luminous filled styles; secondary buttons should use outline or dark glass styles.
- Empty dark panels are not acceptable. Every panel needs useful labels, mock data or visible controls.

For login:

- Use the same high-end visual system.
- Show system name prominently.
- Include visible account, password, optional organization/code fields, remember-login checkbox and login button.
- Include subtle status text such as "安全接入", "专网认证", "V1.0".
- Do not use a generic centered white login card.

## Visual Tokens

Use CSS variables in each HTML file:

```css
:root {
  --bg: #020b24;
  --panel: rgba(7, 28, 74, 0.78);
  --panel-strong: rgba(9, 42, 98, 0.92);
  --line: rgba(42, 190, 255, 0.42);
  --line-soft: rgba(73, 130, 210, 0.22);
  --cyan: #25e8ff;
  --teal: #00d0a6;
  --amber: #f4c95d;
  --danger: #ff5d7a;
  --text: #eaf7ff;
  --muted: #83a8d8;
}
```

Recommended CSS techniques:

- `clip-path: polygon(...)` for beveled panels and navigation tabs.
- `linear-gradient`, `radial-gradient` and `repeating-linear-gradient` for background depth.
- `box-shadow` and pseudo-elements for luminous edge highlights.
- CSS grid for the main layout.
- `letter-spacing` only where labels are short and readable.
- Stable dimensions for controls, tables, cards, tabs and action areas.

Do not use:

- Plain white or light-gray admin pages.
- Default Ant Design / Element / Bootstrap visual language.
- Ordinary left sidebar + plain top bar + white card composition.
- Purple-blue SaaS gradient cards.
- Random decorative blobs, cartoon icons or unrelated illustrations.
- External CDNs, remote fonts, remote images or icon libraries.

## Information Density

A software copyright manual benefits from screenshots that show operable product depth. Each prototype should include visible business state:

- 4-8 filter fields or key controls where appropriate.
- 4-7 table rows or 3-6 form sections.
- Status labels such as "待审核", "已完成", "预警中", "启用", "停用".
- Operation links or buttons that match the manual steps.
- Domain-specific mock data, not "测试1/测试2" placeholders.

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

- At first glance it reads as a custom system, not a generic backend.
- The system title is prominent and domain-specific.
- Top navigation and active tab are clear.
- Key operation buttons are visible.
- Field names and table headers are readable at 1920x1080.
- No text overlaps borders, icons or adjacent controls.
- The image can be inserted into a Word manual without looking like a placeholder.
