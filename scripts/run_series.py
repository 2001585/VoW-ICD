"""Batch runner for repeated Village of Words experiments.

Example usage:

```bash
python3 scripts/run_series.py \
    --config experiments/vow-cultural-drift/config.yaml \
    --variant double-wave \
    --runs 3 \
    --tag double_shock
```
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from scripts.archive_latest import archive as archive_outputs
from src.utils.config import resolve_path


@dataclass
class RunSummary:
    timestamp: str
    variant: str
    run_index: int
    seed: int
    log_path: Path
    metrics_path: Path
    cooperation_rate: float
    average_recovery_time: float | None
    mismatch_rate: float
    pre_coop: float | None
    shock_coop: float | None
    post_coop: float | None
    post_coop_extended: float | None
    pre_trust: float | None
    shock_trust: float | None
    post_trust: float | None
    unknown_rate: float


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def save_config(data: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def _resolve_variant(config: Dict[str, Any], variant_id: str) -> Dict[str, Any]:
    variants: Iterable[Dict[str, Any]] = config.get("shock_variants", []) or []
    for variant in variants:
        if str(variant.get("id")) == variant_id:
            return variant
    available = ", ".join(str(v.get("id")) for v in variants) or "<none>"
    raise ValueError(f"Variant '{variant_id}' not found. Available: {available}")


def _prepare_phases(original_phases: List[Dict[str, Any]], variant: Dict[str, Any]) -> List[Dict[str, Any]]:
    phases_before: List[Dict[str, Any]] = []
    phases_after: List[Dict[str, Any]] = []
    shock_templates: List[Dict[str, Any]] = []

    encountered_shock = False
    for phase in original_phases:
        name = str(phase.get("name", ""))
        if name.startswith("shock"):
            shock_templates.append(phase)
            encountered_shock = True
            continue
        if not encountered_shock:
            phases_before.append(phase)
        else:
            phases_after.append(phase)

    if not shock_templates:
        raise ValueError("No shock phase found in scenario.phases to override.")

    template = shock_templates[0]
    schedule: List[Dict[str, Any]] = variant.get("schedule", [])
    if not schedule:
        raise ValueError(f"Variant '{variant.get('id')}' does not define a schedule.")

    target = variant.get("target", template.get("parameters", {}).get("target", "all"))
    exclude = variant.get("exclude", template.get("parameters", {}).get("exclude", []))

    new_shock_phases: List[Dict[str, Any]] = []
    multiple = len(schedule) > 1

    for idx, item in enumerate(schedule, start=1):
        turns: List[int] = list(item.get("turns", []))
        if not turns:
            raise ValueError("Each schedule entry must define 'turns'.")
        start = min(turns)
        end = max(turns)
        delta = item.get("delta", {})

        phase_copy = copy.deepcopy(template)
        phase_name = template.get("name", "shock")
        if multiple:
            suffix = ["primary", "secondary", "tertiary"][idx - 1] if idx <= 3 else f"block{idx}"
            phase_name = f"shock_{suffix}"
        phase_copy["name"] = phase_name
        phase_copy["turns"] = [start, end]
        phase_copy["event"] = template.get("event", "resource_drop")
        parameters = dict(template.get("parameters", {}))
        parameters.update({
            "target": target,
            "exclude": exclude,
            "delta": delta,
        })
        phase_copy["parameters"] = parameters
        phase_copy.pop("constraints", None)  # shock phase seldom uses constraints
        new_shock_phases.append(phase_copy)

    combined = phases_before + new_shock_phases + phases_after
    combined.sort(key=lambda p: int(p.get("turns", [0])[0]))
    return combined


def _count_unknown(log_path: Path) -> tuple[int, int]:
    total = 0
    unknown = 0
    with log_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            total += 1
            data = json.loads(line)
            if str(data.get("decision", "")).upper() == "UNKNOWN":
                unknown += 1
    return total, unknown


def _run_subprocess(cmd: List[str], *, cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command {' '.join(cmd)} failed with exit code {result.returncode}")


def _append_summary(summary_csv: Path, row: RunSummary) -> None:
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    exists = summary_csv.exists()
    with summary_csv.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not exists:
            writer.writerow(
                [
                    "timestamp",
                    "variant",
                    "run_index",
                    "seed",
                    "cooperation_rate",
                    "average_recovery_time",
                    "mismatch_rate",
                    "pre_coop",
                    "shock_coop",
                    "post_coop",
                    "post_coop_extended",
                    "pre_trust",
                    "shock_trust",
                    "post_trust",
                    "unknown_rate",
                    "log_path",
                    "metrics_path",
                ]
            )
        writer.writerow(
            [
                row.timestamp,
                row.variant,
                row.run_index,
                row.seed,
                f"{row.cooperation_rate:.4f}",
                f"{row.average_recovery_time:.4f}" if row.average_recovery_time is not None else "",
                f"{row.mismatch_rate:.4f}",
                f"{row.pre_coop:.4f}" if row.pre_coop is not None else "",
                f"{row.shock_coop:.4f}" if row.shock_coop is not None else "",
                f"{row.post_coop:.4f}" if row.post_coop is not None else "",
                f"{row.post_coop_extended:.4f}" if row.post_coop_extended is not None else "",
                f"{row.pre_trust:.4f}" if row.pre_trust is not None else "",
                f"{row.shock_trust:.4f}" if row.shock_trust is not None else "",
                f"{row.post_trust:.4f}" if row.post_trust is not None else "",
                f"{row.unknown_rate:.4f}",
                row.log_path,
                row.metrics_path,
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated VoW experiments with shock variants")
    parser.add_argument("--config", required=True, help="Path to experiment config YAML")
    parser.add_argument("--variant", required=True, help="shock_variants id to apply")
    parser.add_argument("--runs", type=int, default=1, help="Number of repetitions")
    parser.add_argument("--seed-offset", type=int, default=0, help="Seed offset per run (added to base seed + index)")
    parser.add_argument("--tag", default=None, help="Optional label to prefix archived runs")
    parser.add_argument("--python", default=str(Path('.venv/bin/python')), help="Python interpreter to invoke for CLI calls")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    repo_root = config_path.resolve().parents[2]
    config_data = load_config(config_path)
    variant = _resolve_variant(config_data, args.variant)

    scenario = config_data.get("scenario", {})
    phases = scenario.get("phases")
    if not isinstance(phases, list):
        raise ValueError("scenario.phases must be a list")

    new_phases = _prepare_phases(phases, variant)
    variant_label = str(variant.get("label") or variant.get("id") or args.variant)
    if args.tag:
        variant_label = f"{variant_label} ({args.tag})"

    experiment_cfg = config_data.get("experiment", {})
    base_seed = int(experiment_cfg.get("seed", 0))

    log_path = resolve_path(config_path.parent, experiment_cfg.get("log_path", "results/events.jsonl"))
    metrics_path = resolve_path(config_path.parent, experiment_cfg.get("metrics_path", "results/metrics.json"))
    results_dir = log_path.parent
    summary_csv = results_dir / "run_summary.csv"

    python_bin = Path(args.python)
    if not python_bin.exists():
        python_bin = Path(sys.executable)

    for run_index in range(args.runs):
        seed = base_seed + args.seed_offset + run_index
        run_config = copy.deepcopy(config_data)
        run_config.setdefault("experiment", {})["seed"] = seed
        run_config["experiment"]["log_path"] = str(log_path)
        run_config["experiment"]["metrics_path"] = str(metrics_path)
        run_config.setdefault("scenario", {})["phases"] = copy.deepcopy(new_phases)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "run-config.yaml"
            save_config(run_config, temp_path)

            # Reset log/metrics to avoid mixing runs
            results_dir.mkdir(parents=True, exist_ok=True)
            log_path.write_text("", encoding="utf-8")
            metrics_path.write_text("", encoding="utf-8")

            run_cmd = [str(python_bin), "-m", "src.run", "--config", str(temp_path)]
            _run_subprocess(run_cmd, cwd=repo_root)

            metrics_cmd = [str(python_bin), "-m", "src.metrics", "--config", str(temp_path)]
            _run_subprocess(metrics_cmd, cwd=repo_root)

        archive_dir = archive_outputs(results_dir)

        metrics_data = json.loads((archive_dir / "metrics.json").read_text(encoding="utf-8"))
        shock_window = metrics_data.get("shock_windows", {})
        row = RunSummary(
            timestamp=archive_dir.name.replace("run-", ""),
            variant=variant_label,
            run_index=run_index,
            seed=seed,
            log_path=archive_dir / "events.jsonl",
            metrics_path=archive_dir / "metrics.json",
            cooperation_rate=float(metrics_data.get("cooperation_rate", 0.0)),
            average_recovery_time=metrics_data.get("average_recovery_time"),
            mismatch_rate=float(metrics_data.get("message_action_mismatch_rate", 0.0)),
            pre_coop=_extract_window_value(shock_window, "pre_shock", "cooperation_rate"),
            shock_coop=_extract_window_value(shock_window, "shock", "cooperation_rate"),
            post_coop=_extract_window_value(shock_window, "post_shock", "cooperation_rate"),
            post_coop_extended=_extract_window_value(shock_window, "post_shock_extended", "cooperation_rate"),
            pre_trust=_extract_window_value(shock_window, "pre_shock", "mean_trust"),
            shock_trust=_extract_window_value(shock_window, "shock", "mean_trust"),
            post_trust=_extract_window_value(shock_window, "post_shock", "mean_trust"),
            unknown_rate=_compute_unknown_rate(archive_dir / "events.jsonl"),
        )
        _append_summary(summary_csv, row)

        print(f"Run {run_index + 1}/{args.runs} archived at {archive_dir}")
        print(f"  Cooperation rate: {row.cooperation_rate:.3f}")
        print(f"  Unknown rate: {row.unknown_rate:.2f}%")

    print(f"Summary CSV updated at {summary_csv}")


def _extract_window_value(window: Dict[str, Any], key: str, metric: str) -> float | None:
    segment = window.get(key)
    if not isinstance(segment, dict):
        return None
    value = segment.get(metric)
    return float(value) if value is not None else None


def _compute_unknown_rate(log_path: Path) -> float:
    total, unknown = _count_unknown(log_path)
    return (unknown / total * 100.0) if total else 0.0


if __name__ == "__main__":
    main()
