# Security and deployment guidance

## Risk-profile first

Increase depth when the project has authentication, payments, sensitive/personal data, multi-tenancy, public uploads, admin tools, regulated workflows, third-party scripts, AI, or cross-border data. Even a low-risk project still needs dependency, secret, backup, and incident ownership decisions.

## SECURITY.md

Record:

- Data inventory, classification, controller/owner, purpose, retention, deletion and residency.
- Context/data-flow trust boundaries and abuse cases.
- Human and machine identity; authentication, session, authorization, tenant isolation and privileged access.
- Encryption in transit/at rest, key ownership/rotation and secret handling.
- Input/output validation, upload handling, rate limiting and audit events.
- Dependency provenance, lockfiles, vulnerability scanning, supported runtimes and update responsibility.
- Security verification mapped to risk: code review, automated checks, threat review, penetration test, remediation SLA.
- Detection, response contacts, evidence preservation, notification and learning loop.

Use NIST SSDF and OWASP ASVS as checklists appropriate to the project risk, not as claims of certification.

## DEPLOY.md

### Environment and artifact

- Local, preview, test/staging and production purpose; data and access rules for each.
- Build once, promote the same immutable artifact where feasible.
- Runtime, region, network boundaries, data stores, scheduled/background jobs and external dependencies.
- Configuration schema, secrets provider, rotation and break-glass access.

### Delivery

- Version control and CI quality gates.
- Database migration compatibility, backfill, expand/contract sequence and rollback limits.
- Release strategy: rolling, blue/green, canary, feature flag, mobile staged rollout.
- Automated rollback signal and manual recovery procedure.

### Operability

- User-centered SLI/SLO and alert owner; avoid alerting on every available metric.
- Structured logs, metrics, traces, audit logs, correlation IDs and retention.
- Dependency health, synthetic checks, dashboards, incident severity and escalation.
- Backup scope, encryption, retention and tested restore; RTO/RPO per system/data class.
- Capacity and cost drivers, budget alerts, tagging/allocation and decommission path.
- Domain, DNS, TLS/cert renewal and status/communication channel.

### Mobile release

- Bundle/application identifiers, signing ownership and protected credentials.
- Store environments, review requirements, metadata/privacy declarations and release tracks.
- Backend compatibility window, minimum supported app version and emergency rollback/disable strategy.

## Production gate evidence

A statement such as “daily backups” is incomplete without restore ownership and test evidence. A statement such as “monitor with X” is incomplete without user-visible signals, thresholds, routing, and response. Mark the production gate blocked when a failure can cause unrecoverable data loss, uncontrolled access, or an unowned incident.
