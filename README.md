# NeuroGate 🧠

**Experimental open-source toolkit for documenting neural-dataset use and reproducing decoder evaluations.**

> Manifest checks assess documented conditions. They do **not** certify legal compliance,
> validate consent from a hash, or establish clinical performance. Private evidence stays
> under the responsible organization's control. This repo hosts no patient data.

## What it is (v0.3)

- **NDRM manifest** — a versioned JSON sidecar (`ndrm.json`) documenting dataset identity,
  accountable roles, proposed use, rights/conditions, evidence states, and policy mappings.
- **Honest assessments** — `SCHEMA_VALID / INCOMPLETE / BLOCKED / READY_FOR_REVIEW / ERROR`.
  The tool exposes missing evidence instead of concealing it. It never issues a compliance PASS.
- **One real synthetic benchmark** (`synthetic-regression-v0`) — a documented smoke test with
  train/test split, held-out R², shuffled-target control, and clean-signal fixture. Planned
  tasks (FALCON H1 / MOABB) are labeled PLANNED and return **no score**.
- **Exit-code contract** — `check` exits 0 only for READY_FOR_REVIEW; INCOMPLETE=2,
  BLOCKED=1, ERROR=3. `report` formats by default; `--gate` propagates the decision.

## Provenance & positioning

NeuroGate connects dataset-use documentation to reproducible neural-decoding evaluations.
It builds on established tools rather than replacing them: FALCON (decoder evaluation),
MOABB (EEG benchmarking), Neural Latents Benchmark, GA4GH DUO (data-use vocabulary),
BIDS/DANDI (dataset metadata). Interop is tested against fixtures before any compatibility
claim — a JSON suffix alone establishes nothing.

## Honest quickstart (from source)

```bash
pip install -e .            # from a repo clone; PyPI artifact NOT yet published
neurogate init ~/my-dataset --org "Lab" --contact privacy@lab.org --jurisdiction US-CA
neurogate check ~/my-dataset            # INCOMPLETE until you fill evidence + mapping review
neurogate bench synthetic-regression-v0 # the one runnable benchmark (real computation)
```

`pipx install neurogate` is **not** advertised as verified until the package is published
and clean-install behavior is checked.

## What the checks mean

| Assessment | Meaning |
|---|---|
| SCHEMA_VALID | structural conformance only |
| INCOMPLETE | unresolved facts/evidence/applicability (findings name them) |
| BLOCKED | a known required condition for the workflow is unsatisfied |
| READY_FOR_REVIEW | machine-checkable requirements met **in scope**; human/legal conclusions remain separate |
| ERROR | unparseable/unsupported input |

Evidence states: `declared → referenced → digest_checked → human_reviewed`.
A digest or signature never establishes legal validity.

## Scientific statements we make (and their limits)

- Willett 2023 (62 wpm) used **intracortical** recording; Metzger 2023 (78 wpm) used
  **high-density cortical surface** recording — different demonstrations, not pooled.
- BrainGate long-term study reports a **study-average yield ~35.6% across days/arrays** —
  not a universal initial-yield constraint.
- We make **no negative claims** about FDA approvals; absence of evidence is not evidence
  of absence.

## Governance (small-team, accountable)

Named human maintainer + named human backup; AI assistant explicitly **nonvoting**;
human review for merges, releases, legal mappings, and public attestations. See
[GOVERNANCE.md](GOVERNANCE.md). Apache-2.0 governs the released code — it does not
compel free hosting or bind future maintainers; "free" identifies what is actually
promised: released code remains available under its license.

## Status

v0.3.0 — after external review: placeholder scores removed, verdict logic repaired
(no false PASS), strict schema/version handling, nondestructive init, corrected claims.
Next milestones: one pinned existing-benchmark adapter, three external users, repeat use.