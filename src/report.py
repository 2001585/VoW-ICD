"""Generate textual and structured reports from metrics outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


from src.utils.config import get_section, load_config, resolve_path


def _load_metrics(metrics_path: Path) -> Dict[str, Any]:
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def _format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def _format_float(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.3f}"


class ReportGenerator:
    """Render Markdown and JSON reports for Village of Words experiments."""

    def __init__(self, title: str = "Village of Words Summary") -> None:
        self.title = title

    def render_markdown(self, metrics: Mapping[str, Any]) -> str:
        metadata = metrics.get("metadata", {})
        contributions = metrics.get("contributions", {})
        message_counts = metrics.get("message_counts", {})
        highlights = self._highlights(contributions, message_counts)
        lines = [
            f"# {self.title}",
            "",
            f"- Experiment: {metadata.get('experiment', 'unknown')}",
            f"- Seed: {metadata.get('seed', 'N/A')}",
            f"- Log: `{metadata.get('log_path', 'unknown')}`",
            f"- Generated at: {metadata.get('generated_at', 'N/A')}",
            "",
            "## Key Metrics",
            f"- Cooperation rate: {_format_percentage(metrics.get('cooperation_rate', 0.0))}",
            f"- Average contribution: {_format_float(metrics.get('average_contribution'))}",
            f"- Average recovery time: {_format_float(metrics.get('average_recovery_time'))} turns",
            f"- Contribution Gini: {_format_float(metrics.get('gini_coefficient'))}",
            f"- Dialogue entropy: {_format_float(metrics.get('dialogue_entropy'))}",
            f"- Total turns observed: {metrics.get('total_turns', 0)}",
            f"- Total logged events: {metrics.get('total_events', 0)}",
            "",
        ]
        if highlights:
            lines.extend(["## Highlights"] + [f"- {highlight}" for highlight in highlights] + [""])

        contribution_rows = self._agent_table(contributions, message_counts)
        if contribution_rows:
            lines.append("## Agent Contributions")
            lines.extend(contribution_rows)
        else:
            lines.append("## Agent Contributions\nNo agent data available.")
        return "\n".join(lines).strip() + "\n"

    def render_json(self, metrics: Mapping[str, Any]) -> Dict[str, Any]:
        contributions = metrics.get("contributions", {})
        message_counts = metrics.get("message_counts", {})
        return {
            "title": self.title,
            "summary": {
                "cooperation_rate": metrics.get("cooperation_rate"),
                "average_contribution": metrics.get("average_contribution"),
                "average_recovery_time": metrics.get("average_recovery_time"),
                "gini_coefficient": metrics.get("gini_coefficient"),
                "dialogue_entropy": metrics.get("dialogue_entropy"),
                "total_turns": metrics.get("total_turns"),
                "total_events": metrics.get("total_events"),
            },
            "metadata": metrics.get("metadata", {}),
            "agents": {
                "contributions": contributions,
                "message_counts": message_counts,
            },
            "highlights": self._highlights(contributions, message_counts),
        }

    def _agent_table(
        self,
        contributions: Mapping[str, Any],
        message_counts: Mapping[str, Any],
    ) -> List[str]:
        if not contributions and not message_counts:
            return []
        agents = sorted(set(contributions.keys()) | set(message_counts.keys()))
        rows = ["| Agent | Contribution | Messages |", "| --- | ---: | ---: |"]
        for agent in agents:
            contrib = float(contributions.get(agent, 0.0))
            messages = int(message_counts.get(agent, 0))
            rows.append(f"| {agent} | {contrib:.3f} | {messages} |")
        rows.append("")
        return rows

    def _highlights(
        self,
        contributions: Mapping[str, Any],
        message_counts: Mapping[str, Any],
    ) -> List[str]:
        if not contributions and not message_counts:
            return []
        highlights: List[str] = []
        if contributions:
            leader = max(contributions.items(), key=lambda item: float(item[1]))
            highlights.append(
                f"Top contributor: {leader[0]} ({float(leader[1]):.3f} {self._resource_unit()})"
            )
        if message_counts:
            talker = max(message_counts.items(), key=lambda item: int(item[1]))
            highlights.append(
                f"Most active speaker: {talker[0]} ({int(talker[1])} messages)"
            )
        return highlights

    @staticmethod
    def _resource_unit() -> str:
        return "stone"


def run_cli(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Render reports from metrics outputs.")
    parser.add_argument("--config", required=True, help="Experiment config path.")
    parser.add_argument("--metrics", help="Override metrics.json path.")
    parser.add_argument(
        "--out",
        help="Output path for the primary report (SUMMARY.md or report.json).",
    )
    parser.add_argument(
        "--format",
        choices={"md", "json", "both"},
        default="md",
        help="Report format. Defaults to Markdown.",
    )
    args = parser.parse_args(argv)

    config_path = Path(args.config).resolve()
    raw_config = load_config(config_path)
    base_dir = Path(raw_config["base_dir"])
    experiment = get_section(raw_config, "experiment")

    metrics_path = (
        Path(args.metrics)
        if args.metrics
        else resolve_path(base_dir, experiment.get("metrics_path", "results/metrics.json"))
    )
    metrics_data = _load_metrics(metrics_path)

    default_summary = resolve_path(
        base_dir, experiment.get("summary_path", "results/SUMMARY.md")
    )
    out_path = resolve_path(base_dir, args.out) if args.out else default_summary
    out_path.parent.mkdir(parents=True, exist_ok=True)

    generator = ReportGenerator()
    render_format = args.format

    if render_format in {"md", "both"}:
        markdown = generator.render_markdown(metrics_data)
        out_md = out_path if render_format != "both" or out_path.suffix == ".md" else out_path
        if out_md.suffix != ".md":
            out_md = out_md.with_suffix(".md")
        out_md.write_text(markdown, encoding="utf-8")
        json_path = out_md.with_name("report.json")
    else:
        json_path = out_path if out_path.suffix == ".json" else out_path.with_suffix(".json")

    if render_format in {"json", "both"}:
        json_payload = generator.render_json(metrics_data)
        out_json = json_path
        if render_format == "json":
            out_json = out_path if out_path.suffix == ".json" else out_path.with_suffix(".json")
        out_json.write_text(
            json.dumps(json_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    elif render_format == "md":
        json_payload = generator.render_json(metrics_data)
        json_path.write_text(
            json.dumps(json_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(  # noqa: T201 - CLI feedback
        json.dumps(
            {
                "status": "ok",
                "metrics": str(metrics_path),
                "output": str(out_path),
                "format": render_format,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    run_cli()
