# Atlas design system — evaluation fixture

This is fictional input for evaluation 13, not a real organization's approval or test report.

## Approval and applicability

The design team approved the employee-service portal's directory and request-form patterns on 2026-09-10. The portal reuses these patterns with no component or brand changes. This source records that approval; it does not claim implementation, browser, keyboard or contrast tests have run on the new portal.

## Approved page patterns

- Desktop directory: persistent top navigation, page heading and search above the results; each result has a service name, description and request action. The directory is the main work surface.
- Narrow directory: same content order in one column; navigation wraps and search remains before results.
- Request form: single-column labeled fields, inline validation and a visible confirmation action. Errors preserve input.

## Semantic palette

| Role | Value |
|---|---|
| Canvas | #F8FAFC |
| Surface | #FFFFFF |
| Text | #172033 |
| Secondary text | #475569 |
| Action / hover / pressed | #2457D6 / #1E40AF / #1E3A8A |
| On action | #FFFFFF |
| Focus | #2457D6 |
| Control border | #64748B |
| Disabled text / surface | #64748B / #F1F5F9 |
| Success text / surface | #166534 / #F0FDF4 |
| Error text / surface | #991B1B / #FEF2F2 |

State meaning also has text. Supported appearance is light. Required contrast and focus behavior must be checked in the implementation; this fixture does not provide computed results.

## Typography and geometry

Use `system-ui, sans-serif`, with system language fallbacks and no downloaded fonts. Page heading is 32px/40px, weight 700 (24px/32px on narrow screens); section heading 20px/28px, weight 600; body and input 16px/24px, weight 400; action label 16px/24px, weight 600; helper text 14px/20px. Space scale: 4, 8, 12, 16, 24, 32px. Controls use 8px radius and a 44px minimum height. Main content is at most 1120px wide with 24px desktop or 16px narrow gutters; use one column below 768px.

## Components and maintenance

Atlas supplies the portal's navigation, search, results list, Button primary, labeled Input and inline Alert. Components use the semantic roles and typography above. Preserve hover/focus/pressed/disabled/loading for buttons, and default/focus/invalid/disabled/read-only for inputs. Loading and error results expose readable status and retry; empty results suggest adjusting search. Focus is a 2px action-colored ring with a 2px offset. No project overrides are planned. Design team owns the source; changes require review of the affected patterns.
