"""NeuroGate v0.3 tests — regression cases for every reproduced defect in the
external frontier review. Test count is NOT evidence; each test targets a
specific false-PASS / schema / honesty defect."""
import os, sys, json, tempfile
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from neurogate.ndrm import (new_manifest_draft, check_manifest, validate_schema,
                            migrate, SchemaError, MAPPINGS, SUPPORTED_SCHEMA_VERSIONS)
from neurogate.bench import run_benchmark, list_benchmarks, _run_synthetic_regression


def _draft(d, **kw):
    kw.setdefault("responsible_organization", "Lab")
    kw.setdefault("contact", "p@lab.org")
    kw.setdefault("jurisdiction", "US-CA")
    return new_manifest_draft(d, **kw)


def _fill_complete(d):
    """Fill a draft to the READY_FOR_REVIEW edge (machine-checkable only)."""
    p = os.path.join(d, "ndrm.json")
    m = json.load(open(p))
    m["manifest_id"] = "mf-001"
    m["dataset"].update({"id": "ds-1", "version": "v1.0", "modality": "ecog"})
    m["responsibility"]["custodian"] = "Custodian Name"
    m["rights"]["license"] = "CC-BY-4.0"
    m["lifecycle"]["retention_rationale"] = "5 years post-study"
    m["proposed_use"]["purpose"] = "offline decoder evaluation by lab members"
    m["scope"]["jurisdictions"] = [{"jurisdiction": "US-CA", "assessment_status": "reviewed"}]
    m["policy_mapping"] = {"mapping_id": MAPPINGS["US-CA"]["mapping_id"],
                           "version": MAPPINGS["US-CA"]["version"],
                           "reviewed_by": "Dr. Reviewer", "reviewed_date": "2026-09-22"}
    json.dump(m, open(p, "w"))


def _set(d, path, value):
    p = os.path.join(d, "ndrm.json")
    m = json.load(open(p))
    cur = m
    for k in path[:-1]:
        cur = cur.setdefault(k, {})
    cur[path[-1]] = value
    json.dump(m, open(p, "w"))
    return m


# ---------- verdict honesty (P0: eliminate false successful verdicts) ----------

def test_sale_true_never_passes():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("sale",), True)
        assert check_manifest(d)["assessment"] != "READY_FOR_REVIEW"


def test_missing_required_keys_never_pass():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        p = os.path.join(d, "ndrm.json")
        m = json.load(open(p))
        for grp in ("responsibility", "rights", "lifecycle"):
            m[grp] = {}
        m["manifest_id"] = None
        json.dump(m, open(p, "w"))
        rec = check_manifest(d)
        assert rec["assessment"] in ("INCOMPLETE", "BLOCKED")
        rules = {f["rule_id"] for f in rec["findings"]}
        assert "schema.required.responsibility.responsible_organization" in rules


def test_blank_strings_rejected():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("responsibility", "contact"), "   ")
        rec = check_manifest(d)
        assert rec["assessment"] in ("INCOMPLETE", "BLOCKED")
        assert any(f["rule_id"] == "schema.required.responsibility.contact" for f in rec["findings"])


def test_unknown_jurisdiction_never_falls_back():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("scope", "jurisdictions"), [{"jurisdiction": "XX-UNKNOWN", "assessment_status": "reviewed"}])
        rec = check_manifest(d)
        assert rec["assessment"] == "INCOMPLETE"
        rules = {f["rule_id"] for f in rec["findings"]}
        assert "policy.applicability" in rules


def test_empty_consent_blocks_ready_for_human():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        rec = check_manifest(d)  # human + no consent artifacts
        assert rec["assessment"] != "READY_FOR_REVIEW"
        assert any(f["rule_id"] == "evidence.consent_missing" for f in rec["findings"])


def test_synthetic_dataset_no_consent_needed():
    with tempfile.TemporaryDirectory() as d:
        _draft(d, classification="synthetic"); _fill_complete(d)
        rec = check_manifest(d)
        assert rec["assessment"] == "READY_FOR_REVIEW", rec


def test_unreviewed_mapping_blocks():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("policy_mapping",), {"mapping_id": MAPPINGS["US-CA"]["mapping_id"],
                                      "version": "0.3-experimental", "reviewed_by": "",
                                      "reviewed_date": ""})
        rec = check_manifest(d)
        assert rec["assessment"] == "INCOMPLETE"
        assert any(f["rule_id"] == "policy.mapping_unreviewed" for f in rec["findings"])


def test_full_ready_path():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("evidence", "consent_artifacts"),
             [{"subject_ref": "opaque-1", "session_ref": "s1", "artifact_uri": "evidence/consent-1.json",
               "sha256": "a" * 64, "date": "2026-01-01"}])
        rec = check_manifest(d)
        assert rec["assessment"] == "READY_FOR_REVIEW", rec["findings"]
        assert rec["legal_compliance_determined"] is False  # always


# ---------- strict schema & version handling (P0) ----------

def test_unsupported_version_is_error():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("ndrm_version",), "999")
        rec = check_manifest(d)
        assert rec["assessment"] == "ERROR"
        assert any("schema.version_unsupported" == f["rule_id"] for f in rec["findings"])


def test_controls_string_type_rejected():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("controls", "declared"), "deletion_path purpose_limitation")  # substring trick
        assert check_manifest(d)["assessment"] == "ERROR"


def test_consent_artifacts_null_type_rejected():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("evidence", "consent_artifacts"), None)
        rec = check_manifest(d)
        assert rec["assessment"] == "ERROR"
        assert any(f["rule_id"] == "schema.type.consent_artifacts" for f in rec["findings"])


def test_root_not_object_is_structured_error():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        open(os.path.join(d, "ndrm.json"), "w").write(json.dumps([1, 2, 3]))
        rec = check_manifest(d)
        assert rec["assessment"] == "ERROR" and rec["schema_result"] == "ERROR"


def test_duplicate_json_keys_rejected():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        open(os.path.join(d, "ndrm.json"), "w").write('{"ndrm_version": "0.3", "ndrm_version": "0.2"}')
        rec = check_manifest(d)
        assert rec["assessment"] == "ERROR"


def test_garbage_json_is_structured_error():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        open(os.path.join(d, "ndrm.json"), "w").write("{not json")
        rec = check_manifest(d)
        assert rec["assessment"] == "ERROR"


def test_unsafe_evidence_uri_rejected():
    with tempfile.TemporaryDirectory() as d:
        _draft(d); _fill_complete(d)
        _set(d, ("evidence", "consent_artifacts"),
             [{"subject_ref": "s", "artifact_uri": "https://evil.example/consent", "sha256": "b" * 64}])
        rec = check_manifest(d)
        assert any(f["rule_id"] == "evidence.unsafe_path" for f in rec["findings"])
        assert rec["assessment"] != "READY_FOR_REVIEW"


def test_referenced_without_digest_flagged():
    with tempfile.TemporaryDirectory() as d:
        _draft(d, classification="nonhuman"); _fill_complete(d)
        _set(d, ("evidence", "consent_artifacts"),
             [{"subject_ref": "s", "artifact_uri": "evidence/x.json"}])
        rec = check_manifest(d)
        assert any(f["rule_id"] == "evidence.digest_missing" for f in rec["findings"])
        assert rec["evidence_status"] == "referenced"


# ---------- nondestructive init (P0) ----------

def test_init_refuses_overwrite():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        try:
            _draft(d)
            assert False, "overwrite should have raised"
        except SchemaError as e:
            assert e.rule_id == "init.refuse_overwrite"


# ---------- migration ----------

def test_migrate_preserves_prior_file():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        p = os.path.join(d, "ndrm.json")
        m = json.load(open(p)); m["ndrm_version"] = "0.2"
        json.dump(m, open(p, "w"))
        res = migrate(d, to="0.3")
        assert res["migrated"] is True and os.path.exists(res["preserved"])
        assert json.load(open(p))["ndrm_version"] == "0.3"


def test_migrate_target_version_supported():
    with tempfile.TemporaryDirectory() as d:
        _draft(d)
        try:
            migrate(d, to="999")
            assert False, "unsupported target should raise"
        except SchemaError as e:
            assert e.rule_id == "migrate.unsupported_version"


# ---------- benchmarks: real computation, honest statuses ----------

def test_synthetic_regression_is_real():
    r = _run_synthetic_regression(seed=42)
    assert isinstance(r["held_out_r2"], float) and 0.2 < r["held_out_r2"] < 1.0
    assert r["shuffled_target_r2"] < 0.15          # control: no transfer (may be negative)
    assert r["clean_fixture_r2"] > 0.99             # control: metric recovers clean signal


def test_synthetic_reproducible():
    a = _run_synthetic_regression(seed=7)
    b = _run_synthetic_regression(seed=7)
    assert a["held_out_r2"] == b["held_out_r2"]


def test_bench_synthetic_scores():
    res = run_benchmark("synthetic-regression-v0")
    assert res["status"] == "COMPLETED_SYNTHETIC_ONLY"
    assert res["provenance"] == "local-synthetic (fully reproducible, no external data)"
    assert res["held_out_r2"] is not None and 0 < res["held_out_r2"] <= 1.0


def test_bench_planned_tasks_return_no_score():
    for name in ("falcon-h1-motor", "moabb-eeg-example"):
        res = run_benchmark(name)
        assert res["status"] == "PLANNED" and res["score"] is None


def test_bench_unknown_returns_error():
    res = run_benchmark("nonexistent-bench")
    assert "error" in res and res.get("exit_code") == 2


def test_no_bits_per_minute_claim():
    lines = "\n".join(list_benchmarks())
    assert "bits_per_minute" not in lines  # arbitrary scalar naming retired


def test_bench_count():
    assert len(list_benchmarks()) == 3  # 1 runnable + 2 planned


# ---------- policy mappings ----------

def test_mappings_scoped_and_versioned():
    for code, mp in MAPPINGS.items():
        assert mp["mapping_id"] and mp["version"] and mp["sources"] and mp["scope_assumptions"]
        assert mp["status"] in ("EXPERIMENTAL", "RESEARCH_DRAFT", "REVIEWED")


def test_no_universal_no_sale_from_law():
    # no-sale is PROJECT POLICY, never attributed to statute
    mp = MAPPINGS["US-CO"]
    assert "no_sale" not in " ".join(mp["sources"]).lower()