# Regional, compliance, and AI branches

This file routes questions; it is not a static legal opinion. Requirements change. Verify current facts against official regulators, platform owners, and service documentation, record the access date, and recommend specialist review when consequences are material.

## China mainland branch

Confirm early:

- Whether the service is publicly accessible in mainland China and who owns the domain/service entity.
- Hosting region, ICP/public-security filing implications, licensed business categories and store/mini-program channels.
- Personal and sensitive personal information, minors, consent/notice, SDK inventory, permissions, retention/deletion and user rights.
- Data residency, cross-border transfer, processors/subprocessors and incident obligations.
- Real-name, content governance, algorithm/deep-synthesis/generative-AI or sector rules when triggered.
- Domestic SMS, payment, map, push, CDN and cloud-provider constraints and exit paths.

Use official Chinese government/regulator domains for current legal facts. Treat cloud vendor summaries as implementation guidance, not legal authority.

## Global branch

Confirm target countries rather than treating “global” as one jurisdiction:

- Privacy roles, lawful basis/notice/consent, data subject rights, retention and processor agreements.
- Data regions and transfer mechanisms.
- Accessibility, payments/tax, consumer/subscription, age/minors, content and sector obligations.
- Store rules, export/sanctions and third-party service availability when applicable.

Route legal facts to the responsible jurisdiction's regulator or official statutory source. Record uncertainty and owner.

## Cross-market design

- Keep regional behavior differences explicit in PRD/SPEC.
- Keep data topology and provider differences in ARCHITECTURE/DEPLOY.
- Keep notices, controls and verification in SECURITY.
- Decide whether one product behavior, regional feature flags, or separate deployments are intended.

## AI/LLM branch

Only load this branch when AI is in scope. Confirm:

### Product and behavior

- User value and which decisions remain human-owned.
- Model output contract, uncertainty display, refusal/fallback and user correction.
- Offline evaluation set, quality threshold, prohibited outcomes and release gate.

### Data and security

- Prompt/context sources, personal/confidential data, retention and training-use policy.
- Retrieval/index ownership, deletion propagation, prompt injection, data exfiltration and tool permissions.
- Provider region, subprocessors, logging, moderation and incident handling.

### Architecture and operations

- Provider/model selection constraints, portability and version pinning.
- Latency/token/cost budgets, caching and rate limits.
- Timeout, retry, circuit breaker, deterministic fallback and model/provider degradation.
- Prompt/model/evaluation version traceability and production quality monitoring.

Do not claim that an LLM behavior is guaranteed merely because a prompt requests it. Put critical controls outside probabilistic model output where possible.
