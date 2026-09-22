#!/usr/bin/env python3
"""neurogate CLI v0.3 — document neural-dataset use, reproduce evaluations, surface unknowns.

  neurogate init      write a deliberately INCOMPLETE draft manifest (refuses overwrite)
  neurogate check     documented-conditions check → READY_FOR_REVIEW | INCOMPLETE | BLOCKED | ERROR
  neurogate validate  schema-only structural validation
  neurogate migrate   versioned manifest update (prior file preserved, reviewable)
  neurogate bench     run benchmarks (synthetic smoke test real; planned tasks return no score)
  neurogate list-bench
  neurogate report    render the stored/last check result; optional --gate propagates decision

Exit codes: check=0 only for READY_FOR_REVIEW; BLOCKED=1, INCOMPLETE=2, ERROR=3.
bench: unknown task or failed run = nonzero. report formats stored results (no re-check)
unless --gate, which re-runs the check and propagates the decision.
"""
import argparse, json, os, sys
from . import __version__
from .ndrm import (new_manifest_draft, check_manifest, validate_schema, migrate,
                   SchemaError, SUPPORTED_SCHEMA_VERSIONS)
from .bench import list_benchmarks, run_benchmark

ASSESSMENT_EXIT = {"READY_FOR_REVIEW": 0, "INCOMPLETE": 2, "BLOCKED": 1, "ERROR": 3}


def cmd_init(args):
    try:
        org = getattr(args, "responsible_organization", None) or getattr(args, "org", "")
        p = new_manifest_draft(args.path, responsible_organization=org,
                               contact=args.contact, jurisdiction=args.jurisdiction,
                               dataset_id=args.dataset_id, classification=args.classification,
                               modality=args.modality)
        print(json.dumps({"written": os.path.join(args.path, "ndrm.json"),
                          "assessment": "INCOMPLETE (deliberate draft — fill required fields)",
                          "schema_version": p["ndrm_version"]}, indent=2))
        return 0
    except SchemaError as e:
        print(json.dumps({"error": e.reason, "rule_id": e.rule_id, "remedy": e.remedy}, indent=2))
        return 3


def cmd_validate(args):
    rec = validate_schema(args.path)
    print(json.dumps(rec, indent=2))
    return 0 if rec["schema_result"] == "SCHEMA_VALID" else 3


def cmd_check(args):
    rec = check_manifest(args.path, requested_use=args.use)
    print(json.dumps(rec, indent=2))
    return ASSESSMENT_EXIT.get(rec["assessment"], 3)


def cmd_bench(args):
    res = run_benchmark(args.benchmark, args.data)
    if "error" in res:
        print(json.dumps(res, indent=2))
        return int(res.get("exit_code", 2))
    if isinstance(res, dict) and res.get("ran"):
        bad = [k for k, v in res["ran"].items() if "error" in v]
        print(json.dumps(res, indent=2))
        return 2 if bad else 0
    print(json.dumps(res, indent=2))
    if res.get("status") == "COMPLETED_SYNTHETIC_ONLY" and res.get("held_out_r2") is not None:
        return 0
    if res.get("status") == "PLANNED":
        return 0
    return 0 if res.get("score") is not None else 1


def cmd_report(args):
    if args.gate:
        rec = check_manifest(args.path, requested_use=args.use)
        from .report import render
        print(render(rec))
        return ASSESSMENT_EXIT.get(rec["assessment"], 3)
    # formatter mode: reads stored receipt if present, else renders schema-only view
    store = os.path.join(args.path, "last_receipt.json")
    if os.path.exists(store) and not args.fresh:
        from .report import render
        print(render(json.load(open(store))))
        print("(report: formatter mode — rendering stored last_receipt.json; "
              "use --fresh or --gate to execute checks)")
        return 0
    rec = check_manifest(args.path, requested_use=args.use)
    from .report import render
    print(render(rec))
    print("(report: formatter mode executed a check to render; use --gate to propagate exit)")
    return 0


def cmd_migrate(args):
    try:
        res = migrate(args.path, to=args.to)
        print(json.dumps(res, indent=2))
        return 0
    except SchemaError as e:
        print(json.dumps({"error": e.reason, "rule_id": e.rule_id, "remedy": e.remedy}, indent=2))
        return 3


def main():
    ap = argparse.ArgumentParser(prog="neurogate", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version="neurogate 0.3.0")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="write an incomplete draft manifest (nondestructive)")
    p.add_argument("path")
    p.add_argument("--org", dest="responsible_organization", default="",
                   help="responsible organization (stored under responsibility)")
    p.add_argument("--contact", default="", help="accountable contact (e.g. privacy@lab.org)")
    p.add_argument("--jurisdiction", default="US-CA")
    p.add_argument("--dataset-id", default="")
    p.add_argument("--classification", default="human", choices=["human", "nonhuman", "synthetic"])
    p.add_argument("--modality", default="")
    p.add_argument("--force", action="store_true",
                   help="EXPLICIT replacement of an existing manifest (reviewed overwrite)")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("check", help="documented-conditions check (exit 0 only if READY_FOR_REVIEW)")
    p.add_argument("path"); p.add_argument("--use", default=None)
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("validate", help="schema-only structural validation")
    p.add_argument("path")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("migrate", help="versioned manifest update; prior file preserved")
    p.add_argument("path"); p.add_argument("--to", default="0.3")
    p.set_defaults(fn=cmd_migrate)

    p = sub.add_parser("bench", help="run a benchmark (synthetic smoke test is real; others PLANNED)")
    p.add_argument("benchmark", nargs="?", default="all"); p.add_argument("--data", default=None)
    p.set_defaults(fn=cmd_bench)

    sub.add_parser("list-bench", help="list benchmarks and their status").set_defaults(
        fn=lambda a: (print("\n".join(list_benchmarks())), 0)[1])

    p = sub.add_parser("report", help="render a report (formatter by default; --gate propagates)")
    p.add_argument("path"); p.add_argument("--gate", action="store_true"); p.add_argument("--use", default=None)
    p.add_argument("--fresh", action="store_true")
    p.set_defaults(fn=cmd_report)

    args = ap.parse_args()
    rc = args.fn(args)
    sys.exit(int(rc) if isinstance(rc, int) else 0)


if __name__ == "__main__":
    main()