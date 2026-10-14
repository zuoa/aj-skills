# Coding agent project guidance

Use [ENGINEERING.md](ENGINEERING.md) as the agent-neutral source for workflow, commands, code rules, tests, and definition of done.

Read project intent and constraints from:

- [PRD.md](PRD.md) for product scope and outcomes
- [SPEC.md](SPEC.md) for scope, `openspec/specs/` for implemented behavior, and selected `openspec/changes/` for proposed work
- [DESIGN.md](DESIGN.md) for UI/UX constraints
- [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries and internal design
- [SECURITY.md](SECURITY.md) for security/privacy controls
- [DEPLOY.md](DEPLOY.md) for delivery and operations
- `docs/adr/` for durable decisions

Before changing code, expose material assumptions and conflicts. Implement the smallest scoped change that satisfies the confirmed specification, then run the applicable checks from `ENGINEERING.md`. Do not silently change behavior when the blueprint and request disagree.

For OpenSpec, start from root SPEC’s current_changes and the assigned change’s proposal, delta specs, technical design.md and numbered tasks.md. Root DESIGN.md owns visual constraints. Read applicable contracts and project sources; execute in dependency order and record actual scenario evidence before claiming acceptance. Do not automatically relax scenarios to fit failed code. Validate with OpenSpec; sync/archive only after implementation and verification. ENGINEERING owns the detailed workflow.
