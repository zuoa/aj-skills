# Workflow Contract

## Directory layout

```text
{output_root}/
  01.spec/spec.md
  02.modules/01.md ... 10.md
  03.prototype.style/selection.md
  03.prototype.html/*.html              # HTML mode
  03.prototype.prompt/*.md               # image mode
  04.prototype/batch.json、*.jpg
  05.code/01-模块名称.txt ... 10-模块名称.txt
  06.document/{软件名称}_操作手册.md/.docx
  或 06.document/{软件名称}_软件设计说明书.md/.docx
  07.code.full/{软件名称}_代码.docx
  08.application-info/{软件名称}_软著申请表信息.txt
  09.originality-audit/source-manifest.json
  09.originality-audit/originality-report.json
  09.originality-audit/originality-report.md
```

`01` through `08` are formal materials. `09` is internal quality-control material and is never merged into a submitted document.

## Modes

- `normal`: create a new complete material set.
- `correction`: read the correction notice and existing materials, create a new timestamped output root, and rebuild the representative program and document without overwriting the originals.

Correction mode must perform substantive source selection and document restructuring. Renaming variables, replacing synonyms or shuffling sections is not sufficient.

## Numbering

- `02.modules` contains exactly `01.md` through `10.md`.
- `05.code` contains exactly ten `编号-模块名称.txt` files.
- Module ids remain consistent across modules, code, manifest and any module-specific prototypes.
- At least eight module names are domain-specific; generic support modules total no more than two.
- Code-file lengths may differ substantially. Only the total minimum of 3000 nonblank source lines is fixed.

## Selected document

Write one primary identification document under `06.document`:

- operation manual for interaction-heavy products or an explicit user request;
- software design specification for algorithm/backend/data/device products;
- the more representative type when correcting a template-like document, with design specification preferred when the distinguishing expression is internal processing logic.

Generate exactly one selected document for each material set.

Do not create a `.draft.md` formal artifact. Any temporary working text must remain outside the formal output tree or be removed before delivery.

## DOCX typography

Without a user template, `markdown_to_docx.py` uses A4 pages, SimSun/宋体 10.5 pt for Chinese body text, Times New Roman for Latin text and numbers, SimHei/黑体 for Chinese headings, and Arial for Latin headings. The converter must set `w:eastAsia`, `w:ascii` and `w:hAnsi` explicitly; renderer-dependent font fallback is not an acceptable formatting strategy. Lists use Word list styles, and tables use fixed widths, cell padding and explicit borders.

When a template is supplied or discovered, it remains the source for existing cover and layout content. Generated body styles are normalized to the typography above so an unrelated theme font cannot leak into the formal document.

## Prototype contract

Operation manuals use ten module overview images and representative complex function images. Add `00-login` only when the software has an authentication flow; otherwise use the real entry or task-start screen and pass `--no-login` to prototype scripts and validation. Design specifications use only visuals that materially explain system architecture, processing flows, states, data relationships or actual processing results.

`04.prototype/batch.json` remains the resumable manifest for generated images. Every item includes `id`, `mode`, `module`, `html` or `prompt`, `output`, retry information and status.

## Source manifest

`09.originality-audit/source-manifest.json` defines the source concatenation order. Its `files` list must match all ten files under `05.code`, use safe relative paths and carry current SHA-256 fingerprints. The code-document builder uses this order, not an independently invented order.

## Quality gate

Run `audit_originality.py` after code and document generation and before building the code DOCX. A failing report blocks final delivery. After any source change, rerun the audit so the report fingerprints remain current.

The audit's similarity thresholds are internal heuristics. Formal materials must not refer to them or to the generation process.

## Reference-directory resolution

Search `reference`, `refence` and `refrence` under the output root, current directory and `~/aj-skills`, in that order. Do not rename the user's directories.

## Step boundaries

Do not silently fabricate a downstream artifact when a required dependency or upstream result is missing. Report the exact missing dependency or file. Missing a user template is not blocking: produce a correctly formatted DOCX without the template and record that fact in the final response.

## Delivery summary

Report only:

- output root;
- selected document type;
- selected technology stack;
- core formal files;
- template usage;
- audit and validation result;
- concrete unfinished or blocked items.
