# Method sources

Use these as reference models, not as a requirement to apply every practice.

## Agent behavior and context

- [Karpathy-inspired Claude Code Guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md): community-authored synthesis of public observations; use the ideas and preserve attribution, do not represent it as Karpathy's own `CLAUDE.md`.
- [Anthropic: Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices): keep project instructions concise, human-readable, versioned, and focused on commands, core files, style, testing and repository behavior.

## Requirements and specification

- [GitHub Spec Kit](https://github.github.com/spec-kit/): Spec → Plan → Tasks → Implement workflow for agentic development.
- [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/overview.md): observable requirements/scenarios, domain specs, and change-oriented evolution.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html): product quality model for eliciting, specifying and evaluating quality requirements.

## Architecture and decisions

- [C4 model](https://c4model.com/): hierarchical context, container, component and supporting deployment/dynamic views.
- [Google Cloud ADR guidance](https://docs.cloud.google.com/architecture/architecture-decision-records): capture options, decision drivers, choice and consequences close to the codebase.
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html): question-based review across operations, security, reliability, performance, cost and sustainability.

## Design, security, and operations

- [VoltAgent awesome-design-md](https://github.com/VoltAgent/awesome-design-md): optional reference analyses for articulating visual language, semantic tokens, component treatments, scoped guardrails and previews. These are community interpretations, not official brand specifications or project approval. Inspected examples and adaptation procedure: [design-reference-workflow.md](design-reference-workflow.md), reviewed 2026-09-18.
- [Nielsen Norman Group: 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/): stable review questions for status visibility, user control, consistency, error prevention, recognition and recovery; treat them as heuristics rather than a visual style.
- [WCAG 2.2](https://www.w3.org/TR/wcag/): testable web accessibility success criteria.
- [W3C H86: text alternatives for emojis and emoticons](https://www.w3.org/WAI/WCAG21/Techniques/html/H86.html): Emoji names may not communicate the intended meaning to assistive technology; provide an appropriate alternative when used.
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines): implementation-oriented checks for semantics, focus, forms, motion, content handling, navigation, touch, locale and performance; adapt copy conventions to the product language.
- [Apple Human Interface Guidelines: Icons](https://developer.apple.com/design/human-interface-guidelines/icons): keep interface icons simple, recognizable, visually consistent and accessible across supported Apple platforms.
- [GOV.UK Design System accessibility strategy](https://design-system.service.gov.uk/accessibility/accessibility-strategy/): accessible components, simple and intuitive use, and testing with assistive technologies.
- [shadcn/ui documentation](https://ui.shadcn.com/docs): React open-code component distribution, theming, supported primitive foundations and framework setup; verify the current foundation instead of assuming an older Radix-only architecture.
- [Radix Primitives accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility): WAI-ARIA patterns, keyboard navigation and focus management for React headless primitives.
- [shadcn-vue introduction](https://www.shadcn-vue.com/docs/introduction): Vue open-code component distribution and customization model.
- [PrimeVue styled mode](https://primevue.org/theming/styled/): Vue styled-suite theme architecture and design-token configuration.
- [Material UI overview](https://mui.com/material-ui/getting-started/): React styled-suite scope, production component coverage and customization model.
- [Element Plus guide](https://element-plus.org/en-US/guide/quickstart): Vue 3 component-suite setup and import strategies.
- [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final): secure development practices integrated across the lifecycle.
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/): application security requirements and verification guidance.
- [The Twelve-Factor App](https://12factor.net/): portable SaaS configuration and operational principles; apply selectively because modern deployment contexts vary.
- [DORA continuous delivery](https://dora.dev/capabilities/continuous-delivery/): test/deployment automation, observability, database change management and low-risk releases.
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/): SLOs, monitoring, incidents, load, configuration and canary releases.

For volatile facts—versions, prices, support lifecycle, cloud/store limitations, or law—open the current official source during the project-blueprint run and cite it next to the affected decision.
