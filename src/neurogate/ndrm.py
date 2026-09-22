"""NeuroData Rights Manifest (NDRM) — the core governance primitive.

A sidecar next to any neural dataset declaring: who owns it, which law packs apply,
allowed uses, and revocation contact. v0.2: BIDS-compatible JSON (ndrm.json) with
provenance chain, consent artifact hashes, and cross-border transfer flags.

Law packs (reframed per Lens A review — actual statutory scope, marked where
implementing law is still pending):
- US-CO: Colorado Privacy Act incl. HB24-1058 clarifying neural data = sensitive biometric
- US-CA: CCPA/CPRA general access/limit-use rights (no neural-specific right claimed)
- CL: Chile Art. 19 neurorights = programmatic; implementing law PENDING (marked)
- EU: GDPR Art. 9 special-category + Art. 6 lawful basis (distinguished)
"""
import os, json, yaml, time

LAW_PACKS = {
    "US-CO": {"law": "Colorado Privacy Act + HB24-1058 (neural data = sensitive data)",
              "status": "ENACTED",
              "requires": ["purpose_limitation", "consent_record", "deletion_path", "no_sale_default", "sensitive_data_consent"]},
    "US-CA": {"law": "CCPA/CPRA general access + limit-use rights (applies to neural data; no neural-specific right)",
              "status": "ENACTED",
              "requires": ["purpose_limitation", "consent_record", "deletion_path", "no_sale_default", "access_request_path", "limit_use_disclosure"]},
    "CL": {"law": "Chile Constitution Art. 19 neurorights amendment (programmatic; implementing law PENDING)",
           "status": "PENDING_IMPLEMENTATION",
           "requires": ["purpose_limitation", "consent_record", "deletion_path"]},
    "EU": {"law": "GDPR Art. 9 special-category data + Art. 6 lawful basis",
           "status": "ENACTED",
           "requires": ["lawful_basis", "purpose_limitation", "consent_record", "deletion_path", "access_request_path", "no_sale_default", "dpia_reference"]},
}


def build_manifest(path, owner="", jurisdiction="US-CA", contact="UNSET", fmt="json"):
    pack = LAW_PACKS.get(jurisdiction, LAW_PACKS["US-CA"])
    manifest = {
        "ndrm_version": "0.2",
        "dataset": os.path.basename(path),
        "owner": owner or "UNSET",
        "generated": time.strftime("%Y-%m-%d"),
        "jurisdiction": jurisdiction,
        "applicable_law": pack["law"],
        "law_status": pack["status"],
        "allowed_uses": ["research"],
        "sale": False,
        "revocation_contact": contact,
        "required_controls": pack["requires"],
        "provenance_chain": [],          # [{actor, action, timestamp, artifact_hash}]
        "consent_artifacts": [],         # [{subject_ref, session_ref, artifact_uri, sha256, date}]
        "cross_border_transfers": {"allowed": False, "mechanisms": [], "notes": ""},
        "retention_schedule": "UNSET",
        "security_controls": [],
        "revocation_trail": [],          # [{date, what, signed_by}]
    }
    if fmt == "json":
        out = os.path.join(path, "ndrm.json")
        with open(out, "w") as f:
            json.dump(manifest, f, indent=2)
    else:  # yaml twin kept for human review
        out = os.path.join(path, "ndrm.yaml")
        with open(out, "w") as f:
            f.write("# NeuroData Rights Manifest v0.2 (canonical: ndrm.json; BIDS-friendly)\n")
            f.write(yaml.safe_dump(manifest, sort_keys=False))
    return manifest


def check_manifest(path):
    mfile = os.path.join(path, "ndrm.json")
    if not os.path.exists(mfile):
        mfile = os.path.join(path, "ndrm.yaml")  # legacy accepted, flagged
        if not os.path.exists(mfile):
            return {"verdict": "FAIL", "reason": f"no ndrm.json in {path}",
                    "fix": "run: neurogate init " + path}
        legacy = True
    else:
        legacy = False
    m = (json.load if mfile.endswith(".json") else yaml.safe_load)(open(mfile))
    pack = LAW_PACKS.get(m.get("jurisdiction", ""), LAW_PACKS["US-CA"])
    missing = [c for c in pack["requires"] if c not in m.get("required_controls", [])]
    unset = [k for k in ("owner", "revocation_contact", "retention_schedule") if m.get(k) == "UNSET"]
    pending = pack["status"] == "PENDING_IMPLEMENTATION"
    checks = [{"check": f"control:{c}", "ok": c not in missing} for c in pack["requires"]]
    checks += [{"check": f"field:{k}", "ok": k not in unset} for k in ("owner", "revocation_contact", "retention_schedule")]
    checks.append({"check": "no_sale_default", "ok": m.get("sale") is False})
    checks.append({"check": "consent_artifacts_linked", "ok": len(m.get("consent_artifacts", [])) > 0})
    checks.append({"check": "format:bids-compatible-json", "ok": not legacy})
    verdict = "PASS" if not missing and not unset and not legacy else "FAIL"
    return {"verdict": verdict, "jurisdiction": m.get("jurisdiction"), "law": pack["law"],
            "law_status": pack["status"], "implementing_law_pending": pending,
            "missing_controls": missing, "unset_fields": unset, "checks": checks,
            "notes": ["migrate ndrm.yaml → ndrm.json for BIDS/DANDI first-class acceptance"] if legacy else []}
