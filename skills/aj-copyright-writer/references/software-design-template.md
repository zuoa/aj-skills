# Software Design Specification Guide

Use this document when the software's representative expression lies in algorithms, backend processing, data flows, protocols, devices or complex business rules, or when a correction notice identifies the prior document as template-like.

## Composition principle

The design specification should explain how this particular software is organized and how it obtains its results. Use only sections that carry real content; do not pad every module into an identical chapter shape.

The document normally covers:

1. software purpose and design objectives;
2. overall architecture and component responsibilities;
3. domain entities, identifiers and relationships;
4. representative processing flows;
5. state transitions and business invariants;
6. algorithms, rules or protocol processing;
7. interfaces and data exchange;
8. validation, exception recovery and idempotency;
9. security, permissions, audit and traceability;
10. deployment and runtime design;
11. mapping between designs and source-program files.

These are content categories, not a mandatory fill-in template. Merge, reorder or rename sections to fit the software.

## Required specificity

For each representative design, include the concrete business object, input fields, output fields, preconditions, processing decisions, state changes, failure paths and recovery result. Prefer a state table, rule matrix, sequence diagram, data-flow diagram or worked calculation when it communicates the design better than prose.

Do not use universal examples such as `name`, `type`, `status` and `createdTime` without the software's domain fields. Do not describe a generic three-layer architecture unless the responsibilities and data movement are specific to this software.

## Algorithm and rule descriptions

Describe:

- the business reason for the calculation or decision;
- normalized inputs and their units or allowed values;
- decision branches, thresholds, ordering and tie-breaking;
- outputs and how downstream modules consume them;
- invalid, missing, stale or conflicting input handling;
- the code file and core method implementing the design.

Do not claim an algorithm is proprietary, advanced or intelligent merely because it uses a formula or model. Show its concrete expression instead.

## State and workflow descriptions

Name every state with business language. State which role or event may trigger each transition, the conditions that block it, the records written after success and the recovery action after failure. Avoid generic `pending / success / failed` when the domain has more precise states.

## Interface descriptions

Include only interfaces that expose representative behavior. For each, state the caller, business purpose, key request fields, response result, validation, idempotency rule and failure response. Avoid pages of standard CRUD endpoints.

## Code correspondence

End each major design section with a natural source correspondence line. Refer to the source filename, class and method, but do not expose workflow directory names such as `05.code`:

```text
对应源程序文件：异常追溯链构建
对应类与方法：TraceChainService.buildTraceChain、mergeSensorWindow、resolveMissingHop
```

The referenced file and method names must exist in `source-manifest.json` and the source text. Do not paste large source blocks into the document.

## Visual material

Use visuals only when they add evidence: architecture, component interactions, state transitions, domain relationships, representative processing results or a real operational screen. Captions must identify the concrete software behavior shown. Avoid generic dashboards and decorative charts.

## Final checks

- All ten module names are covered somewhere in the document.
- Representative fields, states and rules agree with the source program.
- Each major algorithm or flow maps to an existing code file and method.
- Repeated section skeletons and interchangeable boilerplate have been removed.
- The formal document contains no generation notes, audit language, assumptions or placeholders.
