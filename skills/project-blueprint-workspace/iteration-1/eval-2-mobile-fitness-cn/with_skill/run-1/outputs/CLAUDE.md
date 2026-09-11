# Claude Code project guidance

Read [ENGINEERING.md](ENGINEERING.md), then route to [PRD.md](PRD.md), [SPEC.md](SPEC.md)/`specs/`, [DESIGN.md](DESIGN.md), [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), or [DEPLOY.md](DEPLOY.md) according to the change.

- Surface conflicts and high-impact assumptions before coding.
- Keep changes traceable and scoped; do not silently alter observable behavior.
- Preserve the modular monolith, PostgreSQL source of truth, private object access, and server-side authorization boundaries.
- Never log OTPs, tokens, phone numbers, photo URLs/content, or request bodies.
- Run the exact applicable commands from `ENGINEERING.md`; provisional placeholder commands must be confirmed in the repository before relying on them.

