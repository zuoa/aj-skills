# Workflow Contract

此文件定义 `aj-copyright-writer` 的产物约定。执行时以用户指定目录为准；用户未指定时创建独立输出目录，避免污染项目根目录。

## Directory Layout

```text
{output_root}/
  01.spec/
    spec.md
  02.modules/
    01.md
    ...
    10.md
  03.prototype.html/
    00-login.html
    01.html
    ...
    10.html
    01-01.html
    ...
  03.prototype.style/
    selection.md
  03.prototype.prompt/
    00-login.md
    01.md
    ...
    10.md
    01-01.md
    ...
  04.prototype/
    batch.json
    00-login.jpg
    01.jpg
    ...
    10.jpg
    01-01.jpg
    ...
  05.code/
    01-模块名称.txt
    ...
    10-模块名称.txt
  06.manual/
    {SOFTWARE_NAME}_操作手册.draft.md
    {SOFTWARE_NAME}_操作手册.md
    {SOFTWARE_NAME}_操作手册.docx
  07.code.full/
    {SOFTWARE_NAME}_代码.docx
```

## Numbering Rules

- Always use two-digit file names: `01` to `10`.
- Numbered directories must contain exactly the expected files:
  - `02.modules`: `01.md` to `10.md`
  - `03.prototype.html`: `00-login.html`, `01.html` to `10.html`, plus function-point pages in default HTML mode
  - `03.prototype.style`: `selection.md` recording the recommended and confirmed prototype style
  - `03.prototype.prompt`: `00-login.md`, `01.md` to `10.md`, plus function-point prompts in image mode
  - `04.prototype`: `00-login.jpg`, `01.jpg` to `10.jpg`, plus function-point screenshots
  - `05.code`: `01-模块名称.txt` to `10-模块名称.txt`
- Keep the same number across module, prompt, prototype image and code:
  - `02.modules/03.md`
  - `03.prototype.html/03.html` or `03.prototype.prompt/03.md`
  - `04.prototype/03.jpg`
  - `05.code/03-模块名称.txt`
- Function-point pages use `模块编号-功能点编号`, for example `03-02.html`, `03-02.md`, `03-02.jpg`.
- Every module needs a module overview screenshot. In addition, cover `40%-60%` of all function points with dedicated screenshots.
- Prioritize complex workflows, data-entry pages, chart/data visualization, monitoring/alert screens, audit flows, report export and configuration pages.

## Batch Manifest

Prototype image generation uses `04.prototype/batch.json` as a resumable manifest. Create or refresh it before taking screenshots or making API calls.

Each item must include:

```json
{
  "id": "00-login",
  "mode": "html",
  "module": "login",
  "html": "/abs/path/03.prototype.html/00-login.html",
  "output": "/abs/path/04.prototype/00-login.jpg",
  "retry": {
    "attempts": 0,
    "max": 3
  },
  "status": "pending"
}
```

In `image` mode, each item uses `prompt` instead of `html`. The manifest must contain 11 items: `00-login` and `01` to `10`. Allowed statuses: `pending`, `running`, `success`, `failed`. Re-running the prototype script should skip `success` items whose output file still exists, unless `--force` is passed.

## Reference Directory Resolution

When the user mentions `reference`, `refence` or `refrence`, treat them as possible local reference directories. Search in this order:

1. `{output_root}/reference`
2. `{output_root}/refence`
3. `{output_root}/refrence`
4. `{cwd}/reference`
5. `{cwd}/refence`
6. `{cwd}/refrence`
7. `~/aj-skills/reference`
8. `~/aj-skills/refence`
9. `~/aj-skills/refrence`

Do not rename the user's directories.

## Required User-Visible Artifacts

The final answer should mention:

- Output root.
- Whether live web research succeeded.
- Whether `style.md` was found.
- Whether the manual template was found.
- Prototype generation mode: `html` screenshot or `image` API.
- Recommended prototype style, user-confirmed style and whether a user-provided `style.md` was used as an overlay.
- Whether the operation manual draft was humanized with the conservative copyright-manual humanizer.
- Whether docx files were generated.
- Any blocked step with the exact missing dependency, key or file.

## Step Boundaries

Do not skip a numbered step silently. If a step cannot be completed:

1. Write the best possible upstream artifacts.
2. Stop before fabricating downstream artifacts that depend on the missing result.
3. Explain the blocker and the command or file needed to continue.

Examples:

- If `GEMINI_API_KEY` is missing, still create prototype prompts, but do not create fake `04.prototype/*.jpg`.
- If the Word template is missing, generate a docx without template and record that it is untemplated.
- If public information about the software is scarce, continue from reasonable assumptions and label them as assumptions.
