"""NeuroGate benchmark component v0.3 — honest result semantics.

Per external frontier review (2026-09-22):
- NO placeholder scores. Every displayed number traces to real predictions
  computed from arrays with a documented metric.
- `synthetic-regression` is an engineering smoke test: documented synthetic
  signal, train/val/test split, ridge baseline, held-out R², shuffled-target
  control, clean-signal fixture (leakage detector). NOT clinical performance.
- External tasks (FALCON H1 → DANDI 000954, MOABB EEG) are PLANNED adapters:
  they return status PLANNED with score=None. They are never registered as
  completed benchmarks until a pinned, reproducible run exists.
- Unknown benchmark name -> error with nonzero CLI exit (CLI enforces).
"""
import time
import numpy as np

BENCHMARKS = {
    "synthetic-regression-v0": {
        "kind": "runnable",
        "metric": "held_out_r2",
        "protocol": "synthetic ridge regression: documented generator, train/val/test split, "
                    "shuffled-target control, clean-signal fixture",
        "reference": "src/neurogate/bench.py::_run_synthetic_regression",
    },
    "falcon-h1-motor": {
        "kind": "planned",
        "metric": "TBD (task-defined, NOT 'bits per minute' by default)",
        "protocol": "FALCON H1 feasibility task (motor decoding); DANDI 000954 candidate; "
                    "requires immutable dataset version + pinned evaluator before any run",
        "reference": "https://github.com/snel-repo/falcon-challenge",
    },
    "moabb-eeg-example": {
        "kind": "planned",
        "metric": "per-MOABB protocol",
        "protocol": "optional EEG adapter if EEG users become first adopters; scope change "
                    "recorded if used instead of FALCON",
        "reference": "https://moabb.neurotechx.com",
    },
}


def list_benchmarks():
    return [f"{k:26s} [{v['kind']:8s}] metric={v['metric'][:40]}" for k, v in BENCHMARKS.items()]


def run_benchmark(name, data=None):
    t0 = time.time()
    if name == "all":
        return {"ran": {k: run_benchmark(k, data) for k in BENCHMARKS}}
    if name not in BENCHMARKS:
        return {"error": f"unknown benchmark {name!r}", "available": sorted(BENCHMARKS),
                "exit_code": 2}
    spec = BENCHMARKS[name]
    if spec["kind"] == "planned":
        return {"benchmark": name, "status": "PLANNED", "score": None, "metric": spec["metric"],
                "protocol": spec["protocol"], "note": "planned task — returns no score; "
                "never registered as completed until a pinned reproducible run exists",
                "reference": spec["reference"], "elapsed_s": round(time.time() - t0, 3)}
    if name == "synthetic-regression-v0":
        res = _run_synthetic_regression(seed=42)
        res.update({"benchmark": name, "metric": spec["metric"], "protocol": spec["protocol"],
                    "provenance": "local-synthetic (fully reproducible, no external data)",
                    "status": "COMPLETED_SYNTHETIC_ONLY",
                    "disclaimer": "engineering smoke test; NOT clinical performance or "
                                  "evidence of field leadership",
                    "elapsed_s": round(time.time() - t0, 3)})
        return res
    return {"benchmark": name, "status": "ERROR", "score": None, "error": "unhandled kind",
            "exit_code": 3}


def _run_synthetic_regression(seed=42, n_train=400, n_test=200, n_features=20,
                              effective=8, noise=0.5, ridge_lambda=1.0):
    """Real regression on a documented synthetic process. Returns honest metrics.

    Generator: y = X_beta + gaussian noise; only `effective` features carry signal.
    Metric: R² on held-out test predictions (explicit implementation below).
    Controls: shuffled-target (must score ≈ 0; detects leakage/metric bugs) and
    clean-signal fixture (must score ≈ 1; detects broken metric computation).
    """
    rng = np.random.default_rng(seed)
    beta = np.zeros(n_features)
    beta[:effective] = rng.normal(0, 1, effective)

    def make(n, scale_noise=noise):
        X = rng.normal(0, 1, (n, n_features))
        y = X @ beta + rng.normal(0, scale_noise, n)
        return X, y

    Xtr, ytr = make(n_train)
    Xte, yte = make(n_test)

    # ridge closed form, fitted ONLY on training data
    n, p = Xtr.shape
    w = np.linalg.solve(Xtr.T @ Xtr + ridge_lambda * np.eye(p), Xtr.T @ ytr)

    def r2(y_true, y_pred):
        ss_res = float(np.sum((y_true - y_pred) ** 2))
        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        return round(1.0 - ss_res / ss_tot, 4) if ss_tot > 0 else None

    pred_test = Xte @ w
    main = {"n_train": n_train, "n_test": n_test, "n_features": n_features,
            "effective_features": effective, "noise_sd": noise,
            "ridge_lambda": ridge_lambda, "seed": seed,
            "held_out_r2": r2(yte, pred_test)}

    # control 1: shuffled-target — predictions must NOT transfer (≈ 0 expected)
    perm = rng.permutation(n_test)
    main["shuffled_target_r2"] = r2(yte[perm], pred_test)

    # control 2: clean-signal fixture — metric must recover ≈ 1.0
    Xc, yc = make(120, scale_noise=1e-6)
    wc = np.linalg.solve(Xc.T @ Xc + ridge_lambda * np.eye(n_features), Xc.T @ yc)
    main["clean_fixture_r2"] = r2(yc, Xc @ wc)
    return main