#!/usr/bin/env python3
"""neurogate CLI — one command to first value.

  neurogate init      create a neurodata-rights manifest (NDRM) for your dataset
  neurogate check     audit a dataset/pipeline against neural-data laws (CO/CA/Chile)
  neurogate bench     run the open decoder benchmark suite
  neurogate report    emit a human-readable compliance + benchmark report
"""
import argparse, json, os, sys, time
from . import __version__
from .ndrm import build_manifest, check_manifest
from .bench import list_benchmarks, run_benchmark


def cmd_init(args):
    p = build_manifest(args.path, owner=args.owner, jurisdiction=args.jurisdiction)
    print(json.dumps(p, indent=2))
    print(f"\nNDRM written to {args.path}/ndrm.yaml — commit it next to your data.")


def cmd_check(args):
    res = check_manifest(args.path)
    ok = res["verdict"] == "PASS"
    print(json.dumps(res, indent=2))
    sys.exit(0 if ok else 1)


def cmd_bench(args):
    if args.list:
        print("\n".join(list_benchmarks()))
        return
    res = run_benchmark(args.benchmark, args.data)
    print(json.dumps(res, indent=2))


def cmd_report(args):
    res = check_manifest(args.path)
    from .report import render
    print(render(res))


def main():
    ap = argparse.ArgumentParser(prog="neurogate", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"neurogate {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="create a neurodata-rights manifest")
    p.add_argument("path"); p.add_argument("--owner", default=""); p.add_argument("--jurisdiction", default="US-CA")
    p.set_defaults(fn=cmd_init)
    p = sub.add_parser("check", help="audit dataset against NDRM + law pack")
    p.add_argument("path"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("bench", help="run open decoder benchmarks")
    p.add_argument("benchmark", nargs="?", default="all"); p.add_argument("--data")
    p.set_defaults(fn=cmd_bench)
    p.add_parser("list-bench", help="list available benchmarks").set_defaults(fn=lambda a: print("\n".join(list_benchmarks())))
    p = sub.add_parser("report", help="human-readable compliance report")
    p.add_argument("path"); p.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
