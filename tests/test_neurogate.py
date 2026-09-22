import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from neurogate.ndrm import build_manifest, check_manifest
from neurogate.bench import run_benchmark, list_benchmarks
import tempfile, yaml


def test_init_and_check_pass():
    with tempfile.TemporaryDirectory() as d:
        m = build_manifest(d, owner="Test Owner", jurisdiction="US-CA", contact="t@example.org")
        assert os.path.exists(os.path.join(d, "ndrm.yaml"))
        res = check_manifest(d)
        assert res["verdict"] == "PASS", res


def test_check_missing_manifest():
    with tempfile.TemporaryDirectory() as d:
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "no ndrm.yaml" in res["reason"]


def test_missing_control_fails():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="T", jurisdiction="US-CA")
        # strip a required control
        p = os.path.join(d, "ndrm.yaml")
        m = yaml.safe_load(open(p))
        m["required_controls"] = [c for c in m["required_controls"] if c != "deletion_path"]
        yaml.safe_dump(m, open(p, "w"))
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "deletion_path" in res["missing_controls"]


def test_unset_owner_fails():
    with tempfile.TemporaryDirectory() as d:
        build_manifest(d, owner="", jurisdiction="US-CA")
        res = check_manifest(d)
        assert res["verdict"] == "FAIL" and "owner" in res["unset_fields"]


def test_all_jurisdictions():
    for j in ["US-CO", "US-CA", "CL", "EU"]:
        with tempfile.TemporaryDirectory() as d:
            build_manifest(d, owner="T", jurisdiction=j, contact="t@example.org")
            assert check_manifest(d)["verdict"] == "PASS"


def test_bench_synthetic_runs():
    res = run_benchmark("synthetic-kalman-cursor")
    assert res["score"] is not None and res["provenance"] == "local-synthetic"


def test_bench_reference_honest():
    res = run_benchmark("dandi-speech-wpm")
    assert res["score"] is None and res["provenance"] == "REQUIRES-EXTERNAL-DATA"


def test_bench_list_all():
    assert len(list_benchmarks()) == 5
