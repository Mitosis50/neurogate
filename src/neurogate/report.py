"""Human-readable compliance + benchmark report."""


def render(res):
    lines = []
    lines.append("=" * 62)
    lines.append(" NEUROGATE COMPLIANCE REPORT")
    lines.append("=" * 62)
    lines.append(f" Verdict      : {res.get('verdict')}")
    lines.append(f" Jurisdiction : {res.get('jurisdiction', 'n/a')}")
    lines.append(f" Law          : {res.get('law', 'n/a')}")
    if res.get("missing_controls"):
        lines.append(f" MISSING      : {', '.join(res['missing_controls'])}")
    if res.get("unset_fields"):
        lines.append(f" UNSET FIELDS : {', '.join(res['unset_fields'])}")
    for c in res.get("checks", []):
        lines.append(f"  [{'PASS' if c['ok'] else 'FAIL'}] {c['check']}")
    lines.append("=" * 62)
    return "\n".join(lines)
