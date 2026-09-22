# NeuroGate Governance v0.3 (small-team, accountable)

## Roles

| Role | Holder | Scope |
|------|--------|-------|
| Maintainer (named human) | Dr. Elbert Basa | technical direction, releases, merge approval |
| Maintainer backup (named human) | *vacant — actively sought* | continuity; takes over if maintainer unreachable 30 days |
| AI assistant | Mira (fleet) | triage drafts, docs, CI upkeep — **explicitly NONVOTING** |
| Patient/participant perspective | *open* | consulted before decisions affecting rights or data sharing |

**Human accountability is not multiplied by AI seats.** All merges, releases, legal
mappings, and public attestations require human review. Automation is scoped to the
access it actually needs.

## Operating rules

- **Decisions:** maintainer decides; every decision logged in `docs/DECISIONS.md` with date + rationale.
- **Conflicts of interest:** declared in the issue thread; recusal required for affected decisions.
- **Emergency suspension:** maintainer may suspend a release key/namespace change pending review; logged same-day.
- **Release keys & namespace:** held by the maintainer; handover instructions in `docs/HANDOVER.md` before any larger institution forms.
- **Response targets (honest):** acknowledgment within **3 working days** (target, not promise). Automated acknowledgment is labeled as automated.
- **No elections by first-100-accounts** — manipulable. Future stakeholder seats require deliberate design.
- **Delay institution-building** (foundation, council machinery, financial commitments) until people demonstrably depend on the tool.

## What "free" actually promises

- Released code remains available under **Apache-2.0** (complete text in `LICENSE`).
- Apache-2.0 permits redistribution and commercial derivatives; it does not compel
  free hosting, prevent a commercial fork, or bind future maintainers' service prices.
- Ongoing hosting/support depends on resources; no promises beyond the license are made.
- **This repo hosts no patient data.** Benchmarks reference external datasets under their own access conditions.

## Release hygiene

- Complete Apache-2.0 license text ships in `LICENSE`.
- Release authority: named maintainer; handover plan in `docs/HANDOVER.md`.
- `docs/DECISIONS.md` is the public decision log.