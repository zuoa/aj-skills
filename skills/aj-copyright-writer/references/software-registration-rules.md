# Software Registration Rules

Primary source: 《计算机软件著作权登记办法》（国家版权局令第 1 号）。 Official page: https://www.ncac.gov.cn/xxfb/flfg/bmgz/202410/t20241015_869486.html

Related source: 《计算机软件保护条例》. Official page: https://xzfg.moj.gov.cn/front/law/detail?LawID=914

## Hard material rules

- Registration materials include the application form, software identification materials and relevant proof documents.
- Identification materials include a source program and any one kind of related document.
- For ordinary deposit, submit the first and last continuous 30 pages of the source program and document. If either complete material is fewer than 60 pages, submit it in full.
- Unless a special rule applies, each program page contains at least 50 lines and each document page at least 30 lines.
- The registered software must be independently developed, or be an authorized modification with important functional or performance improvements.
- Names of the software and right holder must remain consistent across application materials.
- Application files use Chinese and A4 paper.
- A requested correction must be submitted within the specified period; Article 22 states 30 days for corrections requested by the registration institution.

## Exceptional deposit

Article 12 permits the specified exceptional-deposit methods, including the first continuous 10 source pages plus any continuous 50 source pages. Do not describe arbitrary fragment stitching as continuous deposit. Use an exceptional method only when the applicant intentionally selects it and the material is organized accordingly.

## Implications for this skill

- Prefer actual project source and documentation when supplied.
- When generating from a software name, produce one internally coherent software expression rather than unrelated snippets.
- Use a stable manifest order to define the submitted source stream, then take the first and last continuous portions from that stream.
- Keep required imports inside selected business files; exclude low-value standalone files instead of damaging program coherence.
- Select the one document type that best demonstrates the software: an operation manual for distinctive interaction flows or a design specification for distinctive processing logic.
- Do not present internal similarity thresholds as registration rules; the authority has not published a universal “template percentage” threshold.

## Code document

- exactly 60 pages when the source stream is long enough;
- 50 source lines per page;
- first 1500 and last 1500 lines from the ordered stream when the stream exceeds 3000 lines;
- name and version in the header, page number at upper right;
- A4, SimSun/宋体 9 pt, left aligned and single spaced;
- no covers, directories or generated-material explanations between code lines.

## Selected document

The related document may describe content, composition, design, functional specifications, development, testing or use. Choose the operation manual or software design specification whose expression corresponds most directly to the submitted program. Generate exactly one selected document and ensure its final Word form corresponds to the submitted program and meets the applicable page and line rules before filing.

## Legal-quality boundary

The skill improves material quality and consistency; it does not invent an official similarity threshold or guarantee an administrative outcome. Formal output itself should contain only the software material, while these process notes remain in the skill instructions.
