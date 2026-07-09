# Feasibility Rubric

Used in Phase 2. Assess feasibility across (at minimum) four dimensions, each rated, then find the domain's killer constraint.

## Rating scale

Use a consistent, scannable scale on every line. The recommended one:

- **★ Mature / ready** — proven tech/process, can build now.
- **◑ Needs engineering work** — feasible but requires real effort (integration, tuning, cold-start, standardization).
- **⚠ Hard constraint / bottleneck** — something external or high-stakes that can block the whole project if not designed around.

The point of symbols over words: a reviewer (or you, re-reading) can scan a column and instantly see where the red is.

## The four dimensions

### 1. Technical feasibility
Break the concept into its architecture layers or major components and rate each. Common layers for a platform/system concept:
- **Data collection / sensing** — devices, instruments, intake channels. Are they mature? What's the cost/accuracy tradeoff?
- **Analysis / intelligence** — models, algorithms, rules. Mature statistics vs. R&D-heavy ML? Small-sample problem? Explainability requirement?
- **Application / workflow** — task flow, mobile/web, recording & feedback. Usually mature; the real constraint is content supply and user adherence, not tech.
- **Resource / scheduling / self-evolution** — knowledge bases, expert routing, learning loops. Watch for cold-start and data-volume thresholds.
- **Integration** — APIs, cross-org data exchange, legacy/heterogeneous systems.

### 2. Organizational / operational feasibility
- Who must cooperate, and is that cooperation *sustainable* (not just willing once)?
- Where's the human bottleneck? (e.g., scarce specialists asked to volunteer time → not sustainable without a funding/incentive mechanism.)
- Are roles, handoffs, and SLAs clear?

### 3. Compliance & ethics feasibility  ← most under-weighted, most fatal
This is where projects die and where most analyses are weakest. Don't generalize — **name the specific laws/standards and the specific red-line.**

Domain red-lines to check (extend as needed):
- **Minors' data** — PIPL-equivalent minor protections: separate consent from guardian, separate storage, strict access (often under-14 = sensitive).
- **Health / medical data** — health data security standards, classification, minimization, de-identification.
- **AI crossing into regulated decisions** — if AI outputs diagnosis/treatment/credit/safety decisions, it may be regulated software (SaMD / algorithmic recommendation / credit-scoring rules). The usual de-risk: **position the system as decision-*support* / education / promotion, never as the decision-maker; all regulated conclusions come from a licensed human, logged.**
- **Data cross-border** — if foreign cloud/AI used, cross-border assessment may apply.
- **Algorithmic fairness** — avoid discriminatory profiling of vulnerable groups.
- **Sector rules** — finance, education, public security, autonomous systems, etc., each have their own.

### 4. Economic / sustainability feasibility
- Build cost vs. budget envelope (rough order of magnitude is fine).
- Ongoing cost: who pays? (A platform with no funding model decays.)
- Cold-start problem: components that need data/volume to work — how do they function before threshold? (Sequence them behind manual phases.)

## Finding the killer constraint

Every domain has **one** constraint that, unresolved, makes the rest moot. Finding it is the highest-value move in the whole analysis. Method:

1. Walk the four dimensions.
2. Ask: *"If this one thing stays unsolved, does the whole concept collapse or become non-compliant?"*
3. That's the killer constraint. State it in one sentence, then give the **de-risking move** (the specific design choice or reform item that neutralizes it).

Examples by domain:
- Child health + AI → "AI generating intervention advice may cross into diagnosis → SaMD regulation. De-risk: position as health-management *support*, all medical conclusions by licensed clinicians, logged."
- Smart elderly care → "consent & data-sharing across family/care home/clinic without a governance framework → legally unusable data. De-risk: data-ownership & sharing rules (a 改革变革项)."
- Credit/finance AI → "model decisions regulated + explainability mandate. De-risk: interpretable models + human-in-the-loop + audit trail."
- Public-safety sensing → "cross-department data sharing is the bottleneck, not the sensors. De-risk: cross-dept data-sharing agreement + minimization."

## Feasibility verdict table (Phase 2 output)

Close Phase 2 with a table like:

| Module | Rating | One-line定性 |
|---|---|---|
| (each layer/component) | ★ / ◑ / ⚠ | … |
| (collaboration mechanism) | ◑ | … |
| (compliance & ethics) | ⚠ | … |

Then the **killer constraint** sentence + de-risking move, called out explicitly.
