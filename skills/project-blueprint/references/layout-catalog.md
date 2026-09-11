# Application-shell and layout selection

Use this catalog to recommend the structural shell of a product before choosing
its visual theme. A layout family defines persistent regions, navigation, and
how work surfaces relate; it is not a color style, component-library preset, or
synonym for an industry.

## Keep four decisions separate

Compose the result in `DESIGN.md` instead of treating a familiar screenshot as
one indivisible template:

1. **Layout family** defines the durable spatial model, such as an enterprise
   shell, focused workbench, or guided flow.
2. **Navigation model** defines hierarchy and movement: header, side navigation,
   tabs, breadcrumbs, bottom navigation, rail, or stack navigation.
3. **Work-surface model** defines the content relationship: single canvas,
   dashboard, list-detail, main-supporting pane, document canvas, or step flow.
4. **Platform chrome** defines cross-product capabilities such as authentication,
   tenant/workspace switching, global search, notifications, help, and profile.

Unified login or SSO does not by itself justify a left sidebar. Authentication
belongs to platform chrome and security architecture; choose the layout from
task breadth, navigation depth, switching frequency, content relationships,
screen environment, and user expertise. A product may also compose families:
for example, an enterprise shell can contain a guided purchase flow.

## Evidence to collect before recommending

| Input | Question that changes the recommendation |
|---|---|
| Product surfaces | Is this a public site, authenticated product, mobile app, or a connected suite of products? |
| Primary task | Is the user monitoring, finding, reading, editing, comparing, approving, or completing a bounded transaction? |
| Information architecture | How many stable top-level destinations exist, how deep is the hierarchy, and do labels need more room than a header provides? |
| Work continuity | Must selection, filters, document context, or live status remain visible while the user works? |
| Frequency and expertise | Is this occasional self-service or repeated expert work where scan speed and shortcuts matter? |
| Content relationship | Is content independent, list-detail, source-document-plus-inspector, dashboard-to-drilldown, or a strict sequence? |
| Platform capabilities | Anonymous/auth-gated areas, SSO/IdP discovery, tenants/workspaces, roles, global search, notifications, help, and product switching? |
| Devices and input | Phone/desktop share, resize and split-screen use, touch/keyboard/pointer, field conditions, and safe areas? |
| Risk | Could hidden context, stale status, accidental tenant changes, or an ambiguous action cause financial, legal, operational, or privacy harm? |

When evidence is incomplete, recommend a provisional family and name the
prototype or task test that would change it. Do not infer the shell only from
labels such as “enterprise,” “AI,” or “modern.”

## Layout families

| ID and direction | Structural anatomy | Strong fit | Weak fit / main risk | Responsive transformation |
|---|---|---|---|---|
| `enterprise-workspace` — multi-module application shell | Persistent global header for product/tenant/identity utilities; collapsible left primary navigation; page header and local actions above a fluid content area | Authenticated B2B suites, administration, ERP/CRM, approval and configuration products with several durable modules or roles | A small app with few destinations loses horizontal space and feels bureaucratic. SSO alone is not evidence for this shell | Keep global identity and current context visible; turn the side navigation into an accessible drawer or reduced rail only when labels remain discoverable; do not reproduce a dense desktop page on phone |
| `compact-product-shell` — shallow authenticated product | Persistent top header with product identity, three to five peer destinations, and account utilities; page header/local toolbar above one primary content canvas; optional local tabs inside a destination | Focused SaaS, team utilities, small internal tools, and self-service products with shallow information architecture and users who benefit from full content width | Header crowding, ambiguous dropdowns, and hidden hierarchy appear as modules grow. Do not keep adding menus after the information architecture proves it needs a side navigation | Move peer destinations into a clearly labelled drawer or platform-appropriate compact navigation; keep the current page, primary action, and identity reachable without duplicating navigation |
| `focused-workbench` — context-preserving creation/review | Slim global chrome; contextual navigator or source list; large central canvas; optional resizable inspector/supporting pane; local toolbar acts on the current object | Document review, legal/research work, editors, case management, AI review, developer or creative tools where source and selection must persist | Too many always-open panes crowd occasional users; nested independent scroll areas and focus order become difficult | Expanded windows show two or three related panes; compact windows preserve the same selection as stack navigation and expose the inspector as a sheet/full screen |
| `operations-console` — live situation and intervention | Persistent shell; visible freshness/incident/status band; overview metrics only when actionable; dense table/timeline/map/chart surface; synchronized filters; drilldown or detail drawer | Monitoring, incident response, logistics, finance operations, inventory, security, and trained teams managing changing state | Decorative dashboards, stale data, color-only status, and excessive widgets obscure action. Not appropriate merely because a stakeholder asks for a dashboard | Prioritize alerts and current actions on smaller windows; collapse secondary metrics and move row detail to a dedicated screen without hiding freshness or severity |
| `catalog-hub` — find, compare, and discover | Header with shallow global navigation; prominent scoped search; filters/sort adjacent to a grid or list; category/discovery landing; separate detail surface | E-commerce, media/content libraries, marketplaces, knowledge catalogs, directories, and public-to-account experiences | A deep operational hierarchy outgrows the header/filter model; over-filtering and card-only content reduce scan efficiency | Filters become a drawer/sheet, results switch to a readable list where needed, and search stays prominent; preserve query/filter state across detail and back navigation |
| `guided-flow` — bounded completion path | Minimal surrounding navigation; single primary column or focused task canvas; step/progress context when it helps; persistent save/exit/review; one clear primary action | Onboarding, applications, checkout, booking, imports, setup wizards, and other ordered, high-consequence submissions | Poor as the whole shell for exploratory or interrupt-driven work; rigid steppers fail when steps are optional or revisitable | Use one main task per compact screen, keep progress and recovery visible, and avoid desktop multi-column forms that scramble reading and error order |
| `public-service-portal` — information and task entry | Accessible header and footer; shallow audience/task navigation; search; restrained landing modules; readable content width; clear handoff into authenticated self-service | Corporate/institutional sites, government/public service, documentation entry points, support centers, and products mixing public information with account tasks | Marketing modules can bury urgent tasks; an authenticated operational product should not retain a promotional homepage as its daily workspace | Reduce navigation without hiding essential routes, preserve search and urgent tasks, and let long content reflow to one readable column |
| `adaptive-mobile-app` — few stable top-level destinations | Phone bottom navigation or platform-equivalent tabs; stack navigation inside each destination; contextual top bar/actions; rail/sidebar or multi-pane adaptation on larger windows | Consumer, field, community, habit, messaging, and media apps with a small stable set of peer destinations and frequent one-handed switching | Too many destinations create overflow and unstable navigation; bottom navigation must not be used for commands. Desktop web may need another family rather than a stretched phone UI | Base changes on available window and input, not device name: bottom navigation in compact windows, rail/sidebar or adaptable tabs in expanded windows, with selection and back-stack continuity |

### Direction-to-shortlist defaults

Use these only when stronger product evidence is absent. Present two or three
credible candidates, not the entire catalog.

| Product/task direction | First candidate | Credible alternative | When to change the order |
|---|---|---|---|
| Multi-module enterprise workflow, admin, or approval | `enterprise-workspace` | `focused-workbench` | Put `focused-workbench` first when one object/document dominates and surrounding modules are secondary. |
| Small authenticated SaaS or internal tool with few modules | `compact-product-shell` | `enterprise-workspace` | Put `enterprise-workspace` first when navigation depth, role-specific modules, or cross-module switching no longer fits a stable header. |
| Monitoring, logistics, incident, or live operations | `operations-console` | `enterprise-workspace` | Put `enterprise-workspace` first when configuration and records dominate live intervention. |
| Research, document, case, review, or creation | `focused-workbench` | `enterprise-workspace` | Put `public-service-portal` first when reading/browsing is public and editing is rare. |
| Store, marketplace, searchable library, or directory | `catalog-hub` | `public-service-portal` | Put `public-service-portal` first when authoritative guidance and task routing matter more than comparison/discovery. |
| Onboarding, booking, checkout, application, or setup | `guided-flow` | Its containing product family | Treat the flow as a nested mode when users also need a durable product workspace. |
| Corporate, government, support, or documentation entry | `public-service-portal` | `catalog-hub` | Put `catalog-hub` first when search/filter/result comparison is the main job. |
| Phone-first consumer or field product | `adaptive-mobile-app` | Task-specific family for expanded Web/tablet | Use a different Web shell when desktop roles and tasks materially differ; do not force cross-platform geometry to match. |

## Platform chrome and unified identity

Record these capabilities independently from the layout shortlist. Only show a
capability in persistent chrome when users need it across contexts; otherwise
place it at the relevant local surface.

| Capability | Placement rule | Behavior to decide | Security/architecture handoff |
|---|---|---|---|
| Authentication entry | Public header for mixed public/account products; dedicated auth boundary for auth-gated products | Password/passkey/social/SSO entry, IdP or tenant discovery, return URL, loading/error/recovery, signed-in destination | Protocol, session, MFA, account linking, timeout, re-authentication, and logout are governed by `SECURITY.md`/`ARCHITECTURE.md`, not inferred from the shell |
| Tenant/workspace switcher | Persistent header or clearly labelled shell region only when switching is frequent and authorized | Show current context, confirm high-risk switches, preserve or deliberately reset local state, make cross-tenant boundaries unmistakable | Authorization and data isolation must be enforced server-side; navigation visibility is not access control |
| Product/app switcher | Global header when the organization offers multiple independently navigable products | Recently used/all products, current product, destination behavior, keyboard/search access | Entitlements and target-domain/session behavior require explicit ownership |
| Global search or command entry | Header when scope truly spans the product; local toolbar/sidebar when it only filters current content | Visible scope, result types, permissions, shortcut, recent queries, empty/error states | Search index authorization, auditability, and command confirmation belong in architecture/security |
| Notifications/inbox | Global header when alerts cross modules and require timely action | Unread semantics, severity, freshness, deep link, acknowledgement, batching | Delivery, retention, permissions, and sensitive preview policy |
| Help/support | Persistent utility only when users need cross-context assistance | Contextual help, docs, contact/escalation, diagnostics disclosure | Support data transfer and impersonation/access controls |
| Profile/session | Consistent global location after sign-in | Account identity, preferences, accessibility, session status, sign-out-all, organization membership | Session revocation, audit events, personal-data handling |

Role-aware navigation may remove destinations a user cannot use, but direct
URLs and backend actions still require authorization. Define what happens when
permissions change mid-session and how the shell communicates expired sessions,
wrong-tenant links, unavailable modules, and partial platform outages.

## Score and confirm the shortlist

Score two or three candidates on a 1–5 scale. Explain the evidence behind any
score that changes the result.

| Criterion | Weight | What a high score means |
|---|---:|---|
| Primary-task and content-relationship fit | 30% | The work surface keeps the objects, actions, and context needed for the main job visible. |
| Information architecture and navigation fit | 20% | The model handles the real breadth/depth without hiding important destinations or wasting space. |
| Frequency, expertise, and efficiency | 15% | It supports the actual session length, repetition, shortcuts, and learning needs. |
| Device and input adaptation | 15% | Compact and expanded windows preserve task and navigation continuity across touch, keyboard, and pointer. |
| Risk, accessibility, and context clarity | 15% | Current location, tenant, state, focus order, landmarks, recovery, and consequential actions remain clear. |
| Delivery and evolution cost | 5% | The UI foundation supports the regions and responsive changes without fragile custom shell behavior. |

The confirmation in `DESIGN.md` must include:

- recommended family and whether it is the product shell or a nested task mode;
- closest rejected alternative and the evidence that made it lose;
- desktop/expanded anatomy and compact transformation;
- navigation hierarchy, persistent regions, scroll ownership, and page/local action placement;
- selected platform-chrome capabilities, including authentication/SSO and tenant
  behavior where applicable;
- a representative task prototype or usability/accessibility check that could
  overturn the decision.

Do not confirm a layout from a static homepage alone. Test at least one deep
destination, long/empty/error content, permission denial, keyboard traversal,
200% zoom, compact width, and restoration of selection/filter/step state.

## Cross-layout acceptance checks

- Use semantic `header`, `nav`, `main`, and `aside` regions where applicable;
  uniquely label multiple navigation landmarks and expose the current page.
- Keep global navigation distinct from local object actions. Tabs switch peer
  views; toolbars act on the current view; neither should become a miscellaneous
  overflow for unrelated features.
- Define one scroll owner per major axis where practical. Sticky headers,
  virtualized tables, split panes, dialogs, and drawers need explicit focus,
  overflow, and restoration behavior.
- Preserve current product, tenant/workspace, location, and unsaved-work status
  across responsive transformations. A collapsed icon-only rail must not make
  unfamiliar destinations guessable only by icon.
- Derive breakpoints from content failure and available window size. Verify
  resizing, split screen, browser zoom, text expansion, safe areas, and input
  changes instead of targeting a few device names.
- Keep primary navigation stable. Do not hide destinations merely because their
  content is empty or temporarily unavailable; explain the state at the
  destination unless authorization or policy requires otherwise.

## Official references

Official sources checked 2026-09-11. Recheck changeable APIs at decision time.

- [Carbon global header](https://carbondesignsystem.com/patterns/global-header/):
  separates global/system navigation from local/product navigation, places
  authentication and cross-product utilities in persistent chrome, and shows
  when a header needs a left panel for deeper navigation.
- [Ant Design Layout](https://ant.design/components/layout/): compares
  header-first and side-navigation structures, including hierarchy, horizontal
  space, collapsible sidebars, and responsive behavior.
- [Apple tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars),
  [toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
  and [split views](https://developer.apple.com/design/human-interface-guidelines/split-views):
  distinguish navigation from view actions and describe adaptable tabs,
  sidebars, and list-detail structures.
- [Android adaptive navigation](https://developer.android.com/develop/adaptive-apps/guides/build-adaptive-navigation)
  and [canonical layouts](https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts):
  adapt bottom navigation, rails/drawers, list-detail, and supporting panes from
  available window size while preserving navigation state.
- [WAI-ARIA breadcrumb pattern](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/)
  and [navigation landmark example](https://www.w3.org/WAI/ARIA/apg/patterns/landmarks/examples/navigation.html):
  identify current location and require distinct labels when a page has multiple
  navigation regions.
