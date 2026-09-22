# Review Lens A — Legal/Policy + NDRM Schema

**Reviewer:** hostile-but-fair verifier (subagent)  
**Date:** 2026-09-22  
**Artifact:** NeuroGate v0.1 (`src/neurogate/ndrm.py`, `docs/reviews/FRONTIER_REVIEW_BRIEF_v0.1.md`)

## (A) Legal/policy soundness of the four law packs

**Grade: 2 / 5**

The law packs are a useful first sketch, but they **over-operationalize, under-specify, and mislabel** several statutes. They look like a compliance checklist without the statutory text behind it.

| Pack | Source class | Core finding |
|---|---|---|
| **US-CO HB24-1058** | VERIFIED | Statute only expands CPA "sensitive data" to include biological data (which includes neural data). It does **not** independently create purpose-limitation/consent/deletion/no-sale controls; those are CPA-level consumer rights that already attach to personal data. The pack should say "CO CPA sensitive-data controls" not "HB24-1058 controls". |
| **US-CA SB 1223 / CPRA** | VERIFIED | Neural data is added to "sensitive personal information" under Civ. Code § 1798.140(ag)(1)(G). The right created is **not** a neural-specific access right; it is the general CCPA right to know/access/delete plus the CPRA right to **limit use/disclosure** of sensitive personal information (§ 1798.121). The `access_request_path` control is fine as a generic CCPA access mechanism, but calling it "neural-data-specific" over-claims. |
| **CL Art. 19 (Law 21.383)** | VERIFIED | The amendment is **programmatic**: it mandates that law shall safeguard "brain activity, as well as the information derived from it" and protect physical/mental integrity. It does **not** enumerate consent, deletion, or identity-integrity artifacts. The pending bill (Boletín 13.828-19) would add mental privacy, consent, minors, workplace limits, etc. `identity_integrity_statement` is therefore an **invented artifact**, not a statutory requirement. It may be a good practice, but the code presents it as required-by-law. |
| **EU GDPR Art. 9** | VERIFIED | Art. 9 prohibits processing special-category data (including biometric data for identification and data concerning health) unless an Art. 9(2) exception applies; explicit consent is one. The pack is mostly right, but "lawful_basis" is ambiguous: GDPR requires **both** an Art. 6 lawful basis **and** an Art. 9 exception. `access_request_path` is an Art. 15 right, not a pack-specific control. `no_sale_default` has no direct GDPR basis (sale is not a GDPR concept; consideration is lawful basis/purpose limitation). |

### Missing/misstated controls

1. **None of the packs require a retention period / storage limitation.** CPRA/GDPR both have storage-limitation principles; CPA has data minimization. The schema has no field for it.
2. **No data-transfer / third-party / service-provider / contractor field.** CPRA § 1798.100 et seq. and GDPR Chapter V both impose obligations on sharing; the schema cannot record recipients or cross-border transfers.
3. **No security / access-control field.** Colorado CPA § 6-1-1306 and GDPR Art. 32 require appropriate security; the packs ignore it.
4. **No minor/child flag.** CPA and CPRA have special rules for known children / minors under 16; neural data from pediatric subjects is higher-risk and unlabeled.
5. **Sale=false is over-simplified.** CPRA "sale" excludes some transfers and "sharing" is a separate opt-out; GDPR doesn't use "sale" as a control category.
6. **Chile pack lacks a consent/control artifact basis.** The constitutional amendment delegates everything; the pending bill is not yet law. The right artifact should be framed as a voluntary declaration, not a statutory checklist item.

## (B) NDRM schema fitness

**Grade: 2 / 5**

A YAML sidecar is a reasonable **project-level** human-editable format, but as designed it has serious fitness gaps for a governance primitive:

### Missing fields

| Missing field | Why it matters |
|---|---|
| **Provenance chain / `GeneratedBy`** | BIDS requires provenance for derived data; a rights manifest without a chain cannot show who transformed the data or from which raw files. |
| **Consent artifact hashes / URIs** | The pack demands a `consent_record`, but the manifest never links to the actual consent form, its hash, or the consenting subject/session. Without this, `consent_record` is an empty checkbox. |
| **Cross-border transfer flags / recipient list** | GDPR Chapter V and most research-data-sharing agreements need to record transfers and adequate safeguards (SCCs, etc.). |
| **Subject/session scope** | One `ndrm.yaml` is written per directory, but neural datasets have per-subject consent. There is no way to attach a manifest to a specific subject or session. |
| **Retention / deletion schedule** | `deletion_path` is a contact/mechanism, not a retention horizon. |
| **Security controls / encryption-at-rest** | Required by CPA and GDPR security obligations; absent. |
| **Data minimization / purpose specification** | `allowed_uses: ["research"]` is too coarse for lawful-basis specificity. |
| **Versioning / revocation history** | No `previous_version` hash or revocation log; if a subject revokes consent, the manifest cannot be audited. |

### YAML sidecar acceptability

- **BIDS:** BIDS key-value metadata **MUST** be JSON (BIDS Common Principles, "Key-value files (dictionaries)": "JavaScript Object Notation (JSON) files MUST be used for storing key-value pairs"). A YAML sidecar would be treated as a non-standard file. It may survive under the "Unspecified data" clause, but it will **not** be consumed by BIDS validators or tools.
- **DANDI:** DANDI validates NWB files and uses a `dataset_description.json` (BIDS-style) plus `dandiset.yaml` for archive-level metadata. There is no documented acceptance of an arbitrary per-directory YAML sidecar for rights metadata.
- **NWB:** NWB embeds metadata inside the NWB file; external YAML sidecars are not a recognized NWB pattern.

**Conclusion:** A YAML sidecar is acceptable as a **project-specific** convention, but it will not be accepted by BIDS/DANDI/NWB maintainers without (1) converting to JSON, (2) aligning with `dataset_description.json` / `GeneratedBy` / BIDS provenance model, and ideally (3) proposing a BIDS Extension Proposal.

## Issue list (one line each)

1. US-CO pack mislabels CPA general controls as HB24-1058-specific controls.
2. US-CA pack over-claims a neural-data-specific access right; the right is general CCPA/CPRA access/limit-use.
3. Chile pack invents `identity_integrity_statement` as a statutory artifact; the constitutional amendment is programmatic and implementing legislation is pending.
4. GDPR pack conflates "lawful_basis" (Art. 6) with Art. 9 exception and adds `no_sale_default`, which is not a GDPR concept.
5. No retention/storage-limitation field despite CPRA/GDPR/CPA data minimization.
6. No cross-border transfer / recipient / adequacy field despite GDPR Chapter V and multi-site research norms.
7. No consent artifact hash/URI/link, so `consent_record` is unverifiable.
8. No provenance chain / `GeneratedBy`, breaking BIDS-derived-data expectations.
9. No subject/session scope, so per-subject consent cannot be attached.
10. No security/encryption/access-control field despite CPA/GDPR security obligations.
11. No minor/child flag despite special CPA/CPRA minor rules.
12. YAML sidecar violates BIDS "JSON MUST be used for key-value pairs" rule; maintainers will not accept it as a first-class sidecar.
13. `sale: false` is too coarse: CPRA distinguishes sale, sharing, and authorized transfers; GDPR doesn't use sale as a control.
14. `allowed_uses: ["research"]` lacks purpose-specification granularity required by lawful-basis and consent regimes.
15. No versioning/revocation audit trail; cannot prove a manifest was updated after a consent withdrawal.

## 3 highest-value fixes

1. **Conform to BIDS/DANDI metadata model:** rewrite the sidecar as JSON (e.g., `ndrm.json` or embed in `dataset_description.json` under a `NeuroGateRights` key), align fields with `GeneratedBy`/`SourceDatasets`/provenance, and propose a lightweight BEP rather than a standalone YAML file.
2. **Add verifiable consent linkage:** replace the empty `consent_record` checkbox with `consent_artifacts` (array of `{subject_id, session_id, consent_form_url, hash_algo, hash_value, signed_date}`), and require at least one artifact for non-synthetic data.
3. **Correct the law-pack claims:** rename US-CO to "CO CPA sensitive-data controls (as expanded by HB24-1058)", reframe US-CA as "CCPA/CPRA sensitive-PI controls (neural data now included)", reframe Chile as a "voluntary neurorights declaration" pending implementing law, and split GDPR into explicit `art6_lawful_basis` + `art9_exception` with no `sale` control.

## Source ledger

- [1] Colorado HB24-1058 enrolled text (2024): https://leg.colorado.gov/sites/default/files/documents/2024A/bills/2024a_1058_enr.pdf — defines biological data and neural data, expands CPA sensitive data.
- [2] California SB 1223 (CPRA neural data amendment, 2024): https://pactsntl.org/__static/jdj5jdewje1rrui5rkd2tulsb2nsudn6/California-Neural-Rights-Bill.pdf — adds neural data to sensitive PI under Civ. Code § 1798.140(ag)(1)(G); preserves existing access/delete/limit-use rights.
- [3] Chile Law 21.383 / Art. 19 neurorights amendment (2021): https://santiagoramonycajal.org/en/2026/01/13/neuroderechos — programmatic constitutional principle; implementing bill Boletín 13.828-19 still pending.
- [4] GDPR Art. 9: https://gdpr.eu/article-9-processing-special-categories-of-personal-data/ — special-category prohibition + exceptions; requires Art. 6 lawful basis and Art. 9(2) exception.
- [5] BIDS Common Principles 1.11.1 — key-value files MUST be JSON; inheritance principle; unspecified data: https://bids-specification.readthedocs.io/en/stable/common-principles.html.
- [6] DANDI validation / metadata docs (2026): https://docs.dandiarchive.org/user-guide-sharing/validating-files/ and https://docs.dandiarchive.org/user-guide-sharing/dandiset-metadata/ — validation is NWB-first; archive metadata is dandiset-level, not per-directory YAML.
