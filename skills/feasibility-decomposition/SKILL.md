---
name: feasibility-decomposition
description: Deep feasibility analysis and structured decomposition of a concept/proposal/设想 against a reference framework (a policy, standard, plan, or spec). Produces (1) an alignment mapping matrix that surfaces coverage gaps, (2) a multi-dimensional feasibility assessment (technical / organizational / compliance / economic) with ratings and the domain's killer constraints, (3) value/highlights framed for award or funding applications, (4) a methodology-driven decomposition (default: the V字模型 with 业务协同模型 + 数据共享模型 double-through), and (5) standardized delivery checklists (business functions, data dependency & sharing, infrastructure, reform/transformation items). Use this whenever the user wants to 可行性分析 a 课题/设想/方案/产品 against a 政策框架/标准/规划/行业规范, do 数字化改革拆解, produce 业务功能清单/数据依赖及共享清单/基础设施依赖清单/改革变革项清单 for 课题申报/奖项申报/项目立项/可研/初设, or apply the V字模型/业务协同模型/数据共享模型. Trigger even when the user does not name the methodology — any request like "深度分析这个设想的可行性并拆解成清单", "对标 XX 框架/政策做拆解", "把这个课题按数字化改革拆解", or "帮我准备申报材料" qualifies. Also use for analogous tasks outside digital reform: any "concept measured against a framework, then feasibility + structured breakdown + checklists" request.
---

# Feasibility Analysis & Structured Decomposition

You are given a **concept** (设想 / 课题方案 / 产品构想 / 方案) and a **reference framework** (政策 / 行动计划 / 标准 / 规划 / 规范 / 技术规格) to align it against. Your job is to turn the two into a rigorous, decision-grade deliverable: *is this concept feasible, how does it map to the framework, where are the gaps, what's award-worthy, and what exactly must be built/reformed — broken down into concrete checklists.*

This is a thinking-and-writing skill. The quality bar is high: outputs are typically used for 课题申报 / 奖项申报 / 立项可研, where vague analysis fails and where a single missed compliance red-line or coverage gap can sink the whole application.

## The one-line method

> **设想 × 框架 → 对齐 → 可行性 → 亮点 → 拆解 → 清单**

Walk the seven phases below. Each phase exists for a specific reason — don't skip, because later phases depend on earlier findings (gaps feed feasibility, feasibility feeds highlights, both feed decomposition).

## Before you start: ingest and verify (do not hallucinate the framework)

1. **Read the concept.** If it's a `.docx`, extract text (a `.docx` is a zip; `word/document.xml` holds the text — a small Python `zipfile` + `xml.etree` snippet works, or use the `docx` skill). If `.pdf`, read it. If described inline, use that. Restate it crisply in your own words so you've actually understood it.
2. **Fetch and verify the framework.** This matters more than people think. **Do not reconstruct a policy/standard from memory** — fetch the real source. If a URL is given, read it (web reader / fetch). If the direct fetch is filtered or fails, fall back to web search to recover the framework's actual structure and requirements, and cite the source. Misquoting a national policy in a 申报 material is an unrecoverable error. When you cite a requirement, **mark whether you verified it against the source (cite 文号 / 条款号 / URL) or are assuming it from the user's summary** — don't blur the two. A reviewer who checks a phantom clause is a fatal error, so keep what's nailed-down visibly distinct from what's provisional.
3. **Bound the scope.** If the concept or framework is ambiguous (e.g., "is this for the whole city or one school?"), ask one focused clarifying question. Don't rabbit-hole on many questions — most can be resolved with a sensible default that you state explicitly and move on.

## Phase 1 — Alignment mapping (对标对齐)

Build an **alignment matrix**: the framework's requirements/dimensions down the rows, the concept's coverage across the columns, each cell scored for coverage (e.g., ★★★★★ strong / ★★★☆☆ partial / ☆☆☆☆☆ gap), with a final column for *gap + recommendation*.

Why this comes first: the alignment matrix is where **coverage gaps** surface, and gaps are the most common reason an application loses points or a project fails review. Finding "the framework requires X but the concept doesn't address it at all" early lets you either close it (recommend adding it) or flag it as a known limitation — both are far better than the reviewer finding it for you.

Always end Phase 1 with 2–3 **headline conclusions** (strategic fit level, the must-close gaps, the standout alignment that becomes a highlight).

## Phase 2 — Feasibility, deep and multi-dimensional

Assess feasibility across at least four dimensions, each with an explicit rating and a one-line judgment. Read **`references/feasibility-rubric.md`** for the full rubric, the rating scale, and how to find the **killer constraint** of the domain.

The dimensions (adapt/extend to the domain):
- **Technical** — by architecture layer or component; what's mature vs. needs R&D.
- **Organizational / operational** — who must cooperate, is that cooperation sustainable, where's the human bottleneck.
- **Compliance & ethics** — the **most under-weighted and most fatal** dimension. For minors + health data, for finance, for safety-critical systems, this is where projects die. Name the specific laws/standards and the specific red-line.
- **Economic / sustainability** — cost vs. budget, cold-start problem, who pays ongoing.

The single most valuable habit in this phase: **find the domain's killer constraint** — the one thing that, if unresolved, makes everything else moot (e.g., AI output crossing into 诊断/诊疗 triggers medical-device regulation; a self-improving "flywheel" can't cold-start without enough data). State it plainly and give the de-risking move. When the killer constraint is a binary design choice ("does this feature cross a regulated line?"), present the de-risking as a **structured either/or**: Path A (stay outside the constraint — what you give up) vs Path B (accept the constraint — what it costs in time/money/scope), with a recommendation. A forced decision is far more useful to the reader than scattered mitigation hints.

End with a **feasibility verdict table** (per-module rating + one-line定性).

## Phase 3 — Highlights / value framing (亮点提炼)

Frame the concept's strengths in the language evaluators actually use. The reliable four lenses:
- **Policy fit (政策契合)** — how it advances the framework's goals, especially any *source-stage / upstream* positioning others miss.
- **Model innovation (模式创新)** — what structural collaboration or closed-loop is novel vs. the framework's own mechanism.
- **Technical advancement (技术先进性)** — the hardest-to-copy capability.
- **Measurable outcomes (成效可量化)** — anchor to the framework's own quantitative targets where possible (e.g., its 2030 KPIs).

Plus two that consistently differentiate winners: **replicability / standardization** (can others copy this path?) and **ethics/compliance leadership** (did they solve the hard governance problem others ignore?).

For each highlight, give the one-line claim AND the concrete evidence that would prove it (an indicator, a number, a artifact). A highlight with no proof is filler. **At least one highlight must be anchored to a quantitative target** — ideally the framework's own KPI (its 2030 target, a coverage rate, a decline percentage, a budget threshold). "Aligns with national policy" with no number attached is not a highlight.

## Phase 4 — Methodology-driven decomposition (结构化拆解)

Apply a structured decomposition that threads **two models** through every part of the work. The **default methodology is the V字模型** (浙江数字化改革): self-top-down decomposition + self-bottom-up integration, with the **业务协同模型 (business collaboration)** and **数据共享模型 (data sharing)** as the twin spines running through the whole V. Read **`references/decomposition-and-checklists.md`** for the V字模型 step-by-step and the adaptation rules.

Why two models, not one: business collaboration answers *"who does what, when, reformed how"*; data sharing answers *"what data, from whom, shared how, governed how."* In reform projects these two are inseparable — a beautiful workflow with no data pathway is fiction, and a data lake with no reformed workflow is a graveyard. Threading both is what separates 数字化改革 from mere 信息化, and it's where the "reform gold content" (改革含金量) lives that award panels look for.

**Adapt when the task is NOT digital reform.** If the framework is an industry standard, a technical spec, a compliance regime, or a research methodology, do not force the V字模型. Instead use that domain's native decomposition (e.g., a spec's clause structure, a standard's requirement categories, a methodology's stages). The constant is: decompose the concept into buildable/verifiable units along **two complementary axes** (one process/workflow axis + one data/information axis), threaded through every phase. See the adaptation box in the reference.

## Phase 5 — Standardized delivery checklists (标准化清单)

Produce the checklists the decomposition implies. The **default set (digital reform / 课题申报 context) is four lists**:
1. **业务功能清单** (business functions) — id, name, layer, description, role, trigger, related data.
2. **数据依赖及共享清单** (data dependency & sharing) — entity, items, source, collection method, sharing parties & purpose, frequency, sensitivity, compliance.
3. **基础设施依赖清单** (infrastructure) — by layer (sensing / network / compute-storage / platform-AI / integration / portal / security).
4. **改革变革项清单** (reform & transformation) — by category (制度重塑 / 流程再造 / 规则重构 / 机制创新 / 标准规范), each with what it breaks from the old mechanism.

Each list is a markdown table. Full column schemas and adaptation rules (how to change the four categories when the framework isn't digital reform) are in **`references/decomposition-and-checklists.md`**, and the complete document skeleton including every table is in **`references/output-template.md`**.

Why four lists and not one: they map cleanly to the questions every reviewer/PM asks — *what does it do (functions), what data does it need and from whom (data), what must we buy/build (infrastructure), and what rules/must we change to make it real (reform).* A project that lists features but no reform items is IT, not reform.

## Phase 6 — Risks & phasing (optional but recommended)

Close with a one-page **risk countermeasure table** (risk / level / mitigation) and a **phased rollout** (phases with period, focus, exit goal). Phasing especially matters when the concept has self-improving/learning components that cannot cold-start — sequence them behind a manual/half-auto phase until data volume crosses the threshold.

## Output

Produce **one markdown file** named descriptively (e.g., `<concept>_可行性分析与拆解.md`), placed in the working directory, following **`references/output-template.md`**. After writing, give the user a tight summary of the headline findings (the gaps, the killer constraint, the top highlights, the list counts) and offer 2–3 concrete next steps (convert to Word/PDF, deepen one list into a 可研/初设 table, design the indicator system). Offer; don't auto-do.

## Quality bar — what separates a great run from a mediocre one

- **The framework is real, not invented.** Cite it. If you couldn't fully verify a requirement, say so.
- **Gaps are named, not hidden.** A gap you surface is a problem you're helping solve; a gap the reviewer finds is a failure.
- **The killer constraint is identified.** Every domain has one. Find it.
- **Feasibility is rated, not vibes.** Use the scale. A reader should see at a glance what's green, what's yellow, what's red.
- **Reform items exist when the context is reform.** No 改革变革项 = you did IT planning, not reform planning.
- **Highlights have proof.** Claim + evidence, always paired.
- **Two models threaded, not bolted on.** Business collaboration and data sharing appear in *every* phase, not just one section.

## When to deviate

If the user only wants part of this (just feasibility, or just one list), do that part well rather than forcing the full seven phases — but say what you're omitting by **enumerating the omitted components by name with a reason**. For example: "omitted — V字模型 decomposition, the business-function / data / infrastructure lists, and the highlights section, because the classification path must be decided before function lists are meaningful." Naming ≥2 omitted components with a rationale is far more useful than "I'll keep it short" — it tells the reader exactly what's missing so they can ask for it.
