"""NeuroData Rights Manifest (NDRM) v0.3 — documentation & evidence primitive.

HONEST RESULT SEMANTICS (external frontier review, 2026-09-22):
  SCHEMA_VALID      input conforms to the supported structural schema only
  INCOMPLETE        required facts, evidence, or applicability decisions unresolved
  BLOCKED           a known required condition for the requested workflow is unsatisfied
  READY_FOR_REVIEW  all machine-checkable requirements in the selected scope are
                    satisfied; human/legal conclusions remain attributed separately
  ERROR             input unparseable, version unsupported, or operation failed

This tool assesses DOCUMENTED conditions. It does NOT certify legal compliance,
validate consent from a hash, or establish clinical performance.

Design per external review: one experimental US-CA policy mapping; CO/EU/CL are
research drafts. Unknown jurisdictions NEVER silently fall back. Duplicate JSON
keys rejected. Evidence paths constrained to safe local relative paths. No
network access during validation. Field contents are data, never commands.
"""
import os, json, time, re, hashlib, copy

SUPPORTED_SCHEMA_VERSIONS = {"0.3"}
CANONICAL_FILE = "ndrm.json"

# --- Scoped, versioned policy mappings (source-backed, human-review-gated) ---
# Status ladder: RESEARCH_DRAFT < EXPERIMENTAL < REVIEWED (requires named human reviewer + date)
MAPPINGS = {
    "US-CA": {
        "mapping_id": "policy-mapping-us-ca-sb1223",
        "version": "0.3-experimental",
        "status": "EXPERIMENTAL",
        "sources": [
            "California SB1223 (2024): neural data added to CCPA 'sensitive personal "
            "personal information'; excludes data inferred from nonneural information",
            "CCPA/CPRA general rights: access, deletion, correction, limit-use of sensitive PI",
        ],
        "effective_interval": "2024-01-01/open",
        "scope_assumptions": [
            "applies only to businesses meeting CCPA thresholds/exemptions",
            "no neural-specific access right exists; access is the general CCPA right",
            "neither generic research consent nor a blanket sale ban is a universal substitute",
        ],
        "notes": "EXPERIMENTAL: machine-checkable documentation checks only. Human legal review REQUIRED before any compliance reliance.",
    },
    "US-CO": {
        "mapping_id": "policy-mapping-us-co-hb24-1058",
        "version": "0.3-research-draft",
        "status": "RESEARCH_DRAFT",
        "sources": [
            "Colorado HB24-1058 (2024): adds 'biological data' incl. neural data to CPA sensitive data",
            "Colorado Privacy Act (CPA) supplies scope, exceptions, duties, rights",
        ],
        "effective_interval": "2024-08-01/open",
        "scope_assumptions": [
            "biological-data definition contains identification-related language",
            "universal no-sale requirement is NOT established by the amendment alone",
        ],
        "notes": "RESEARCH DRAFT: not reviewed by a qualified Colorado privacy attorney.",
    },
    "EU-GDPR": {
        "mapping_id": "policy-mapping-eu-gdpr",
        "version": "0.3-research-draft",
        "status": "RESEARCH_DRAFT",
        "sources": [
            "GDPR Art. 6 lawful basis + Art. 9 special-category condition (kept separate)",
            "DPIA driven by likely high risk (Art. 35), not merely presence of neural data",
        ],
        "effective_interval": "2018-05-25/open",
        "scope_assumptions": [
            "research participation consent is not automatically the legal basis for all processing",
        ],
        "notes": "RESEARCH DRAFT: applicability analysis (establishment, controller, residence) required.",
    },
    "CL": {
        "mapping_id": "policy-mapping-cl-neurorights",
        "version": "0.3-research-draft",
        "status": "RESEARCH_DRAFT",
        "sources": [
            "Chile Law 21.383: constitutional Art. 19(1) neurorights (programmatic; no manifest field prescribed)",
            "Chile Law 21.719: comprehensive data-protection law, transition to 2026-12-01",
        ],
        "effective_interval": "constitutional: open; Law 21.719: 2026-12-01/open",
        "scope_assumptions": [
            "constitutional source kept distinct from operative privacy law",
            "do not apply future rules as already effective",
        ],
        "notes": "RESEARCH DRAFT: unresolved local legal interpretation must stay unresolved.",
    },
}

REQUIRED_FIELD_PATHS = [  # (key path) — blank/missing -> INCOMPLETE
    ("manifest_id",),
    ("dataset", "id"),
    ("dataset", "version"),
    ("dataset", "classification"),
    ("dataset", "modality"),
    ("responsibility", "responsible_organization"),
    ("responsibility", "custodian"),
    ("responsibility", "contact"),
    ("rights", "license"),
    ("lifecycle", "retention_rationale"),
]

_SAFE_URI_RE = __import__("re").compile(r"^(?!.*(^|[\\/])\.\.([\\/]|$))[\w\-./@:]+$")


class SchemaError(Exception):
    """Structured input error — carries rule_id and remedy."""
    def __init__(self, rule_id, reason, remedy):
        super().__init__(reason)
        self.rule_id = rule_id
        self.reason = reason
        self.remedy = remedy

    def finding(self):
        return {"rule_id": self.rule_id, "result": "ERROR", "severity": "error",
                "evidence_status": "none", "remedy": self.remedy}


def _no_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"duplicate JSON key: {k}")
        d[k] = v
    return d


def _load_manifest(path):
    """Bounded local parse. JSON canonical; YAML accepted as input (not a defect)."""
    jf, yf = os.path.join(path, "ndrm.json"), os.path.join(path, "ndrm.yaml")
    if os.path.exists(jf):
        raw = open(jf, "rb").read()
        if len(raw) > 1_000_000:
            raise SchemaError("schema.file_too_large", "ndrm.json exceeds 1 MB bound",
                              "split oversized manifests; keep manifests small")
        try:
            m = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_dupes)
        except (ValueError, UnicodeDecodeError) as e:
            raise SchemaError("schema.parse_error", f"invalid JSON: {e}",
                              "fix JSON syntax; duplicate keys are rejected")
        if not isinstance(m, dict):
            raise SchemaError("schema.root_type", "manifest root must be a JSON object",
                              "top-level {} required")
        return m, "json"
    if os.path.exists(yf):
        import yaml
        try:
            m = yaml.safe_load(open(yf))
        except Exception as e:
            raise SchemaError("schema.parse_error", f"invalid YAML: {e}", "fix YAML syntax")
        if not isinstance(m, dict):
            raise SchemaError("schema.root_type", "manifest root must be a mapping",
                              "top-level mapping required")
        return m, "yaml"
    raise SchemaError("schema.manifest_missing", f"no ndrm.json in {path}",
                      "run: neurogate init " + path)


def _blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "") or v == "UNSET"


def _get(m, *keys):
    cur = m
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _draft_shape(responsible_organization="", contact="", jurisdiction="US-CA",
                 dataset_id="", classification="human", modality=""):
    """The v0.3 draft manifest dict (deliberately incomplete)."""
    manifest = {
        "ndrm_version": "0.3",
        "manifest_id": "",
        "dataset": {"id": dataset_id, "version": "", "inventory_digest": "",
                    "classification": classification, "modality": modality},
        "responsibility": {"responsible_organization": responsible_organization,
                           "custodian": "", "contact": contact, "author": "", "reviewer": ""},
        "scope": {"jurisdictions": [{"jurisdiction": jurisdiction,
                                     "assessment_status": "unreviewed",
                                     "notes": "applicability not yet assessed"}]},
        "proposed_use": {"purpose": "", "recipients": "", "commercial": None,
                         "training": False, "inference": False, "evaluation": True},
        "rights": {"license": "", "privacy_restrictions": [], "consent_basis": "",
                   "duo_terms": []},
        "evidence": {"consent_artifacts": [],   # [{subject_ref,session_ref,artifact_uri,sha256,date}]
                     "provenance_chain": [], "security_controls": []},
        "controls": {"declared": [], "implementation_evidence": [], "observed_tests": []},
        "lifecycle": {"retention_rationale": "", "rights_request_process": "",
                      "withdrawal_limitations": "", "incident_history": []},
        "policy_mapping": {"mapping_id": None, "version": None, "status": "unselected",
                           "reviewed_by": "", "reviewed_date": ""},
        "derivations": {"parent_datasets": [], "preprocessing_revision": "",
                        "derived_artifacts": []},
        "project_policy": {"no_sale_default": True,  # NeuroGate default — PROJECT POLICY, not law
                           "note": "projects may choose stricter defaults; label them here"},
        "sale": False,
        "cross_border_transfers": {"allowed": None, "mechanisms": [], "notes": ""},
        "generated": __import__("time").strftime("%Y-%m-%d"),
    }
    return manifest


def new_manifest_draft(path, responsible_organization="", contact="", jurisdiction="US-CA",
                       dataset_id="", classification="human", modality=""):
    """Write a deliberately INCOMPLETE v0.3 draft. Refuses to overwrite."""
    out = os.path.join(path, "ndrm.json")
    if os.path.exists(out):
        raise SchemaError("init.refuse_overwrite",
                          f"{out} already exists; init is nondestructive",
                          "use: neurogate migrate (versioned update) or --force (explicit replacement)")
    manifest = _draft_shape(responsible_organization, contact, jurisdiction,
                            dataset_id, classification, modality)
    os.makedirs(path, exist_ok=True)
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def migrate(path, to="0.3"):
    """Versioned, reviewable update. Prior file preserved as ndrm-v<prev>.json.bak."""
    m, fmt = _load_manifest(path)
    prev_version = str(m.get("ndrm_version", "?"))
    if to not in SUPPORTED_SCHEMA_VERSIONS:
        raise SchemaError("migrate.unsupported_version", f"target {to} unsupported",
                          f"supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
    if prev_version == to:
        return {"migrated": False, "reason": f"already at {to}"}
    prev_file = os.path.join(path, "ndrm.json" if fmt == "json" else "ndrm.yaml")
    bak = os.path.join(path, f"ndrm-v{prev_version}.json.bak")
    if fmt == "json":
        old = copy.deepcopy(m)
        manifest = _draft_shape(contact=old.get("revocation_contact", ""))
        # build from old, preserving known values
        manifest["manifest_id"] = old.get("manifest_id", "")
        if "owner" in old:
            manifest["responsibility"]["responsible_organization"] = old.get("owner", "")
            manifest["responsibility"]["contact"] = old.get("revocation_contact", "")
        if "dataset" in old and isinstance(old["dataset"], dict):
            manifest["dataset"]["id"] = old["dataset"].get("id", old.get("dataset", ""))
        manifest["jurisdictions_note"] = "migrated from v" + prev_version
        for key in ("evidence", "lifecycle", "derivations", "project_policy", "sale"):
            if key in old:
                if isinstance(manifest.get(key), dict) and isinstance(old[key], dict):
                    manifest[key].update({k: v for k, v in old[key].items() if v not in (None, "", [])})
                else:
                    manifest[key] = old[key]
        with open(bak, "w") as f:
            json.dump(old, f, indent=2)
        with open(prev_file, "w") as f:
            json.dump(manifest, f, indent=2)
        return {"migrated": True, "from": prev_version, "to": to, "preserved": bak,
                "review": "diff required before use; migrated fields carry over verbatim"}
    raise SchemaError("migrate.format", "migrate requires canonical ndrm.json",
                      "convert YAML to JSON first (re-run init in a fresh dir, then diff)")


def _evidence_status_of(consent_artifacts):
    if not consent_artifacts:
        return "none"
    statuses = set()
    for a in consent_artifacts:
        if not isinstance(a, dict):
            continue
        if a.get("human_reviewed"):
            statuses.add("human_reviewed")
        elif a.get("sha256"):
            statuses.add("digest_checked")
        elif a.get("artifact_uri"):
            statuses.add("referenced")
        else:
            statuses.add("declared")
    order = ["none", "declared", "referenced", "digest_checked", "human_reviewed"]
    return max(statuses, key=order.index)


def validate_schema(path):
    """Structural validation only. Returns receipt with schema_result."""
    try:
        m, fmt = _load_manifest(path)
    except SchemaError as e:
        return _receipt(None, path, "ERROR", "ERROR", requested_use=None,
                        findings=[e.finding()], evidence_status="none", fmt=None)
    findings = []
    if str(m.get("ndrm_version")) not in SUPPORTED_SCHEMA_VERSIONS:
        findings.append({"rule_id": "schema.version_unsupported", "result": "ERROR",
                         "severity": "error", "evidence_status": "none",
                         "remedy": f"supported versions: {sorted(SUPPORTED_SCHEMA_VERSIONS)}; use neurogate migrate"})
    # type discipline
    controls = m.get("controls", {}).get("declared") if isinstance(m.get("controls"), dict) else None
    if not isinstance(controls, list):
        findings.append({"rule_id": "schema.type.controls_declared", "result": "ERROR",
                         "severity": "error", "evidence_status": "none",
                         "remedy": "controls.declared must be a JSON array of strings"})
    ca = m.get("evidence", {}).get("consent_artifacts") if isinstance(m.get("evidence"), dict) else None
    if ca is not None and not isinstance(ca, list):
        findings.append({"rule_id": "schema.type.consent_artifacts", "result": "ERROR",
                         "severity": "error", "evidence_status": "none",
                         "remedy": "evidence.consent_artifacts must be a JSON array (use [] for none)"})
    if not isinstance(m.get("sale"), bool):
        findings.append({"rule_id": "schema.type.sale", "result": "ERROR",
                         "severity": "error", "evidence_status": "none",
                         "remedy": "sale must be a boolean"})
    valid = not any(f["result"] == "ERROR" for f in findings)
    return _receipt(m if valid else None, path,
                    "SCHEMA_VALID" if valid else "ERROR",
                    "SCHEMA_VALID" if valid else "ERROR",
                    _get(m, "proposed_use", "purpose") if valid else None,
                    findings, "none", fmt)


def check_manifest(path, requested_use=None):
    """Full documented-conditions check with honest assessment semantics."""
    findings = []

    def add(rule_id, result, severity, evidence_status, remedy):
        findings.append({"rule_id": rule_id, "result": result, "severity": severity,
                         "evidence_status": evidence_status, "remedy": remedy})

    try:
        m, fmt = _load_manifest(path)
    except SchemaError as e:
        return _receipt(None, path, "ERROR", "ERROR", requested_use,
                        [e.finding()], "none", None)

    # --- schema version ---
    version = str(m.get("ndrm_version", ""))
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        return _receipt(m, path, "ERROR", "ERROR", requested_use,
                        [{"rule_id": "schema.version_unsupported", "result": "ERROR",
                          "severity": "error", "evidence_status": "none",
                          "remedy": f"manifest version {version!r} unsupported "
                                    f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}); run neurogate migrate"}],
                        "none", fmt)
    if not isinstance(m.get("sale"), bool):
        return _receipt(m, path, "ERROR", "ERROR", requested_use,
                        [{"rule_id": "schema.type.sale", "result": "ERROR", "severity": "error",
                          "evidence_status": "none", "remedy": "sale must be true or false"}],
                        "none", fmt)
    ca = m.get("evidence", {}).get("consent_artifacts")
    if ca is None:
        # null is NOT silently accepted: an explicit null must be normalized by the author
        return _receipt(m, path, "ERROR", "ERROR", requested_use,
                        [{"rule_id": "schema.type.consent_artifacts", "result": "ERROR",
                          "severity": "error", "evidence_status": "none",
                          "remedy": "evidence.consent_artifacts must be an array; use [] for none"}],
                        "none", fmt)
    elif not isinstance(ca, list):
        return _receipt(m, path, "ERROR", "ERROR", requested_use,
                        [{"rule_id": "schema.type.consent_artifacts", "result": "ERROR",
                          "severity": "error", "evidence_status": "none",
                          "remedy": "evidence.consent_artifacts must be an array; use [] for none"}],
                        "none", fmt)
    controls = m.get("controls", {}).get("declared")
    if controls is not None and not isinstance(controls, list):
        return _receipt(m, path, "ERROR", "ERROR", requested_use,
                        [{"rule_id": "schema.type.controls", "result": "ERROR", "severity": "error",
                          "evidence_status": "none",
                          "remedy": "controls.declared must be an array (substring membership is not schema validation)"}],
                        "none", fmt)

    # --- required-field completeness (missing/blank -> INCOMPLETE, never PASS) ---
    for keys in REQUIRED_FIELD_PATHS:
        val = _get(m, *keys)
        if _blank(val):
            add("schema.required." + ".".join(keys), "FAIL", "block", "declared",
                f"set {'.'.join(keys)} (currently missing/blank)")

    # --- applicability: jurisdictions + scoped policy mappings (never silent fallback) ---
    scope = m.get("scope", {})
    jurs = scope.get("jurisdictions") if isinstance(scope, dict) else None
    if not jurs or not isinstance(jurs, list):
        add("policy.applicability", "UNKNOWN", "block", "declared",
            "declare scope.jurisdictions with per-jurisdiction assessment_status")
    else:
        for j in jurs:
            code = j.get("jurisdiction") if isinstance(j, dict) else None
            if not code or code not in MAPPINGS:
                add("policy.applicability", "UNKNOWN", "block", "declared",
                    f"jurisdiction {code!r} has no policy mapping; it will NOT be silently "
                    f"substituted — add a scoped mapping or remove it")
                continue
            mp = MAPPINGS[code]
            # manifest may declare a human reviewer for the mapping (evidence_status: declared)
            pm = m.get("policy_mapping", {}) or {}
            if _blank(pm.get("reviewed_by")) or _blank(pm.get("reviewed_date")):
                add("policy.mapping_unreviewed", "UNKNOWN", "block", "declared",
                    f"mapping {mp['mapping_id']} is {mp['status']}: requires named human "
                    f"reviewer + reviewed_date in policy_mapping before READY_FOR_REVIEW")
            else:
                add("policy.mapping_reviewed", "PASS", "info", "declared",
                    f"mapping review DECLARED by {pm['reviewed_by']} on {pm['reviewed_date']}; "
                    "a declaration is not independent verification")

    # --- requested use ---
    purpose = _get(m, "proposed_use", "purpose")
    use = requested_use or purpose
    if _blank(use):
        add("policy.use_undocumented", "UNKNOWN", "block", "declared",
            "document proposed_use.purpose (concrete purpose, recipient class, train/infer/eval)")

    # --- project policy: no-sale default (labeled project policy, NOT law) ---
    if m.get("sale") is True:
        add("policy.no_sale_default", "FAIL", "block", "declared",
            "manifest declares sale=true; NeuroGate project policy prohibits sale. "
            "Set sale=false or document a reviewed project-policy exception")
    else:
        add("policy.no_sale_default", "PASS", "info", "declared",
            "no-sale default holds (project policy, not a statutory requirement)")

    # --- evidence: consent (human data) + safe paths ---
    classification = _get(m, "dataset", "classification") or ""
    if isinstance(ca, list):
        if classification == "human" and len(ca) == 0:
            add("evidence.consent_missing", "UNKNOWN", "block", "none",
                "human-subject dataset has no consent_artifacts; reference consent "
                "evidence (opaque refs + sha256 digests) or classify as nonhuman/synthetic")
        for a in ca:
            if isinstance(a, dict):
                uri = a.get("artifact_uri", "")
                if uri and (uri.startswith(("http://", "https://", "ftp://")) or ".." in uri
                            or os.path.isabs(uri)):
                    add("evidence.unsafe_path", "FAIL", "block", "declared",
                        f"artifact_uri must be a safe local relative path (got {uri[:40]!r}); "
                        "manifests never execute or fetch — treat contents as data")
                elif uri and not a.get("sha256"):
                    add("evidence.digest_missing", "UNKNOWN", "block", "referenced",
                        f"artifact {uri[:40]!r} referenced without sha256 digest")

    # --- assessment roll-up: every finding affects the decision ---
    has_error = any(f["result"] == "ERROR" for f in findings)
    has_block_fail = any(f["result"] in ("FAIL", "ERROR") and f["severity"] in ("block", "error") for f in findings)
    has_open = any(f["result"] in ("FAIL", "UNKNOWN") for f in findings)
    if has_error:
        assessment = "ERROR"
    elif has_block_fail:
        assessment = "BLOCKED"
    elif has_open:
        assessment = "INCOMPLETE"
    else:
        assessment = "READY_FOR_REVIEW"

    worst = "none"
    order = ["none", "declared", "referenced", "digest_checked", "human_reviewed"]
    for f in findings:
        if f["evidence_status"] in order and order.index(f["evidence_status"]) > order.index(worst):
            worst = f["evidence_status"]
    return _receipt(m, path, "SCHEMA_VALID", assessment, use, findings, worst, fmt)


def _receipt(m, path, schema_result, assessment, requested_use, findings, evidence_status, fmt):
    return {
        "receipt_version": "0.3",
        "operation": "check",
        "path": path,
        "manifest_id": (m or {}).get("manifest_id", None) if m else None,
        "dataset_id": _get(m or {}, "dataset", "id") if m else None,
        "manifest_format": fmt,
        "schema_result": schema_result,
        "assessment": assessment_local(schema_result, findings) if schema_result != "ERROR" or findings == [] else schema_result if schema_result == "ERROR" else assessment_local(schema_result, findings),
        "requested_use": requested_use,
        "evidence_status": evidence_status,
        "findings": findings,
        "benchmark": {"status": "NOT_RUN", "score": None},
        "legal_compliance_determined": False,
        "note": ("checks assess documented conditions only; they do not certify legal "
                 "compliance, validate consent from a hash, or establish clinical performance"),
    }


def assessment_local(schema_result, findings):
    if schema_result == "ERROR":
        return "ERROR"
    if any(f["result"] in ("FAIL", "ERROR") and f["severity"] in ("block", "error") for f in findings):
        return "BLOCKED"
    if any(f["result"] in ("FAIL", "UNKNOWN") for f in findings):
        return "INCOMPLETE"
    return "READY_FOR_REVIEW"