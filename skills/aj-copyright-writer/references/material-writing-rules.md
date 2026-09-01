# Material Writing Rules

Use these rules for the specification, ten modules, source program, selected identification document, prototypes and application information.

## Formal-material boundary

Files under `01.spec` through `08.application-info` are formal deliverables. They must describe the software directly and must not contain process labels such as “本文为草案”, “AI 生成”, “模板化材料”, “基于推断扩展” or internal-audit results. Preserve legitimate product names and business terms such as `AI 合同审查` or `合同模板`.

## `01.spec/spec.md`

Use a product-specific structure covering:

- software purpose and target users;
- end-to-end business flows;
- roles and operational boundaries;
- coherent technical architecture;
- domain entities, fields and status transitions;
- ten core modules;
- validation, exception and recovery rules;
- performance, security and traceability requirements.

Use stable domain terminology that can flow into later artifacts. Do not use internal labels such as `模块01` or prose that explains how the material was created.

## `02.modules/*.md`

Generate exactly ten files. Each uses:

```markdown
# 01. 模块名称

## 模块定位
## 使用角色
## 功能点清单
## 入口与前置条件
## 主流程
## 输入与输出
## 核心数据
## 业务规则
## 异常与边界
## 权限与审计
## 界面要点
## 代码实现重点
```

Each module contains three to five function points. At least eight modules must express domain-specific work. No more than two may be generic support modules such as user, role, permission, dictionary, log, setting or help.

Prefer names such as `冷链温湿度异常追溯`, `合同风险条款定位与批注` and `告警分级处置闭环`. Avoid generic names such as `数据管理`, `信息维护` and `统计分析`.

Each module must define concrete fields, statuses, validation rules and exception branches. Universal field stacks such as `名称 / 编码 / 类型 / 状态 / 创建时间` are insufficient unless supplemented by the software's real domain fields.

The fixed ten-module structure is an internal delivery convention, not an official registration rule. Similarity controls in this skill are internal quality heuristics, not claims about an unpublished review algorithm.

## Technology-stack selection

Use the user's actual stack when supplied. Otherwise choose one coherent stack based on the software:

- workflow and enterprise services: Java/Spring, C#/.NET, Python/FastAPI or Node.js/NestJS;
- data and algorithm engines: Python or C++ with the appropriate service layer;
- device and protocol systems: Go, C/C++, Java or another fitting stack;
- desktop applications: C#/.NET, JavaFX, Qt or Electron when appropriate;
- user-interface-heavy web applications: one backend stack plus one matching frontend stack.

Do not insert multiple unrelated languages merely to look complex. Record detected languages and architectural responsibilities in `source-manifest.json`, and use the same stack in the specification, design document and application information.

## `05.code/*.txt`

Generate exactly ten numbered files, but let architectural and business complexity determine each file's length. A file may contain a domain service, workflow engine, algorithm, protocol handler, repository with meaningful queries, interface adapter or UI workflow. It does not need identical backend and frontend sections.

### Prefer

- state transition and lifecycle logic;
- calculations, matching, scoring and classification;
- non-trivial validation and duplicate detection;
- protocol parsing, data normalization and transformation;
- permission boundaries tied to business roles;
- exception recovery, idempotency and audit trails;
- domain-specific queries and aggregation;
- UI state handling for a real user task.

### Exclude

- import-only, package-only or dependency-only files;
- environment/build configuration and framework bootstrap;
- pure getters/setters and behavior-free DTO/entity files;
- empty methods, interfaces or components;
- TODOs, placeholder returns and fake implementations;
- generated API clients, vendored libraries and framework source;
- repeated CRUD scaffolds that differ only in names;
- padded comments and meaningless duplication.

Do not mechanically strip necessary imports from selected business files. Keep source structure coherent. The ten files must contain at least 3000 nonblank source lines in total; there is no default per-file minimum or maximum. Comments should explain business intent and non-obvious behavior, with no mechanical percentage target.

Source files may retain normal blank lines for readability; line counting and code-DOCX composition ignore them. Source files must not contain the word `copyright`, regardless of case.

## `09.originality-audit/source-manifest.json`

The manifest records the ordered source stream used to build the code document. It includes:

- selected technology stack and business terms;
- file order and relative path;
- module id and module name;
- detected languages and core methods;
- nonblank and low-value line counts;
- SHA-256 fingerprint and selection reason.

The order defines the continuous program stream for the source-code document. Changing source after the audit invalidates the report and blocks DOCX generation.

## Document selection

Follow this precedence:

1. explicit user request;
2. template-like-document correction notice → design specification by default;
3. interaction-heavy product → operation manual;
4. algorithm, backend, data-processing or device-integration product → design specification.

The selected document must cover all ten modules, but it must not repeat one identical paragraph structure ten times.

## Operation manual

Write around real user tasks. Select the composition pattern that matches each function:

- task submission or data entry;
- review and approval loop;
- monitoring and incident response;
- analysis and comparison;
- batch import/export;
- rule configuration and validation.

Vary the explanation according to the task. Include only fields, buttons, statuses and prompts visible in the corresponding prototype. Keep figure numbers increasing and use relative image paths. Do not save a `.draft.md` deliverable.

## Software design specification

Use [software-design-template.md](software-design-template.md). Emphasize the domain model, processing logic, state transitions, algorithm inputs and outputs, interfaces, validation and exception recovery. Explain the relationship between each important design and the corresponding code file without copying source code into prose.

## Prototypes

Use the confirmed industry style. HTML prototypes must be self-contained and use real business fields and states. Avoid generic admin dashboards, empty cards and decorative-only charts.

For an operation manual, create ten module overview pages and dedicated pages for 40%–60% of complex function points. Add a login page only when authentication actually exists; otherwise use the real entry screen and run prototype validation with `--no-login`. For a design specification, create only visuals that prove structure, process or processing results; do not invent low-value screens solely to satisfy a screenshot count.

## `07.code.full/${SOFTWARE_NAME}_代码.docx`

- exactly 60 code pages and 50 source lines per page;
- SimSun/宋体, 9 pt, left aligned, single spacing;
- software name and version in the header, page number at upper right;
- no cover, table of contents, generated-material note or module title page;
- for a stream longer than 3000 lines, use the first 1500 and last 1500 lines in manifest order;
- no blank source lines and no `copyright` text.

## `08.application-info/${SOFTWARE_NAME}_软著申请表信息.txt`

Use values that match the generated program and document. Read languages and source volume from the manifest and code statistics. Keep the established 50/100/200-character field limits, choose one software type, and do not leave instructional placeholders in the file.

Use this field order:

```text
开发的硬件环境
运行的硬件环境
开发该软件的操作系统
软件开发环境 / 开发工具
该软件的运行平台 / 操作系统
软件运行支撑环境 / 支持软件
编程语言    语言：{languages}    版本：{versions}    源程序量    {nonblank_lines} 行
开发目的
面向领域 / 行业
软件的主要功能
软件的技术特点    类型：{one software type}。{technical description}
```

Hardware, operating-system, tool, platform, support, purpose and industry values are each at most 50 characters. Main functions are at most 200 Chinese characters and technical characteristics at most 100. The software type must be one of the types listed in `SKILL.md`.

## Cross-material consistency

Before delivery confirm that:

- all ten module names appear in the selected document;
- code filenames and manifest module ids agree;
- domain fields and statuses agree across spec, code, prototype and document;
- buttons and prompts described by an operation manual appear in screenshots;
- technology stack and source volume agree with application information;
- the originality report is `pass` and its source fingerprints are current.
