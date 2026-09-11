# Claude Code project guidance

Read [ENGINEERING.md](ENGINEERING.md) before implementation. Then read the authoritative document for the task:

- Product intent: [PRD.md](PRD.md)
- Observable behavior: [SPEC.md](SPEC.md) and the linked file under `specs/`
- Experience/UI: [DESIGN.md](DESIGN.md)
- Internal design: [ARCHITECTURE.md](ARCHITECTURE.md)
- Security/privacy: [SECURITY.md](SECURITY.md)
- Delivery/operations: [DEPLOY.md](DEPLOY.md)
- Durable decisions: `docs/adr/`

## Behavior

- Surface assumptions, ambiguity, conflicts, and tradeoffs before coding.
- Prefer the smallest implementation that satisfies the confirmed SPEC.
- Keep changes scoped; do not refactor unrelated code.
- Use the repository commands and verification gates in `ENGINEERING.md`.
- If a requested behavior conflicts with the blueprint, stop and propose the required PRD/SPEC update.

## Commands

- Install: `[canonical command]`
- Test: `[canonical command]`
- Typecheck/lint: `[canonical command]`
- Build: `[canonical command]`
