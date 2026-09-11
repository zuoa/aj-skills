# Coding agent project guidance

Use [ENGINEERING.md](ENGINEERING.md) as the agent-neutral source for workflow, commands, code rules, tests, and definition of done.

Read project intent and constraints from:

- [PRD.md](PRD.md) for product scope and outcomes
- [SPEC.md](SPEC.md) plus `specs/` for observable behavior
- [DESIGN.md](DESIGN.md) for UI/UX constraints
- [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries and internal design
- [SECURITY.md](SECURITY.md) for security/privacy controls
- [DEPLOY.md](DEPLOY.md) for delivery and operations
- `docs/adr/` for durable decisions

Before changing code, expose material assumptions and conflicts. Implement the smallest scoped change that satisfies the confirmed specification, then run the applicable checks from `ENGINEERING.md`. Do not silently change behavior when the blueprint and request disagree.
