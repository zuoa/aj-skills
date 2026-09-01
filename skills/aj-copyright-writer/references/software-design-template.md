# Software Design Specification Guide

Use this guide when the selected identification document is a software design specification. It is appropriate for software whose representative expression lies in algorithms, backend processing, data flows, protocols, devices, stateful workflows or complex business rules. The result must read as a self-contained engineering document, not as an explanation of how registration materials or source excerpts were assembled.

## Design baseline

Before drafting, reconcile the specification, ten module definitions, source manifest, source text and any interface or prototype material. Establish an internal trace ledger containing the actual domain terms, entities, fields, states, rules, interfaces, components and implementation symbols. Use this ledger to keep the document accurate, but never paste its workflow paths, numbered package filenames or generation notes into the formal document.

If the supplied evidence does not support a technical claim, narrow the claim. Do not invent services, tables, algorithms, performance figures, deployment nodes or security mechanisms merely to make the document appear complete.

## Document architecture

Choose and order only the sections that explain the software's actual design. A strong design specification normally covers these viewpoints:

1. purpose, scope, intended readers and terminology;
2. design objectives, business constraints and significant quality attributes;
3. system context, external actors and boundary systems;
4. overall architecture, component responsibilities and data movement;
5. domain model, identifiers, relationships and lifecycle states;
6. representative processing mechanisms, algorithms or rule decisions;
7. interface contracts, message semantics and integration boundaries;
8. data consistency, validation, concurrency, idempotency and recovery;
9. permissions, security, audit and traceability;
10. deployment topology, runtime dependencies and observability;
11. optional design—implementation traceability appendix.

These are design viewpoints, not a fill-in template. Merge, rename, reorder or omit sections when the software does not need them. Do not turn the ten delivery modules into ten chapters with identical subsections.

## Architecture and component design

Explain why the chosen decomposition fits the software's business and operational constraints. For each important component, state its responsibility, owned data, upstream and downstream dependencies, boundary conditions and failure isolation behavior. Describe the path of a representative request, event or data batch across components.

Avoid a generic presentation/controller/service/repository inventory unless the document also explains the software-specific responsibilities and data movement at each boundary. Technology names belong in the architecture only where they affect design decisions, runtime behavior or interfaces.

## Domain and data design

Use the software's real business concepts. Identify aggregate roots or primary records, business identifiers, key fields, value ranges, relationships, uniqueness constraints, retention needs and lifecycle rules. A field list alone is not a data design: explain which component owns each record, when it changes and which invariants must always hold.

When a table or entity diagram adds clarity, keep it focused on relationships and constraints. Do not dump a database schema, ORM model or universal fields such as `name`, `type`, `status` and `createdTime` as a substitute for domain analysis.

## Processing, rules and algorithms

Organize core chapters around representative mechanisms rather than code files. A design discussion should make clear:

- the business purpose and trigger;
- normalized inputs, units, allowed values and freshness requirements;
- preconditions and invariants;
- the main sequence and responsibility boundaries;
- decision branches, thresholds, ordering and tie-breaking;
- outputs, persisted changes and downstream use;
- invalid, missing, stale, duplicate or conflicting input handling;
- timeout, partial-failure, retry, rollback or compensation behavior;
- audit events and operational signals produced by the process.

Use a state table, decision table, sequence diagram, data-flow diagram or worked calculation when it communicates the mechanism more precisely than prose. Do not claim that an ordinary formula or rule set is proprietary, advanced or intelligent; show its concrete behavior instead.

## State and workflow design

Name states in business language. For each transition, identify the initiating role or event, guard conditions, records written after success, side effects, blocked transitions and recovery action. Avoid generic `pending / success / failed` states when the domain has more precise lifecycle meanings.

State machines must distinguish business rejection from technical failure. Explain concurrency control where two actors or events can update the same record, and define the result of duplicate or out-of-order events.

## Interface and integration design

Include only interfaces that expose representative behavior. For each interface, state the caller, business purpose, protocol or invocation mode, key request fields, response semantics, validation, authorization, idempotency rule, timeout and failure response. Describe message correlation, version compatibility or ordering only when relevant.

Avoid pages of standard CRUD endpoints. Do not reproduce controller annotations or generated API documentation as design content.

## Reliability, security and runtime design

Tie non-functional design to concrete risks. Describe transaction boundaries, durable records, retries, deduplication, compensation, degradation and observability for the software's critical paths. Explain permission decisions using real roles and business resources. State what security or audit record is written, who may query it and how it supports incident or business traceability.

Deployment content should identify runtime components, network boundaries, storage, queues, device gateways or scheduled jobs that actually exist. Do not add a generic cloud topology or performance target unsupported by the source and specification.

## Design—implementation traceability

The formal body must remain readable without source-code commentary. Never end each section with a generated-looking mapping sentence. The following forms are prohibited:

```text
本节设计由 01-种鹅个体档案与RFID身份管理.py 落地。
对应源程序文件：异常追溯链构建
本模块代码位于 05.code/03-……
```

Do not expose:

- internal directories such as `05.code`;
- numbered delivery-package filenames such as `01-……`;
- `.py`, `.java`, `.go`, `.txt` or other file extensions;
- wording such as `由……落地`, `对应源程序文件` or `本节实现于`;
- implementation mapping repeated mechanically after every chapter.

When implementation traceability materially improves the document, add one concise appendix titled `设计—实现追踪表`. Use professional logical identifiers and verified implementation symbols:

| 设计单元 | 实现组件 | 核心类或服务 | 关键入口 |
| --- | --- | --- | --- |
| RFID 身份绑定 | 个体身份服务 | `RfidIdentityService` | `bindTag`、`verifyUniqueBinding` |
| 异常追溯链生成 | 追溯链编排器 | `TraceChainService` | `buildTraceChain`、`resolveMissingHop` |

The component, type and method names must exist in the source manifest and source text. For languages without classes, use a stable package/module identifier without an extension plus the verified function name. Omit the appendix if the available source cannot support accurate symbol-level traceability.

## Professional writing standard

Write as if one developer is explaining the system to another developer who will maintain it. Start with the record, event or component being discussed. Then state the condition, action and result. Prefer explicit subjects and verifiable behavior: `身份服务在写入绑定关系前检查 RFID 标签与个体编号的唯一性` is stronger than `通过 RFID 技术赋能档案管理`.

Avoid promotional or process language such as `本系统旨在`, `致力于`, `赋能`, `打造`, `全面提升`, `形成闭环`, `提供有力支撑`, `本文将`, `为体现代表性` and `根据源码生成`. `确保稳定性` is not a design statement; state what is retried, what is persisted and what happens after the retry limit instead.

Do not force an introduction and summary around each mechanism. Two concrete paragraphs are better than five paragraphs that restate the heading. Vary sentence length naturally, but do not manufacture rhetorical variety with `此外`, `从而` or `不仅……而且……`.

Use terminology consistently. Define an abbreviation once, then keep the same Chinese term, English term and identifier throughout. Distinguish business concepts, logical components, deployment units and implementation symbols instead of calling all of them `模块`.

After technical review, apply [design-specification-humanizer.md](design-specification-humanizer.md) to the completed Markdown. This is an editing pass, not a new drafting pass: preserve verified facts and remove filler.

## Visual and layout guidance

Use visuals only when they add technical evidence: system context, component interaction, domain relationships, lifecycle states, data flow, deployment topology or a representative processing result. Give every figure a concrete caption and explain the significant relationships in surrounding text. Avoid decorative dashboards, generic architecture icons and screenshots that merely repeat prose.

Use tables for comparable records such as interface contracts, states, decision rules and traceability. Do not put long narrative paragraphs into cells. Keep the body text as the primary explanation.

## Final checks

- The document explains this software's design decisions and could not be reused by changing only the product name.
- Architecture, domain objects, fields, states, interfaces and rules agree with the specification and source program.
- Representative mechanisms include preconditions, decisions, state or data effects, failure paths and recovery behavior.
- All ten business modules are covered by the design viewpoints, without forcing ten identical chapter skeletons.
- No formal paragraph exposes workflow directories, numbered package filenames, file extensions or generated source-mapping sentences.
- Any design—implementation traceability appears once, uses verified logical components and symbols, and reads as an appendix rather than source commentary.
- The formal document contains no assumptions, audit language, placeholders, drafting notes or claims unsupported by evidence.
