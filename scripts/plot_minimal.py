#!/usr/bin/env python3
"""
Generate minimal, publication-ready SVG figures for VOW-ICD results
without external plotting libraries.

Inputs
  --csv <path>   : run_summary.csv containing columns
                   variant, cooperation_rate, average_recovery_time,
                   post_shock_trust, message_action_mismatch
  --out <dir>    : output directory for SVGs

Outputs
  fig3_bars.svg      : 1x2 bar chart with mean±SD for cooperation_rate and
                        average_recovery_time per variant
  fig4_mismatch_box.svg : box plot per variant for message_action_mismatch

Usage
  python3 scripts/plot_minimal.py \
    --csv results/vow-cultural-drift/run_summary.csv \
    --out papers/vow-shock-study/figures

No third-party packages required (uses csv & math only).
"""

from __future__ import annotations
import argparse, csv, math, os, statistics as stats
from collections import defaultdict


ORDER = ["soft", "baseline", "double", "extended"]
LABELS = {
    "soft": "Soft",
    "baseline": "Baseline",
    "double": "Double",
    "extended": "Extended",
}


def read_summary(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            # normalize keys
            r = {k.strip().lower(): v for k, v in row.items()}
            # robust variant normalization
            vraw = (r.get("variant") or r.get("condition") or "").strip().lower()
            if "soft" in vraw:
                variant = "soft"
            elif "double" in vraw:
                variant = "double"
            elif "extend" in vraw:
                variant = "extended"
            elif "base" in vraw or "single" in vraw:
                variant = "baseline"
            else:
                variant = vraw or f"row{i}"

            def parse_float(key: str):
                val = r.get(key) or r.get(key.replace("_", ""))
                if val is None or val == "":
                    return None
                try:
                    return float(val)
                except Exception:
                    try:
                        return float(val.replace("%", "")) / (
                            100.0 if "%" in val else 1.0
                        )
                    except Exception:
                        return None

            rows.append(
                {
                    "variant": variant,
                    "cooperation_rate": parse_float("cooperation_rate"),
                    "average_recovery_time": parse_float("average_recovery_time"),
                    "post_shock_trust": parse_float("post_shock_trust"),
                    "message_action_mismatch": parse_float(
                        "message_action_mismatch"
                    ),
                }
            )
    return rows


def group_stats(rows, key):
    data = defaultdict(list)
    for r in rows:
        v = r["variant"]
        x = r.get(key)
        if x is not None:
            data[v].append(x)
    out = {}
    for v, xs in data.items():
        if not xs:
            continue
        m = stats.mean(xs)
        sd = stats.pstdev(xs) if len(xs) > 1 else 0.0
        out[v] = {"mean": m, "sd": sd, "n": len(xs), "values": xs}
    return out


def scale(value, vmin, vmax, px_min, px_max):
    if vmax == vmin:
        return (px_min + px_max) / 2
    return px_min + (value - vmin) * (px_max - px_min) / (vmax - vmin)


def save_fig3_bars(path_out, rows):
    # Compute stats
    s_coop = group_stats(rows, "cooperation_rate")
    s_rec = group_stats(rows, "average_recovery_time")

    W, H = 1000, 360
    margin = 40
    panel_gap = 40
    panel_w = (W - 2 * margin - panel_gap) // 2
    panel_h = H - 2 * margin
    bar_w = 40
    bar_gap = 35

    # Y scales
    def y_range(stats_dict):
        vals = [d["mean"] + d["sd"] for d in stats_dict.values()]
        vals += [d["mean"] - d["sd"] for d in stats_dict.values()]
        if not vals:
            return 0, 1
        vmin = max(0.0, min(vals) * 0.95)
        vmax = max(vals) * 1.05
        return vmin, vmax

    y1_min, y1_max = y_range(s_coop)
    y2_min, y2_max = y_range(s_rec)

    def panel_svg(x0, y0, title, stats_dict, y_min, y_max, fmt):
        svg = []
        # axes
        svg.append(
            f'<rect x="{x0}" y="{y0}" width="{panel_w}" height="{panel_h}" fill="#fff" stroke="#000" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{x0 + panel_w/2}" y="{y0 - 10}" text-anchor="middle" font-family="Arial" font-size="18">{title}</text>'
        )
        # bars
        for i, v in enumerate(ORDER):
            d = stats_dict.get(v)
            if not d:
                continue
            bx = x0 + 60 + i * (bar_w + bar_gap)
            by = y0 + panel_h
            hval = scale(d["mean"], y_min, y_max, 0, panel_h)
            hsd = scale(d["sd"], 0, (y_max - y_min), 0, panel_h)  # approximate
            bar_h = hval
            # draw bar from bottom up
            svg.append(
                f'<rect x="{bx}" y="{by - bar_h}" width="{bar_w}" height="{bar_h}" fill="#d9d9d9" stroke="#000"/>'
            )
            # error bar (mean±sd)
            err_y1 = by - (scale(d["mean"] + d["sd"], y_min, y_max, 0, panel_h))
            err_y2 = by - (scale(d["mean"] - d["sd"], y_min, y_max, 0, panel_h))
            cx = bx + bar_w / 2
            svg.append(
                f'<line x1="{cx}" y1="{err_y1}" x2="{cx}" y2="{err_y2}" stroke="#000" stroke-width="2"/>'
            )
            svg.append(
                f'<line x1="{cx-8}" y1="{err_y1}" x2="{cx+8}" y2="{err_y1}" stroke="#000" stroke-width="2"/>'
            )
            svg.append(
                f'<line x1="{cx-8}" y1="{err_y2}" x2="{cx+8}" y2="{err_y2}" stroke="#000" stroke-width="2"/>'
            )
            # labels
            svg.append(
                f'<text x="{bx + bar_w/2}" y="{by + 18}" text-anchor="middle" font-family="Arial" font-size="14">{LABELS.get(v,v)}</text>'
            )
            svg.append(
                f'<text x="{bx + bar_w/2}" y="{by - bar_h - 8}" text-anchor="middle" font-family="Arial" font-size="12">{fmt(d["mean"])}</text>'
            )
        return "\n".join(svg)

    def fmt_rate(x):
        return f"{x:.3f}"

    def fmt_time(x):
        return f"{x:.2f} turns"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        panel_svg(margin, margin, "Cooperation Rate (mean±SD)", s_coop, y1_min, y1_max, fmt_rate),
        panel_svg(margin + panel_w + panel_gap, margin, "Average Recovery Time (mean±SD)", s_rec, y2_min, y2_max, fmt_time),
        "</svg>",
    ]
    with open(os.path.join(path_out, "fig3_bars.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def save_fig4_box(path_out, rows):
    # Prepare data per variant
    data = defaultdict(list)
    for r in rows:
        v = r["variant"]
        x = r.get("message_action_mismatch")
        if x is not None:
            data[v].append(x)
    total_n = sum(len(xs) for xs in data.values())
    # If we have insufficient samples for boxplot, fall back to mean±SD bars
    if total_n < 4:  # fewer than a quartile-friendly sample
        stats_dict = group_stats(rows, "message_action_mismatch")
        # Build a single‑panel bar chart
        W, H = 700, 320
        margin = 40
        plot_w = W - 2 * margin
        plot_h = H - 2 * margin
        bar_w = 40
        gap = 35
        vals = [d["mean"] + d["sd"] for d in stats_dict.values()] or [0, 1]
        vmin = 0.0
        vmax = max(vals) * 1.1
        def ypx(y):
            return margin + plot_h - (y - vmin) * plot_h / (vmax - vmin if vmax!=vmin else 1)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
        parts.append('<text x="350" y="24" text-anchor="middle" font-family="Arial" font-size="18">Message–Action Mismatch (mean±SD)</text>')
        parts.append(f'<rect x="{margin}" y="{margin}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="#000"/>')
        for i, v in enumerate(ORDER):
            d = stats_dict.get(v)
            if not d:
                continue
            bx = margin + 60 + i * (bar_w + gap)
            by = margin + plot_h
            h = (d["mean"]) * plot_h / (vmax - vmin if vmax!=vmin else 1)
            parts.append(f'<rect x="{bx}" y="{by-h}" width="{bar_w}" height="{h}" fill="#d9d9d9" stroke="#000"/>')
            # error bars
            m = d["mean"]; sd = d["sd"]; cx = bx + bar_w/2
            parts.append(f'<line x1="{cx}" y1="{ypx(m+sd)}" x2="{cx}" y2="{ypx(m-sd)}" stroke="#000" stroke-width="2"/>')
            parts.append(f'<line x1="{cx-8}" y1="{ypx(m+sd)}" x2="{cx+8}" y2="{ypx(m+sd)}" stroke="#000" stroke-width="2"/>')
            parts.append(f'<line x1="{cx-8}" y1="{ypx(m-sd)}" x2="{cx+8}" y2="{ypx(m-sd)}" stroke="#000" stroke-width="2"/>')
            parts.append(f'<text x="{bx + bar_w/2}" y="{by + 18}" text-anchor="middle" font-family="Arial" font-size="14">{LABELS.get(v,v)}</text>')
        parts.append('</svg>')
        with open(os.path.join(path_out, "fig4_mismatch_box.svg"), "w", encoding="utf-8") as f:
            f.write("\n".join(parts))
        return

    # Else draw boxplot
    W, H = 800, 360
    margin = 50
    plot_w = W - 2 * margin
    plot_h = H - 2 * margin
    vals = [x for xs in data.values() for x in xs] or [0, 1]
    y_min = min(vals) * 0.95
    y_max = max(vals) * 1.05 if max(vals) > 0 else 1.0
    def y_to_px(y):
        return margin + plot_h - (y - y_min) * plot_h / (y_max - y_min if y_max != y_min else 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    parts.append(f'<text x="{W/2}" y="{margin-15}" text-anchor="middle" font-family="Arial" font-size="18">Message–Action Mismatch by Condition</text>')
    parts.append(f'<rect x="{margin}" y="{margin}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="#000"/>')
    box_w = 40
    gap = (plot_w - len(ORDER) * box_w) / (len(ORDER) + 1)
    for i, v in enumerate(ORDER):
        xs = sorted(data.get(v, []))
        if not xs:
            continue
        q1 = stats.quantiles(xs, n=4)[0]
        med = stats.median(xs)
        q3 = stats.quantiles(xs, n=4)[-1]
        iqr = q3 - q1
        lo = max(min(xs), q1 - 1.5 * iqr)
        hi = min(max(xs), q3 + 1.5 * iqr)
        x0 = margin + gap + i * (box_w + gap)
        parts.append(f'<rect x="{x0}" y="{y_to_px(q3)}" width="{box_w}" height="{y_to_px(q1) - y_to_px(q3)}" fill="#e9e9e9" stroke="#000"/>')
        parts.append(f'<line x1="{x0}" y1="{y_to_px(med)}" x2="{x0 + box_w}" y2="{y_to_px(med)}" stroke="#000" stroke-width="2"/>')
        cx = x0 + box_w / 2
        parts.append(f'<line x1="{cx}" y1="{y_to_px(hi)}" x2="{cx}" y2="{y_to_px(q3)}" stroke="#000"/>')
        parts.append(f'<line x1="{cx}" y1="{y_to_px(q1)}" x2="{cx}" y2="{y_to_px(lo)}" stroke="#000"/>' )
        parts.append(f'<line x1="{cx-8}" y1="{y_to_px(hi)}" x2="{cx+8}" y2="{y_to_px(hi)}" stroke="#000"/>' )
        parts.append(f'<line x1="{cx-8}" y1="{y_to_px(lo)}" x2="{cx+8}" y2="{y_to_px(lo)}" stroke="#000"/>' )
        parts.append(f'<text x="{x0 + box_w/2}" y="{margin + plot_h + 18}" text-anchor="middle" font-family="Arial" font-size="14">{LABELS.get(v,v)}</text>')
    parts.append("</svg>")
    with open(os.path.join(path_out, "fig4_mismatch_box.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = read_summary(args.csv)
    if not rows:
        raise SystemExit("No rows found in CSV. Check input path or headers.")
    save_fig3_bars(args.out, rows)
    save_fig4_box(args.out, rows)
    print("Saved:")
    print(" -", os.path.join(args.out, "fig3_bars.svg"))
    print(" -", os.path.join(args.out, "fig4_mismatch_box.svg"))


if __name__ == "__main__":
    main()
