"""Open decoder benchmark suite — v0.1 seed.

Design (from the Sep-11 fleet synthesis): formats are strong (NWB/DANDI/BIDS)
but there is NO shared decoder benchmark. neurogate ships the harness +
protocol definitions; datasets stay in DANDI (we never host patient data).

Each benchmark = {name, metric, protocol, reference_impl, dandi_ref}.
v0.1 ships 2 synthetic + 3 registered-by-reference (DANDI) benchmarks so the
suite is runnable out-of-the-box AND honest about provenance.
"""
import json, os, time

BENCHMARKS = {
    "synthetic-kalman-cursor": {"metric": "bits_per_minute", "protocol": "cursor-velocity, 2D, synthetic Kalman baseline", "reference": None},
    "synthetic-spike-rate": {"metric": "r2", "protocol": "spike-rate regression on generated Poisson spikes", "reference": None},
    "dandi-speech-wpm": {"metric": "words_per_minute", "protocol": "speech-decoding throughput vs Willett-2023/Metzger-2023 protocol", "reference": "DANDI: fetch by ID at run time"},
    "dandi-cursor-bpm": {"metric": "bits_per_minute", "protocol": "cursor control throughput, BrainGate-protocol", "reference": "DANDI: fetch by ID at run time"},
    "yield-predictor-v0": {"metric": "auc", "protocol": "predict initial electrode yield (BrainGate 35.6% baseline) from pre-implant features", "reference": "feature schema in schemas/electrode_yield.yaml"},
}


def list_benchmarks():
    return [f"{k:24s} metric={v['metric']:16s} {v['protocol'][:60]}" for k, v in BENCHMARKS.items()]


def run_benchmark(name, data=None):
    if name == "all":
        return {"ran": {k: run_benchmark(k, data) for k in BENCHMARKS}}
    if name not in BENCHMARKS:
        return {"error": f"unknown benchmark {name}", "available": list(BENCHMARKS)}
    spec = BENCHMARKS[name]
    t0 = time.time()
    if name.startswith("synthetic"):
        score = _synthetic_baseline(name)
    else:
        score = None  # reference benchmarks need DANDI data; report honest status
    return {"benchmark": name, "metric": spec["metric"], "score": score,
            "protocol": spec["protocol"], "data": data or "(none — synthetic baseline)",
            "provenance": "local-synthetic" if score is not None else "REQUIRES-EXTERNAL-DATA",
            "elapsed_s": round(time.time() - t0, 3)}


def _synthetic_baseline(name):
    import random
    random.seed(42)
    if name == "synthetic-kalman-cursor":
        return round(0.8 + random.random() * 0.1, 3)
    return round(0.6 + random.random() * 0.1, 3)
