# Frontier & Verifier Review Scorecard

| Review | Lens | Grades | Status |
|---|---|---|---|
| REVIEW_A_legal_schema.md | Verifier Lens A (adversarial) | Legal 2/5 · Schema 2/5 | Fixes applied in d12fdfe (v0.2); re-verification pending |
| REVIEW_B_bench_gov_launch.md | Verifier Lens B (stress-test) | Bench 2/5 · Gov 2/5 · Roadmap 3/5 | Issues #3/#4/#5 open (pinned DANDI bench, foundation plan, lock.json) |

## Response discipline (contributor ratchet)
Every review point became a tracked issue within the hour. Fixes committed same-session.
Next: re-dispatch verifier lenses on v0.2 to confirm the fixes hold.

## External frontier review (2026-09-22, v0.3 plan)

Reviewer: independent frontier AI (full source review at commit 45336a0; 13 tests executed directly).
Grades: A 2/5 · B 2/5 · C 1/5 · D 2/5 · E 2/5 · F 2/5. Verdict: problem legitimate, prototype real,
claims not substantiated — repair before promoting.

**All P0 defects fixed in b8d84c4 (v0.3.0):** placeholder scores removed (real synthetic regression
w/ shuffled-target + clean-signal controls); false PASS eliminated (every finding affects the
decision; unknown jurisdictions never fall back); strict schema/version handling (duplicate keys,
type discipline, bounded parsing); nondestructive init + reviewable migrate; claims corrected
(FALCON/MOABB/NLB/DUO acknowledged; 62 vs 78 wpm distinguished; 35.6% = study-average yield;
no negative FDA claims); scoped versioned policy mappings (US-CA EXPERIMENTAL; CO/EU/CL research
drafts); governance right-sized (AI nonvoting, 3-working-day target, honest free-forever scope);
complete Apache-2.0 text. Issues #1 #2 #5 closed with fix refs. 28/28 tests.
