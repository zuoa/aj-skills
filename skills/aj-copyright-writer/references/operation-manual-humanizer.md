# Operation Manual Humanizer

Use this reference after drafting `06.manual/${SOFTWARE_NAME}_操作手册.draft.md` and before writing the final `06.manual/${SOFTWARE_NAME}_操作手册.md`.

This is a conservative, professional humanizing pass for software copyright operation manuals. It borrows the useful parts of Humanizer-zh: remove formulaic AI phrasing, reduce inflated claims, vary sentence rhythm and avoid repeated templates. Do not make the manual casual. The final document should still read like a government or enterprise delivery document.

## Goal

Rewrite the draft so it sounds like a careful technical writer prepared it from the actual screens. The degree of rewriting should be moderate:

- Keep the document structure, chapter headings, image links and business coverage stable.
- Rewrite repetitive paragraphs, stiff transitions and obvious template traces.
- Preserve professional wording, legal/material formality and operational clarity.
- Do not add product features, buttons, fields, screenshots or outcomes that are not present in the modules or prototypes.

## Protected Text

Do not change these strings unless the draft contains an obvious typo and the same corrected wording is already used in the module or prototype:

- Software name and version.
- Module names and function names from `02.modules/*.md`.
- UI labels from prototypes, including menu names, tab names, button names, field names, status tags and prompt text.
- Any text inside Chinese corner quotes such as `「新增」`, `「保存」`, `「告警中心」`.
- Figure captions and image paths, for example `![图3 告警处置](../04.prototype/03-02.jpg)`.
- Chapter numbers and heading hierarchy, such as `### 2.4、告警中心` and `#### 2.4.2、告警处置`.
- Legal and application-material terms, such as `计算机软件著作权登记`, `操作手册`, `源程序`, `鉴别材料`.
- Numbers, dates, percentages, filenames and directory paths.

Before rewriting, make a protected glossary from headings, image markdown, corner-quoted UI labels, code spans, module names and function names. After rewriting, check that protected strings still appear unchanged.

## What To Rewrite

Reduce these AI-like patterns:

- Repeated sentence frames, especially every function starting with `用户点击...后，系统进入...页面`.
- Overly complete but hollow statements, such as `便于用户完成全流程闭环管理`.
- Inflated adjectives, such as `全面`, `显著`, `高效`, `智能化`, `一体化`, `多维度`, when they do not add concrete operational meaning.
- Mechanical triads, such as `查询、录入、审核、导出` repeated in every section.
- Stacked transitions, such as `同时`, `此外`, `进一步`, `通过以上操作`.
- Hard labels in the body, such as `页面内容说明：`, `操作过程：`, `预期结果：`, `异常提示：`.

## How To Rewrite

Use a restrained editorial pass:

- Prefer concrete screen language: say what the page shows and what the user does.
- Keep paragraphs short, usually 2 to 5 sentences.
- Vary openings across adjacent sections. Use `进入页面后`, `在列表中`, `选择记录后`, `完成填写后`, `系统校验通过后` as needed, but avoid repeating the same sequence everywhere.
- Merge field, button, result and exception information into the operation narrative.
- Replace vague claims with observable results: list refreshes, status changes, export file appears, processing record is added, validation message is shown.
- Keep formal terms, but remove unnecessary intensifiers.
- If a sentence sounds promotional, make it operational.

## Do Not Do

- Do not use first person, jokes, casual commentary or colloquial filler.
- Do not simplify the manual into a blog-like explanation.
- Do not change exact UI text, button names, field names, module names or figure captions.
- Do not change screenshot paths.
- Do not remove required coverage for login, module pages or function-point pages.
- Do not add unsupported success messages. If the screenshot or module does not contain the text, use a generic but professional description such as `系统显示处理结果并刷新列表`.

## Examples

Before:

```text
用户点击功能区的「新增」按钮后，系统进入新增页面。页面内容说明：页面上方展示筛选条件，页面中部展示数据列表。预期结果：操作成功后系统显示保存成功并刷新列表。异常提示：必填信息未填写时系统显示提示。
```

After:

```text
用户在列表上方点击「新增」后，系统打开新增窗口。窗口中包含基础信息、业务属性和备注说明等内容，用户按页面要求填写后点击「保存」。系统会先校验必填项和重复数据，校验通过后提示处理完成，并将新增记录显示在列表中；如果信息缺失或用户权限不足，页面会在对应位置给出提示，用户可补充后重新提交。
```

Before:

```text
该模块可以全面提升业务处理效率，实现数据的统一管理和高效流转。
```

After:

```text
该模块用于集中维护业务记录，用户可在同一页面完成查询、录入、状态确认和结果查看。
```

## Final Check

The final manual must pass:

```bash
python {baseDir}/scripts/validate_outputs.py \
  --manual-draft-md "06.manual/${SOFTWARE_NAME}_操作手册.draft.md" \
  --manual-md "06.manual/${SOFTWARE_NAME}_操作手册.md"
```

If validation reports missing protected terms, restore the exact original term and adjust only surrounding prose.
