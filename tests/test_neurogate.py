import os, sys, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from neurogate.ndrm import build_manifest, check_manifest, LAW_PACKS
from neurogate.bench import run_benchmark, list_benchmarks


def test_init_and_check_pass():
    with tempfile.TemporaryDirectory() as d:
        m = build_manifest(d, owner="Test Owner", jurisdiction="US-CA", contact="t@example.org")
        assert os.path.exists(os.path.join(d, "ndrm.json"))
        res = check_manifest(d)
        # retention_schedule defaults UNSET in v0.2 unless provided — fill for pass
        import json as j
        m2 = j.load(open(os.path.join(d, "ndrm.json")))
        m2["retention_schedule"] = "5 years post-study"
        j.dump(m2, open(os.path.join(d, "ndrm.json"), "w"))
        res = check_manifest(d)
        assert res["verdict"] == "PASS", res


def test_check_missing_manifest():
    with tempfile.TemporaryDirectory() as d:
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "no ndrm.json" in res["reason"]


def test_missing_control_fails():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="US-CA", contact="t@example.org")
        p = os.path.join(d, "ndrm.json")
        m = json.load(open(p))
        m["required_controls"] = [c for c in m["required_controls"] if c != "deletion_path"]
        json.dump(m, open(p, "w"))
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "deletion_path" in res["missing_controls"]


def test_unset_owner_fails():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="", jurisdiction="US-CA", contact="t@example.org")
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "owner" in res["unset_fields"]


def test_all_jurisdictions():
    for j in ["US-CO", "US-CA", "CL", "EU"]:
        with tempfile.TemporaryDirectory() as d:
            build_manifest(d, owner="T", jurisdiction=j, contact="t@example.org")
            res = check_manifest(d)
            assert res["jurisdiction"] == j


def test_chile_marked_pending():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="CL", contact="t@example.org")
        res = check_manifest(d)
        assert res["implementing_law_pending"] is True and res["law_status"] == "PENDING_IMPLEMENTATION"


def test_bids_json_is_canonical():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="US-CA", contact="t@example.org")
        assert os.path.exists(os.path.join(d, "ndrm.json"))
        res = check_manifest(d)
        assert any(c["check"] == "format:bids-compatible-json" and c["ok"] for c in res["checks"])


def test_legacy_yaml_flagged():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="US-CA", contact="t@example.org", fmt="yaml")
        res = check_manifest(d)
        assert res["verdict"] == "FAIL"  # legacy format fails v0.2 check
        assert any("ndrm.json" in n for n in res["notes"])


def test_consent_artifacts_required():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="US-CA", contact="t@example.org")
        res = check_manifest(d)
        ca = [c for c in res["checks"] if c["check"] == "consent_artifacts_linked"]
        assert ca and ca[0]["ok"] is False  # empty by default → flagged


def test_v02_fields_present():
    with tempfile.TemporaryDirectory() as d:
        m = build_manifest(d, owner="T", jurisdiction="EU", contact="t@example.org")
        for f in ("provenance_chain", "consent_artifacts", "cross_border_transfers",
                  "retention_schedule", "security_controls", "revocation_trail", "law_status"):
            assert f in m, f


def test_bench_synthetic_runs():
    res = run_benchmark("synthetic-kalman-cursor")
    assert res["score"] is not None and res["provenance"] == "local-synthetic"


def test_bench_reference_honest():
    res = run_benchmark("dandi-speech-wpm")
    assert res["score"] is None and res["provenance"] == "REQUIRES-EXTERNAL-DATA"


def test_bench_list_all():
    assert len(list_benchmarks()) == 5
