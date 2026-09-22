🧠🔓 **NeuroGate v0.1 — the open neurodata-rights toolkit is live**

Your neural data never leaves your hands. This project hosts no patient data — ever.

**Why now:** Colorado (HB24-1058), California (CPRA neural-data provisions), and Chile
(constitutional neurorights amendment) all just landed — and nobody ships practical tooling.
Meanwhile neural decoding still has no shared benchmark. We close both gaps:

- **NDRM sidecar** — a tiny `ndrm.yaml` declaring ownership, law packs, allowed uses,
  revocation contact for any neural dataset. One command, committed beside your data.
- **Law packs** — practical control checklists encoded from CO/CA/CL/EU law.
- **Open decoder benchmarks** — 5 seeded protocols (2 runnable synthetic, 3 DANDI-by-reference,
  honest about provenance).

**30 seconds to first value:**
```
pipx install neurogate
neurogate init ~/my-dataset --owner "You" --jurisdiction US-CA
neurogate check ~/my-dataset
```

Free forever (Apache-2.0). Stewardship council — clinical, law/policy, and community seats open.
Contributor ratchet: every PR gets a public response within 24 hours.

Built by a physician-informatics professor + an AI fleet that ships with receipts.
