"""Human-readable report renderer for NeuroGate v0.3 receipts."""


def render(rec):
    lines = []
    lines.append("=" * 66)
    lines.append(" NEUROGATE DOCUMENTED-CONDITIONS REPORT (receipt v{})".format(rec.get("receipt_version", "?")))
    lines.append("=" * 66)
    lines.append(f" dataset        : {rec.get('dataset_id') or '(unset)'}")
    lines.append(f" schema result  : {rec.get('schema_result')}")
    lines.append(f" assessment     : {rec.get('assessment')}")
    lines.append(f" requested use  : {rec.get('requested_use') or '(undocumented)'}")
    lines.append(f" evidence state : {rec.get('evidence_status')}")
    bench = rec.get("benchmark") or {}
    lines.append(f" benchmark      : {bench.get('status')} (score={bench.get('score')})")
    lines.append(f" legal compliance determined by this tool: {rec.get('legal_compliance_determined')}")
    lines.append("-" * 66)
    for f in rec.get("findings", []):
        lines.append(f"  [{f['result']:^7}] ({f['severity']}) {f['rule_id']}")
        lines.append(f"            evidence: {f['evidence_status']}  remedy: {f['remedy'][:90]}")
    if not rec.get("findings"):
        lines.append("  (no findings)")
    lines.append("-" * 66)
    lines.append(" " + rec.get("note", ""))
    lines.append("=" * 66)
    return "\n".join(lines)