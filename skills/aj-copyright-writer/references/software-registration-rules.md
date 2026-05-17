# Software Registration Rules

Use this reference when writing `01.spec/spec.md`, operation manuals and source-code materials for Chinese computer software copyright registration.

Primary legal source:

- 《计算机软件著作权登记办法》，中华人民共和国国家版权局令第 1 号，2002-02-20 发布。
- Public mirror: https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/content/post_8965812.html

## Hard Material Constraints

The application material set generally includes:

- Software copyright registration application form.
- Identification materials of the software.
- Relevant proof documents.

The software identification materials include:

- Program identification materials.
- Documentation identification materials.

For ordinary deposit:

- Source program and documentation are formed from the first and last continuous 30 pages.
- If the whole program or document is fewer than 60 pages, submit the whole program or document.
- Unless a special rule applies, each program page should have at least 50 lines, and each documentation page should have at least 30 lines.

Other relevant points:

- Registration software should be independently developed, or be an authorized derivative with important functional or performance improvements.
- Application documents should use Chinese; foreign-language certificates or proof documents should include Chinese translations.
- Application files use A4 paper format.
- Software name and right-holder names must stay consistent across application files unless supporting proof is provided.

## Implications for This Skill

When the user has real code or manuals:

- Prefer extracting and formatting real materials instead of inventing replacement code.
- Preserve actual module names, version names and right-holder naming.

When the user only provides a software name:

- Generated code and manuals are draft application materials.
- State in `01.spec/spec.md` that unverifiable content is an expanded business setting.
- The applicant must verify the materials against the actual software before filing.

For `07.code.full/${SOFTWARE_NAME}_代码.docx`:

- Keep module order stable and source-like.
- Include enough business logic to show software expression.
- Do not create placeholder-only source files.

For `06.manual/*_操作手册.docx`:

- Use operation steps and screenshots to show a concrete operable product.
- Keep the document consistent with module names, screenshots and code files.
