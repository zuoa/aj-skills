# Coding agent project guidance

Before coding, read [ENGINEERING.md](ENGINEERING.md) and the authoritative artifact for the task:

- Product intent: [PRD.md](PRD.md)
- Observable behavior: [SPEC.md](SPEC.md) and `specs/`
- UX: [DESIGN.md](DESIGN.md)
- Boundaries: [ARCHITECTURE.md](ARCHITECTURE.md)
- Security/privacy: [SECURITY.md](SECURITY.md)
- Delivery/operations: [DEPLOY.md](DEPLOY.md)

Expose material assumptions and conflicts before implementation. Implement the smallest change satisfying confirmed or explicitly provisional specs. Do not add Redis, a broker, search, microservices, or Kubernetes without an ADR and evidence. Never use production personal data outside production. Run the applicable checks in `ENGINEERING.md`; if behavior conflicts with the blueprint, update PRD/SPEC first.

