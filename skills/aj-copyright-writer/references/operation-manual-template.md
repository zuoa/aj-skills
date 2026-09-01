# Operation Manual Writing Guide

Use this guide for interaction-heavy software. It is a composition guide, not a fill-in template.

## Overall structure

The manual should normally include software overview, intended users, domain terms, login or entry, and the ten core business areas. Change chapter names and depth to match the product rather than forcing every function into an identical subsection pattern.

## Compose by task type

Choose the pattern that fits the function.

### Task submission or data entry

Explain the prerequisite business record, how the user reaches the form, the domain fields that affect processing, validation at submission, the created record or state, and how the user corrects rejected input.

### Review and approval loop

Explain the review queue, evidence shown to the reviewer, permitted decisions, required reasons, state changes, return/review-again behavior and audit records.

### Monitoring and incident response

Explain monitored indicators, threshold or event meaning, severity, acknowledgement, assignment, handling, closure and escalation. Connect charts and status colors to concrete actions.

### Analysis and comparison

Explain the comparison population, time window, filters, calculation basis, interpretation, drill-down and export result. Do not describe decorative charts as analysis.

### Batch import or export

Explain accepted columns, uniqueness keys, validation feedback, partial-failure behavior, retry strategy, export scope and output file contents.

### Rule configuration

Explain who may change a rule, value range, effective time, conflict priority, preview or validation, publication and rollback.

Do not repeat all six patterns for every module. Select only what the feature actually does.

## Required consistency

- Use the exact module, function, button, field, status and prompt text shown by the prototype.
- Explain what happens after an action, including state, records, notifications or files.
- Include realistic permission and exception behavior where it affects the user.
- Every described control must be visible in the referenced screenshot.
- All ten module names must appear, but modules may receive different levels of detail.

## Screenshots

- Start with the real login or entry page when the software has one.
- Include each module's representative screen and additional images for 40%–60% of complex function points.
- Prefer data entry, approval, incident handling, analysis, import/export and rule configuration screens.
- Use increasing captions such as `图1 登录页面` and relative paths from `06.document` to `04.prototype`.
- Do not reuse one screenshot under misleading captions.

## Style

Use direct procedural prose for operators. Vary paragraph length and structure according to the task. Avoid rigid labels such as `页面内容说明：`, `功能说明：`, `操作步骤：`, `预期结果：` and `异常提示：`. Avoid repeated stock openings and conclusions.

`1.4、术语定义` may retain `术语：定义` entries because this is a useful information structure rather than narrative boilerplate.

## Prohibited content

- placeholders such as `字段A`, `按钮B` or `模块01`;
- developer-only descriptions that do not affect operation;
- claims about generation, templates, AI, assumptions or originality audits;
- copied database schemas or source-code explanations;
- a `.draft.md` formal output.

Before saving the final Markdown, apply `operation-manual-humanizer.md` conservatively while preserving all UI terms, captions and image paths.
