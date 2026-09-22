"""NeuroData Rights Manifest (NDRM) — the core governance primitive.

A tiny YAML sidecar next to any neural dataset declaring:
who owns it, which law packs apply, allowed uses, and revocation contact.
Law packs encode the practical requirements of CO HB24-1058, CA CPRA neural-data
provisions (AB 1274 class), and Chile's constitutional neurorights amendment.
"""
import os, yaml, datetime

LAW_PACKS = {
    "US-CO": {"law": "Colorado HB24-1058 (neural data = sensitive biometric)",
              "requires": ["purpose_limitation", "consent_record", "deletion_path", "no_sale_default"]},
    "US-CA": {"law": "California CPRA neural-data provisions",
              "requires": ["purpose_limitation", "consent_record", "deletion_path", "no_sale_default", "access_request_path"]},
    "CL": {"law": "Chile Constitution Art. 19 neurorights amendment",
           "requires": ["identity_integrity_statement", "purpose_limitation", "consent_record", "deletion_path"]},
    "EU": {"law": "GDPR Art.9 special-category analog",
           "requires": ["lawful_basis", "purpose_limitation", "consent_record", "deletion_path", "access_request_path", "no_sale_default"]},
}


def build_manifest(path, owner="", jurisdiction="US-CA"):
    pack = LAW_PACKS.get(jurisdiction, LAW_PACKS["US-CA"])
    manifest = {
        "ndrm_version": "0.1",
        "dataset": os.path.basename(path),
        "owner": owner or "UNSET",
        "generated": time.strftime("%Y-%m-%d"),
        "jurisdiction": jurisdiction,
        "applicable_law": pack["law"],
        "allowed_uses": ["research"],
        "sale": False,
        "revocation_contact": "UNSET",
        "required_controls": pack["requires"],
    }
    out = os.path.join(path, "ndrm.yaml")
    with open(out, "w") as f:
        f.write("# NeuroData Rights Manifest v0.1 — commit beside your data\n")
        f.write("# Laws covered: " + pack["law"] + "\n")
        f.write(yaml.safe_dump(manifest, sort_keys=False))
    return manifest


def check_manifest(path):
    mfile = os.path.join(path, "ndrm.yaml")
    if not os.path.exists(mfile):
        return {"verdict": "FAIL", "reason": f"no ndrm.yaml in {path}",
                "fix": "run: neurogate init " + path}
    m = yaml.safe_load(open(mfile))
    pack = LAW_PACKS.get(m.get("jurisdiction", ""), LAW_PACKS["US-CA"])
    missing = [c for c in pack["requires"] if c not in m.get("required_controls", [])]
    unset = [k for k in ("owner", "revocation_contact") if m.get(k) == "UNSET"]
    checks = [{"check": f"control:{c}", "ok": c not in missing} for c in pack["requires"]]
    checks += [{"check": f"field:{k}", "ok": k not in unset} for k in ("owner", "revocation_contact")]
    checks.append({"check": "no_sale_default", "ok": m.get("sale") is False})
    return {"verdict": "PASS" if not missing and not unset else "FAIL",
            "jurisdiction": m.get("jurisdiction"), "law": pack["law"],
            "missing_controls": missing, "unset_fields": unset, "checks": checks}


import time  # noqa: E402  (used by build_manifest)
