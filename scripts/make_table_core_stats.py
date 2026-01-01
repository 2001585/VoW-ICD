#!/usr/bin/env python3
"""
Build a compact SVG table of core stats (mean±SD) per variant
from run_summary.csv.

Columns: Variant | cooperation_rate | average_recovery_time | post_shock_trust

Usage:
  python3 scripts/make_table_core_stats.py \
    --csv results/vow-cultural-drift/run_summary.csv \
    --out papers/vow-shock-study/figures/table2_core_stats.svg
"""
from __future__ import annotations
import argparse, csv, statistics as stats

ORDER = ["soft", "baseline", "double", "extended"]
LABEL = {"soft":"Soft","baseline":"Baseline","double":"Double","extended":"Extended"}

def read_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r = {k.strip().lower(): (v.strip() if isinstance(v,str) else v) for k,v in row.items()}
            var = (r.get("variant") or r.get("condition") or "").lower()
            if "soft" in var: var = "soft"
            elif "double" in var: var = "double"
            elif "extend" in var: var = "extended"
            elif "base" in var or "single" in var: var = "baseline"
            def num(k):
                v = r.get(k)
                if not v: return None
                try:
                    return float(v.replace('%',''))/100.0 if '%' in v else float(v)
                except Exception:
                    return None
            rows.append({
                "variant": var,
                "cooperation_rate": num("cooperation_rate"),
                "average_recovery_time": num("average_recovery_time"),
                "post_shock_trust": num("post_shock_trust"),
            })
    return rows

def agg(rows, key):
    vals = {}
    for v in ORDER:
        xs = [r[key] for r in rows if r["variant"]==v and r[key] is not None]
        if xs:
            m = stats.mean(xs)
            sd = stats.pstdev(xs) if len(xs)>1 else 0.0
            vals[v] = (m, sd, len(xs))
    return vals

def fmt(m, sd):
    # Rates with 3 decimals, times with 2 decimals (heuristic)
    return f"{m:.3f}±{sd:.3f}" if m<=1.0 else f"{m:.2f}±{sd:.2f}"

def build_svg(rows):
    coop = agg(rows, "cooperation_rate")
    rec = agg(rows, "average_recovery_time")
    trust = agg(rows, "post_shock_trust")
    # layout
    W, H = 900, 200
    col_w = [180, 220, 240, 260]
    x = [0]
    for w in col_w[:-1]:
        x.append(x[-1]+w)
    # header + 4 rows
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    svg.append('<style>.h{font:700 18px Arial}.c{font:16px Arial}.grid{stroke:#000;fill:#fff}.head{fill:#e9e9e9}</style>')
    # headers
    headers = ["Variant","cooperation_rate (mean±SD)","average_recovery_time (mean±SD)","post_shock_trust (mean±SD)"]
    y=0
    for i,w in enumerate(col_w):
        svg.append(f'<rect x="{x[i]}" y="{y}" width="{w}" height="40" class="grid head"/>')
        svg.append(f'<text x="{x[i]+w/2}" y="26" text-anchor="middle" class="h">{headers[i]}</text>')
    # rows
    y=40
    row_h=36
    for v in ORDER:
        svg.append(f'<rect x="0" y="{y}" width="{col_w[0]}" height="{row_h}" class="grid"/>')
        svg.append(f'<rect x="{x[1]}" y="{y}" width="{col_w[1]}" height="{row_h}" class="grid"/>')
        svg.append(f'<rect x="{x[2]}" y="{y}" width="{col_w[2]}" height="{row_h}" class="grid"/>')
        svg.append(f'<rect x="{x[3]}" y="{y}" width="{col_w[3]}" height="{row_h}" class="grid"/>')
        svg.append(f'<text x="{col_w[0]/2}" y="{y+24}" text-anchor="middle" class="c">{LABEL[v]}</text>')
        if v in coop:
            svg.append(f'<text x="{x[1]+col_w[1]/2}" y="{y+24}" text-anchor="middle" class="c">{fmt(*coop[v][:2])}</text>')
        if v in rec:
            svg.append(f'<text x="{x[2]+col_w[2]/2}" y="{y+24}" text-anchor="middle" class="c">{fmt(*rec[v][:2])}</text>')
        if v in trust:
            svg.append(f'<text x="{x[3]+col_w[3]/2}" y="{y+24}" text-anchor="middle" class="c">{fmt(*trust[v][:2])}</text>')
        y+=row_h
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = read_rows(args.csv)
    svg = build_svg(rows)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved:", args.out)

if __name__ == "__main__":
    main()

