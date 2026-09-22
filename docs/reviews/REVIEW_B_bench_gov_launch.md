# NeuroGate v0.1 — Review Lens B: Benchmarks + Governance + Launch

**Reviewer:** verifier-team stress-tester (Hermes subagent)  
**Scope:** asks C, D, E, F from `FRONTIER_REVIEW_BRIEF_v0.1.md`.  
**Grounding:** repo source read (`bench.py`, `GOVERNANCE.md`, `docs/LAUNCH_TELEGRAM.md`, `README.md`, `ROADMAP.md`) plus web reconnaissance on FALCON, BEND-BCI, MLCommons/MLPerf, GLUE/SuperGLUE, OpenBB wind-down, Redis→Valkey/Elasticsearch→OpenSearch/Terraform→OpenTofu, Hugging Face hub governance anxiety, and neurodata consent tooling (CONP, Open Brain Consent).

---

## C. Benchmark suite design

**Grade: 2 / 5**

### Rationale
The 5 seeds are the right *shape* but not yet a benchmark suite — they are protocol stubs. Two run only toy random baselines (`synthetic-kalman-cursor`, `synthetic-spike-rate`), and the three DANDI-by-reference entries lack real dataset IDs, download adapters, train/val/test splits, or a submission protocol. v0.1 honestly labels them as `REQUIRES-EXTERNAL-DATA`, which is good provenance hygiene, but the field cannot use them as a yardstick today.

**The ONE benchmark that would make this the field's shared yardstick:**
A **multi-session intracortical motor/speech decoding benchmark with a public held-out test split** — essentially a NeuroGate-branded harness around the FALCON datasets (H1 human reach-and-grasp, H2 handwriting, and the speech analogs) plus DANDI-hosted open-loop calibration data. FALCON already proved that the community will show up for a cross-session robustness benchmark; NeuroGate's value-add should be:
1. NDRM-wrapped provenance (every submission carries a `ndrm.yaml` declaring dataset rights),
2. a one-command reproducible harness (`neurogate bench dandi:<id>`),
3. a public leaderboard with version-pinned DANDI assets and commit-pinned decoder versions.

**Spec shape `{metric, protocol, reference_impl, DANDI-ID}`:**
This is *almost* right, but incomplete. A reproducible benchmark spec needs at least seven fields:
- `metric` (single scalar, e.g. `bits_per_minute`, `r2`, `AUC`)
- `protocol` (task definition + train/val/test split procedure)
- `reference_impl` (baseline code + expected score range)
- `dandi_id` + `version` (pin the asset, not just the dandiset)
- `preprocessing_commit` (pin the data-prep script)
- `random_seed` / `trial_perm` protocol
- `compute_budget` rule (wall-clock, memory, GPU class — to prevent benchmark hacking)

Without version pinning, cross-version comparison is meaningless. Recommendation: treat every benchmark result as a tuple `(decoder_version, benchmark_version, dandi_asset_version, score)`. Require submissions to declare all three versions; the leaderboard sorts within a `(benchmark_version, dandi_asset_version)` cohort. When a new DANDI version or a new benchmark protocol ships, start a new cohort; do not silently overwrite old leaderboards.

**Cross-version decoder comparison:**
Never compare decoders evaluated under different DANDI versions or different preprocessing commits. The harness should pin these in a lockfile (e.g., `benchmark.lock.json`) and refuse to mix cohorts. For fair comparison across decoder releases, re-run the *same* frozen evaluation pipeline on the *same* pinned data for every decoder version.

### Issues (C)
- `bench.py` uses `random.random()` for synthetic scores with a fixed seed; this is a placeholder, not a baseline.
- DANDI references are strings (`"fetch by ID at run time"`), not concrete dandiset/version tuples.
- No train/val/test split, no preprocessing commit pin, no compute budget rule.
- `yield-predictor-v0` predicts electrode yield but has no public training data, no target label definition, and the schema only defines features.
- The BEND-BCI preprint (July 2026) and the FALCON benchmark are already in the field; NeuroGate risks being a late wrapper unless it differentiates on governance + reproducibility.

---

## D. Governance & abuse resistance

**Grade: 2 / 5**

### Rationale
The council model is a well-intentioned seed, but it is not yet abuse-resistant. The maintainer seat (Dr. Basa) holds a tie-breaking veto, the AI co-maintainer seat is held by the maintainer's own fleet (Mira), and the three open seats are unelected until "first 100 contributors." That is a single point of failure, not a polycentric commons.

**Hostile fork / corporate takeover:**
Apache-2.0 makes a hostile fork trivially legal. The only defenses are (a) distributed copyright, (b) neutral-foundation escrow, and (c) a community that can migrate faster than a buyer can capture it. Redis→Valkey and Terraform→OpenTofu show that vendor-controlled projects with CLAs can be relicensed overnight; the forks that survived had Linux Foundation governance and multi-vendor contributors. Elasticsearch→OpenSearch shows that even a corporate-backed fork can later move to a foundation, but only after trust was already damaged.

For NeuroGate, the current structure would not survive a determined takeover because:
- A single person controls the GitHub org, PyPI package, and domain narrative.
- There is no foundation or escrow holding trademarks/domain/assets.
- The "AI co-maintainer" is not independent; it is the maintainer's own tooling, which collapses the two votes into one in practice.

**AI-fleet-assisted triage:**
Labeling drafts as `assist:ai-drafted` and requiring human confirm before merge is the right surface policy. It is currently *theater-adjacent* because there is no public evidence that the fleet is actually a separate reviewer, no published policy for when human override is required, and no audit log of AI-vs-human votes. To make it trustworthy: publish every triage decision with `ai-confidence`, `human-reviewer`, and `disagreement-resolution`; keep the AI out of merge rights; and rotate human reviewers so the same person is not always confirming the same AI.

**Free-forever verifiability:**
"Free forever" is a promise, not a technical guarantee. Verifiability requires:
1. **License immutability:** Apache-2.0 already travels with every copy; do not add a CLA that lets a future maintainer relicense.
2. **No telemetry / no data hosting:** must be independently auditable in CI (e.g., a `telemetry-audit` test that greps the source for network calls).
3. **Asset mirroring:** like the Hugging Face hub anxiety case, if NeuroGate ever hosts artifacts, publish IPFS/torrent mirrors and revision hashes so users are not hostage to the org.
4. **Public decision log:** every monetization or governance change must be in `docs/DECISIONS.md` with 30-day notice *and* a technical signature (e.g., signed git tag).
5. **Foundation route map:** by v0.3, move trademarks/domains to a neutral entity (e.g., NumFOCUS, Linux Foundation, or a purpose-built nonprofit) with a charter that forbids unilateral relicense.

### Issues (D)
- Maintainer + AI co-maintainer effectively collapse to one vote.
- Open seats have no election mechanism, term limits, or removal process yet.
- No neutral-foundation escrow or trademark/domain governance.
- No public `telemetry-audit` or reproducible build attestation.
- "Dual countersignature + 30-day public notice" is stated but lacks enforcement (who are the two signers? what happens if one refuses?).

---

## E. Launch parameters — which of the 10 calls to flip

The 10 calls from the judgment pass:

| # | Call | Verdict | Why |
|---|------|---------|-----|
| 1 | narrative = privacy_sovereignty | **KEEP** | Differentiated and legally timely (CO/CA/Chile). |
| 2 | artifact = toolkit_platform | **KEEP but narrow** | A "platform" promise is too big for v0.1; ship a toolkit first, then grow into a platform. |
| 3 | channel = Telegram/Discord-first | **FLIP to GitHub + docs-first** | Chat-first communities are noisy and ephemeral. Open-source infrastructure wins with searchable issues, reproducible bug reports, and a docs site. Discord/Telegram should be secondary social layer, not primary. |
| 4 | first-impression = one-command-install | **KEEP** | `pipx install neurogate` is the right hook. |
| 5 | governance hook = stewardship council | **FLIP to "council seed with foundation route map"** | A council owned by the founder is not a hook; it is a risk. The launch story should be "governance that cannot be captured," with a concrete path to foundation. |
| 6 | community shape = AI-fleet-assisted | **KEEP but rebrand** | "AI fleet" sounds like automation theater. Call it "human-reviewed, AI-accelerated triage" and publish the audit policy. |
| 7 | economics = pure_commons | **KEEP** | Correct for trust; but add a sustainability plan (grants, nonprofit membership) so pure commons does not mean pure burnout. |
| 8 | virality metric = downstream_usage | **KEEP** | Better than stars. Measure `ndrm.yaml` files in the wild, DANDI datasets citing NeuroGate harness, and benchmark submissions. |
| 9 | #1 risk = abandonment | **KEEP but reframe** | Abandonment is real; the antidote is bus-factor expansion and foundation escrow, not just a feeling. |
| 10 | (implied 10th: stewardship council details / free forever) | — | See D above. |

**Flips to action now:**
- **Channel:** Make GitHub Issues and a ReadTheDocs-style site the primary surface. Use Discord/Telegram only for real-time community support.
- **Governance hook:** Replace "stewardship council" launch language with "governance lock-in plan" — e.g., "by v0.3 we will transfer the trademark to a neutral nonprofit; until then, decisions require two of {maintainer, clinical seat, law/policy seat}."
- **Sustainability:** Add a "funding and sustainability" page. Pure commons without a funding rail is how OpenBB ended up winding down and releasing its stack — 72.6k stars, no sustainable business. NeuroGate should avoid that fate by design.

---

## F. Missing pearls beyond the 10 in ROADMAP.md

**Grade: 3 / 5** (the roadmap is sensible but misses three high-leverage adjacent gaps)

### Highest-value missing pearls
1. **A reproducibility / provenance lockfile format for neural decoding.**
   The field does not just need benchmarks; it needs a standard way to declare *what was run on what data with what preprocessing*. NeuroGate should define a `neurogate.lock.json` (or NWB extension) that records dataset version, preprocessing script hash, decoder commit, random seed, compute environment, and metric. This would be a genuine primitive no one else ships.

2. **A machine-readable consent / data-use layer tied to NDRM.**
   The ROADMAP v0.2 mentions an SPDX-style expression, but the real gap is linking the YAML sidecar to actual consent forms or data-use agreements (e.g., Open Brain Consent templates, CONP clauses). A `consent_hash` or `dua_url` field plus a validator that checks allowed uses against the consent language would close the loop between legal text and code.

3. **A cross-session / cross-subject robustness protocol.**
   FALCON and BEND-BCI already exist, but neither ties robustness evaluation to governance metadata. NeuroGate should add a "robustness" axis to every benchmark: held-out subject, held-out session, perturbation sweep, and compute cost. This is the difference between a leaderboard and a useful yardstick.

### Other overlooked gaps
- **Decoder calibration data budget standard:** how many minutes of calibration are allowed per benchmark condition? Real BCIs are calibration-limited; the benchmark should reflect that.
- **Open-source hardware/implant data provenance:** as intracortical BCI devices proliferate, an `implant_manifest` sidecar (electrode array, firmware version, signal-chain settings) will become essential for reproducibility.
- **An accessible ethics-IRB template generator:** convert NDRM jurisdiction into draft consent-form language researchers can paste into IRB applications. The CONP and Open Brain Consent projects did this for MRI; NeuroGate should do it for electrophysiology and BCI.

---

## Aggregated issue list

1. `bench.py` synthetic baselines are random placeholders, not real algorithm baselines.
2. DANDI benchmark entries lack concrete dandiset IDs, versions, splits, and adapters.
3. No version-lockfile mechanism for cross-version / cross-cohort decoder comparison.
4. No compute-budget or preprocessing-commit rules in benchmark specs.
5. `yield-predictor-v0` lacks training data, target labels, and evaluation protocol.
6. Council governance concentrates effective power in the maintainer + AI seat.
7. No election/removal/term-limit rules for open seats.
8. No neutral foundation escrow or trademark/domain transfer plan.
9. AI-fleet triage policy is stated but not independently auditable.
10. "Free forever" lacks technical verifiability (telemetry audit, build attestation, mirror plan).
11. Launch channels over-weight ephemeral chat vs. searchable docs/issues.
12. Governance hook in launch narrative needs a credible anti-capture route map.
13. Roadmap omits provenance lockfile, machine-readable consent linkage, and cross-session robustness protocols.
14. No sustainability/funding plan for pure-commons economics.

---

## 3 highest-value moves

1. **Ship one real, pinned DANDI benchmark harness by v0.2.**
   Pick a single high-leverage task — e.g., FALCON H1 human reach-and-grasp or a speech-decoding DANDI dandiset — and make `neurogate bench dandi:<id>` actually download, split, run a baseline, and report a reproducible score. A working one-benchmark yardstick beats five stubs.

2. **Governance hardening: publish an anti-capture transition plan.**
   Define the route to a neutral foundation by a target date, require dual human sign-off (not maintainer+AI) for license or monetization changes, and add a CI `telemetry-audit` test. This turns the council from a promise into a credible commitment.

3. **Add a `neurogate.lock.json` provenance format + consent-link validator.**
   Make reproducibility and rights-checking machine-readable. If every NDRM file can carry a `consent_hash` and every benchmark result carries a lockfile, NeuroGate becomes the trust layer the open neural-data ecosystem lacks.

---

*File written for NeuroGate frontier review — Lens B.*
