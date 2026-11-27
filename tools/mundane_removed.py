"""Write data/mundane/REMOVED.md: every record the Research databases leave out (server/mundane_data.py dropped()) and why.

Re-runnable: .venv/bin/python -m tools.mundane_removed
"""
from __future__ import annotations


from server import mundane_data as MD

OUT = MD.DIR / "REMOVED.md"


def main() -> None:
    lines, rows = ["# Records left out of the Research databases", "",
                   "Only events whose time is recorded exactly (to the minute, not reported or announced), with their date and place, are kept; a swearing-in also keeps a reported or approximate ceremony time. The rule is `dropped()` in server/mundane_data.py;",
                   "the source files are untouched, so a record comes back once its missing time is filled in.", "",
                   "| Set | Kept | Removed | Reasons |", "|---|---:|---:|---|"], []
    for name in MD.SETS:
        raw, d = MD.raw_dataset(name), MD.dataset(name)
        reasons = ", ".join(f"{k} {v:,}" for k, v in sorted(d["removed"].items(), key=lambda kv: -kv[1]))
        lines.append(f"| {name} | {len(d['records']):,} | {sum(d['removed'].values()):,} | {reasons} |")
        moments = MD.quake_moments(raw)
        for r in raw:
            why = MD.dropped(r, moments)
            if why:
                title = r.get("name") or r.get("chart_name") or r.get("election") or (f"{r.get('team_a')} v {r.get('team_b')}" if r.get("team_a") else "") or r.get("place") or ""
                rows.append(f"| {r['id']} | {name} | {r['date']} | {str(title).replace('|', '/')} | {why} |")
    lines += ["", "## Every removed record", "", "| Id | Set | Date | Event | Reason |", "|---|---|---|---|---|", *rows, ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT}: {len(rows):,} removed")


if __name__ == "__main__":
    main()
