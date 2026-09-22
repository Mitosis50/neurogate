# NeuroGate v0.1 — Frontier Review Brief

**Repo:** https://github.com/Mitosis50/neurogate
**Owner:** Dr. Elbert Basa (physician-informatics professor, BCBA candidate) · Maintainer: Elbert + Mira (AI fleet)
**License:** Apache-2.0 · **Founded:** 2026-09-21 · **Status:** v0.1 alpha, 4 commits, 8/8 tests pass

---

## 1. What this is

**NeuroGate** = an open-source toolkit closing two gaps nobody else ships:
1. **NeuroData Rights Manifest (NDRM)** — a one-command YAML sidecar (`ndrm.yaml`) for any
   neural dataset declaring: owner, applicable law pack, allowed uses, revocation contact.
   Law packs encode the practical control checklists of: **Colorado HB24-1058**, **California
   CPRA neural-data provisions**, **Chile's constitutional neurorights amendment (Art. 19)**,
   and a **GDPR Art. 9 analog**.
2. **Open decoder benchmarks** — the shared benchmark suite neural decoding lacks. 5 seeds:
   2 runnable synthetic baselines + 3 registered DANDI-by-reference (honest provenance;
   the repo hosts NO patient data, ever).

## 2. Provenance of design decisions (why we believe these gaps exist)
- Two independent methods converged: (a) a typed-judgment AI (TypeSafe Jev, 3 consistent draws)
  selected "neurodata governance tooling" as the highest-leverage pearl (novelty 0.66-0.68) and
  "benchmark suite" as best first move; (b) an independent librarian research pass
  (12 bounded web searches, source-graded) surfaced the same two gaps as Pearls 6 and 7, with
  "BCI Decode Benchmark Harness on DANDI" as Pearl 2 — an exact match.
- Verified ecosystem facts the design rests on: intracortical speech BCIs reach 62-78 wpm in
  single-digit patients; no FDA PMA for implantable motor/speech BCI; BrainGate reports 35.6%
  mean initial electrode yield with only ~7% decline over ~3 years (yield/variability, not decay,
  is the binding constraint); CO/CA/Chile laws landed with no practical compliance tooling; the
  open stack (NWB/DANDI/BIDS/SpikeInterface/BrainFlow) is format-strong but benchmark-weak.

## 3. Core artifacts (inline for review)

### ndrm.yaml schema (v0.1)
```yaml
ndrm_version: "0.1"
dataset: my-dataset
owner: "Lab P.I."           # required
generated: "2026-09-21"
jurisdiction: "US-CA"        # selects the law pack
applicable_law: "California CPRA neural-data provisions"
allowed_uses: ["research"]
sale: false                  # no_sale_default enforced
revocation_contact: "privacy@lab.org"   # required
required_controls:           # must cover the law pack's requirements
  - purpose_limitation
  - consent_record
  - deletion_path
  - no_sale_default
  - access_request_path
```

### Law packs (the compliance primitive)
- **US-CO** HB24-1058 (neural data = sensitive biometric): purpose_limitation, consent_record,
  deletion_path, no_sale_default
- **US-CA** CPRA provisions: + access_request_path
- **CL** Chile Art. 19 neurorights: + identity_integrity_statement
- **EU** GDPR Art. 9 analog: + lawful_basis, access_request_path

### The check semantics
PASS requires: all law-pack controls present in required_controls + owner and
revocation_contact set + sale=false. Any gap names the missing control and the fix command.

### Benchmark suite (v0.1)
| name | metric | provenance |
|---|---|---|
| synthetic-kalman-cursor | bits_per_minute | local-synthetic (runnable now) |
| synthetic-spike-rate | r2 | local-synthetic (runnable now) |
| dandi-speech-wpm | words_per_minute | REQUIRES-EXTERNAL-DATA (DANDI ref) |
| dandi-cursor-bpm | bits_per_minute | REQUIRES-EXTERNAL-DATA |
| yield-predictor-v0 | auc | predicts initial electrode yield (BrainGate 35.6% baseline) |

## 4. Governance model
- **Stewardship council v0:** maintainer seat (Dr. Basa) + AI co-maintainer seat (Mira:
  triage/docs/CI) + three OPEN seats: clinical/researcher, law/policy, community (elected by
  first 100 contributors). Consensus; maintainer breaks ties; every decision in DECISIONS.md.
- **Free forever:** Apache-2.0, no telemetry, no data hosting, no paywall — ever. Any
  monetization proposal requires dual countersignature + 30-day public notice.
- **Contributor ratchet:** every PR/issue gets a public response in 24h. AI fleet drafts
  responses in minutes (labeled `assist:ai-drafted`); a human confirms within 24h.
  **The AI never merges alone.**

## 5. The specific review asks (please grade each 1-5 + rationale)

**A. Legal/policy soundness** — Are the CO/CA/CL/EU law packs a faithful, practical
   operationalization of the real statutes? What control is missing or misstated?
   (E.g., does CA CPRA actually create a neural-data-specific access right, or are we
   over-reading? Is the Chile Art. 19 identity-integrity statement the right artifact?)

**B. NDRM schema fitness** — Is a YAML sidecar the right primitive? What fields are missing
   (provenance chain? consent artifact hashes? cross-border transfer flags)? Would a
   DANDI/BIDS maintainer accept it as a sidecar?

**C. Benchmark suite design** — Are the 5 seeds the right v0.1? What's the ONE benchmark
   that would make this the field's shared yardstick? Is "metric + protocol + reference impl +
   DANDI ID" the right spec shape? How should we handle cross-version decoder comparison?

**D. Governance & abuse resistance** — Will the council model survive a hostile fork or a
   corporate takeover attempt? Is the AI-fleet-assisted triage (transparent labeling, human
   confirm) trustworthy or theater? How do we keep the "free forever" promise verifiable?

**E. Viral-launch parameters** — We ran a structured judgment pass that produced:
   narrative=privacy_sovereignty, artifact=toolkit_platform, channel=Telegram/Discord-first,
   first-impression=one-command-install, governance hook=stewardship council, community shape
   =AI-fleet-assisted, economics=pure_commons, virality metric=downstream_usage,
   #1 risk=abandonment. **Which of these 10 calls would you flip, and why?**

**F. Missing pearls** — Beyond the 10 in our roadmap (clock-sync DSP ASRC, NWB trial
   extension, BrainFlow conformance kit, Open Ephys bridge, ship's-log trial documentation,
   SCED calibration, linear-phase closed-loop filters), what overlooked high-leverage
   contribution are we still missing?

## 6. What we will do with your review
- Every substantive point → an issue in the repo, credited to you, publicly tracked.
- Points grading 1-2 (disagreements) get a council-thread response within 24h.
- The frontier-review scorecard (all grades + responses) lands in `docs/REVIEWS.md`.
