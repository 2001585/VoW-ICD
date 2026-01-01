"""Metrics computation CLI for Village of Words logs."""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

from src.utils.config import get_section, load_config, resolve_path


COOP_MESSAGE_KEYWORDS = {
    "cooperate",
    "cooperation",
    "collaborate",
    "together",
    "assist",
    "support",
    "share",
    "join",
    "alliance",
    "help",
    "trust",
    "rebuild",
    "stabilize",
}

DEFECT_MESSAGE_KEYWORDS = {
    "defect",
    "betray",
    "steal",
    "hoard",
    "withhold",
    "refuse",
    "withdraw",
    "sabotage",
    "abandon",
    "reject",
}


@dataclass(frozen=True)
class EvaluationRules:
    cooperative_decisions: frozenset[str]
    betrayal_decisions: frozenset[str]
    resource_key: str = "stone"

    @classmethod
    def default(cls) -> "EvaluationRules":
        return cls(
            cooperative_decisions=frozenset(
                {"join", "cooperate", "contribute", "support", "assist"}
            ),
            betrayal_decisions=frozenset({"defect", "betray", "steal", "sabotage"}),
            resource_key="stone",
        )

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "EvaluationRules":
        if not data:
            return cls.default()
        coop = data.get("cooperative_decisions")
        betrayal = data.get("betrayal_decisions")
        resource_key = str(data.get("resource_key", "stone"))
        cooperative = (
            frozenset(str(item).lower() for item in coop)
            if isinstance(coop, (list, tuple, set, frozenset))
            else cls.default().cooperative_decisions
        )
        betrayal_set = (
            frozenset(str(item).lower() for item in betrayal)
            if isinstance(betrayal, (list, tuple, set, frozenset))
            else cls.default().betrayal_decisions
        )
        return cls(
            cooperative_decisions=cooperative,
            betrayal_decisions=betrayal_set,
            resource_key=resource_key,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "cooperative_decisions": sorted(self.cooperative_decisions),
            "betrayal_decisions": sorted(self.betrayal_decisions),
            "resource_key": self.resource_key,
        }


@dataclass
class MetricsResult:
    cooperation_rate: float
    average_contribution: float
    average_recovery_time: Optional[float]
    gini_coefficient: float
    dialogue_entropy: float
    total_events: int
    total_turns: int
    contributions: Dict[str, float] = field(default_factory=dict)
    message_counts: Dict[str, int] = field(default_factory=dict)
    phase_summary: Dict[str, Any] = field(default_factory=dict)
    turn_series: List[Dict[str, Any]] = field(default_factory=list)
    shock_windows: Dict[str, Any] = field(default_factory=dict)
    message_action_mismatch_count: int = 0
    message_action_mismatch_rate: float = 0.0
    message_action_mismatches: Dict[str, int] = field(default_factory=dict)
    top_contributor_share: float = 0.0
    leadership_distribution: Dict[str, Any] = field(default_factory=dict)
    persona_summary: Dict[str, Any] = field(default_factory=dict)
    shock_matrix_summary: Dict[str, Any] = field(default_factory=dict)
    message_action_alignment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        return {
            "cooperation_rate": self.cooperation_rate,
            "average_contribution": self.average_contribution,
            "average_recovery_time": self.average_recovery_time,
            "gini_coefficient": self.gini_coefficient,
            "dialogue_entropy": self.dialogue_entropy,
            "total_events": self.total_events,
            "total_turns": self.total_turns,
            "contributions": self.contributions,
            "message_counts": self.message_counts,
            "phase_summary": self.phase_summary,
            "turn_series": self.turn_series,
            "shock_windows": self.shock_windows,
            "message_action_mismatch_count": self.message_action_mismatch_count,
            "message_action_mismatch_rate": self.message_action_mismatch_rate,
            "message_action_mismatches": self.message_action_mismatches,
            "top_contributor_share": self.top_contributor_share,
            "leadership_distribution": self.leadership_distribution,
            "persona_summary": self.persona_summary,
            "shock_matrix_summary": self.shock_matrix_summary,
            "message_action_alignment": self.message_action_alignment,
            "metadata": self.metadata,
        }


class Evaluator:
    """Evaluate experiment logs and compute collaboration metrics."""

    def __init__(self, rules: EvaluationRules | None = None) -> None:
        self.rules = rules or EvaluationRules.default()

    def evaluate(self, log_path: Path) -> MetricsResult:
        entries = self._load_entries(log_path)
        return self._compute_metrics(entries, log_path)

    def save(self, metrics: MetricsResult, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(metrics.to_json(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load_entries(self, log_path: Path) -> List[Dict[str, Any]]:
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
        entries: List[Dict[str, Any]] = []
        with log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                entries.append(json.loads(stripped))
        return entries

    def _compute_metrics(
        self,
        entries: List[Dict[str, Any]],
        log_path: Path,
    ) -> MetricsResult:
        if not entries:
            metadata = {
                "generated_at": self._now_iso(),
                "log_path": str(log_path),
                "agents": [],
                "turns": [],
                "rules": self.rules.to_json(),
            }
            return MetricsResult(
                cooperation_rate=0.0,
                average_contribution=0.0,
                average_recovery_time=None,
                gini_coefficient=0.0,
                dialogue_entropy=0.0,
                total_events=0,
                total_turns=0,
                contributions={},
                message_counts={},
                phase_summary={},
                turn_series=[],
                shock_windows={},
                message_action_mismatch_count=0,
                message_action_mismatch_rate=0.0,
                message_action_mismatches={},
                metadata=metadata,
            )

        cooperative = self.rules.cooperative_decisions
        betrayal = self.rules.betrayal_decisions
        resource_key = self.rules.resource_key

        ordered_entries = entries
        previous_turn: Optional[int] = None
        for entry in entries:
            turn = int(entry.get("turn", 0))
            if previous_turn is not None and turn < previous_turn:
                ordered_entries = sorted(
                    entries,
                    key=lambda item: (int(item.get("turn", 0)), str(item.get("agent", ""))),
                )
                break
            previous_turn = turn

        total_events = len(ordered_entries)
        turns: set[int] = set()
        agents: set[str] = set()

        coop_count = 0
        contributions: Dict[str, float] = defaultdict(float)
        contribution_events = 0
        message_counts: Dict[str, int] = defaultdict(int)
        last_resources: Dict[str, float] = {}
        last_defection_turn: Dict[str, Optional[int]] = {}
        recovery_durations: List[int] = []
        mismatch_counts: Dict[str, int] = defaultdict(int)
        mismatch_total = 0
        agent_trust_sum: Dict[str, float] = defaultdict(float)
        agent_trust_count: Dict[str, int] = defaultdict(int)
        phase_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total": 0,
                "coop": 0,
                "betrayal": 0,
                "trust_sum": 0.0,
                "trust_count": 0,
                "turns": set(),
            }
        )
        turn_stats: Dict[int, Dict[str, Any]] = {}

        for entry in ordered_entries:
            agent = str(entry.get("agent", ""))
            agents.add(agent)
            decision_raw = str(entry.get("decision", ""))
            decision = decision_raw.lower()
            turn = int(entry.get("turn", 0))
            turns.add(turn)
            phase_raw = str(entry.get("phase", "") or "unknown")

            phase_data = phase_stats[phase_raw]
            phase_data["total"] += 1
            phase_data["turns"].add(turn)

            if turn not in turn_stats:
                turn_stats[turn] = {
                    "total": 0,
                    "coop": 0,
                    "betrayal": 0,
                    "trust_sum": 0.0,
                    "trust_count": 0,
                    "phase_counts": defaultdict(int),
                }
            turn_info = turn_stats[turn]
            turn_info["total"] += 1
            turn_info["phase_counts"][phase_raw] += 1

            contributions.setdefault(agent, 0.0)
            last_defection_turn.setdefault(agent, None)

            if decision in cooperative:
                coop_count += 1
                phase_data["coop"] += 1
                turn_info["coop"] += 1
                if last_defection_turn.get(agent) is not None:
                    diff = turn - last_defection_turn[agent]  # type: ignore[index]
                    if diff > 0:
                        recovery_durations.append(diff)
                    last_defection_turn[agent] = None
            elif decision in betrayal:
                phase_data["betrayal"] += 1
                turn_info["betrayal"] += 1
                last_defection_turn[agent] = turn

            message_text = str(entry.get("message", ""))
            intent = _infer_message_intent(message_text)
            decision_intent = (
                "coop"
                if decision in cooperative
                else "defect"
                if decision in betrayal
                else None
            )
            if intent and decision_intent and intent != decision_intent:
                mismatch_counts[agent] += 1
                mismatch_total += 1

            trust_score = entry.get("trust_score")
            if isinstance(trust_score, (int, float)):
                trust_value = float(trust_score)
                phase_data["trust_sum"] += trust_value
                phase_data["trust_count"] += 1
                turn_info["trust_sum"] += trust_value
                turn_info["trust_count"] += 1
                agent_trust_sum[agent] += trust_value
                agent_trust_count[agent] += 1

            resources = entry.get("resources", {})
            if isinstance(resources, Mapping) and resource_key in resources:
                current_value = float(resources[resource_key])
                if agent in last_resources:
                    delta = last_resources[agent] - current_value
                    if delta > 0:
                        contributions[agent] += delta
                        contribution_events += 1
                last_resources[agent] = current_value

            message_counts[agent] += 1

        cooperation_rate = coop_count / total_events if total_events else 0.0
        average_contribution = (
            sum(contributions.values()) / contribution_events if contribution_events else 0.0
        )
        gini = _gini(list(contributions.values()))
        entropy = _entropy(list(message_counts.values()))
        average_recovery_time = (
            sum(recovery_durations) / len(recovery_durations) if recovery_durations else None
        )
        mismatch_rate = mismatch_total / total_events if total_events else 0.0
        total_contribution = sum(value for value in contributions.values() if value > 0)
        if contributions:
            top_agent, top_value = max(contributions.items(), key=lambda item: item[1])
        else:
            top_agent, top_value = None, 0.0
        top_share = top_value / total_contribution if total_contribution > 0 else 0.0
        total_messages = sum(message_counts.values())
        persona_summary: Dict[str, Any] = {}
        for agent in sorted(agents):
            contrib_val = round(contributions.get(agent, 0.0), 4)
            contribution_share = (
                round(contributions.get(agent, 0.0) / total_contribution, 4)
                if total_contribution > 0
                else 0.0
            )
            messages = message_counts.get(agent, 0)
            message_share = round(messages / total_messages, 4) if total_messages else 0.0
            avg_trust_agent = (
                round(agent_trust_sum[agent] / agent_trust_count[agent], 4)
                if agent_trust_count[agent]
                else None
            )
            persona_summary[agent] = {
                "contribution": contrib_val,
                "contribution_share": contribution_share,
                "messages": messages,
                "message_share": message_share,
                "avg_trust": avg_trust_agent,
            }

        leadership_distribution = {
            "gini": round(gini, 4),
            "top_contributor": top_agent,
            "top_contribution": round(top_value, 4),
            "top_contributor_share": round(top_share, 4),
            "total_contribution": round(total_contribution, 4),
        }

        phase_summary: Dict[str, Any] = {}
        for phase_name, stats in phase_stats.items():
            total_phase_events = stats["total"]
            phase_coop_rate = stats["coop"] / total_phase_events if total_phase_events else 0.0
            phase_betrayal_rate = (
                stats["betrayal"] / total_phase_events if total_phase_events else 0.0
            )
            mean_trust_phase = (
                stats["trust_sum"] / stats["trust_count"] if stats["trust_count"] else None
            )
            phase_summary[phase_name] = {
                "events": total_phase_events,
                "cooperative_events": stats["coop"],
                "betrayal_events": stats["betrayal"],
                "cooperation_rate": round(phase_coop_rate, 4) if total_phase_events else 0.0,
                "betrayal_rate": round(phase_betrayal_rate, 4) if total_phase_events else 0.0,
                "mean_trust": round(mean_trust_phase, 4) if mean_trust_phase is not None else None,
                "turns": sorted(stats["turns"]),
            }

        turn_series: List[Dict[str, Any]] = []
        for turn in sorted(turn_stats):
            info = turn_stats[turn]
            total_turn_events = info["total"]
            coop_events = info["coop"]
            betrayal_events = info["betrayal"]
            coop_rate_turn = coop_events / total_turn_events if total_turn_events else 0.0
            betrayal_rate_turn = (
                betrayal_events / total_turn_events if total_turn_events else 0.0
            )
            mean_trust_turn = (
                info["trust_sum"] / info["trust_count"] if info["trust_count"] else None
            )
            if info["phase_counts"]:
                dominant_phase = max(info["phase_counts"].items(), key=lambda item: item[1])[0]
            else:
                dominant_phase = "unknown"
            turn_series.append(
                {
                    "turn": turn,
                    "phase": dominant_phase,
                    "events": total_turn_events,
                    "cooperative_events": coop_events,
                    "betrayal_events": betrayal_events,
                    "cooperation_rate": round(coop_rate_turn, 4)
                    if total_turn_events
                    else 0.0,
                    "betrayal_rate": round(betrayal_rate_turn, 4)
                    if total_turn_events
                    else 0.0,
                    "mean_trust": round(mean_trust_turn, 4)
                    if mean_trust_turn is not None
                    else None,
                }
            )

        def build_window(turn_numbers: List[int]) -> Optional[Dict[str, Any]]:
            if not turn_numbers:
                return None
            existing = [turn_stats.get(number) for number in sorted(set(turn_numbers))]
            existing = [item for item in existing if item]
            if not existing:
                return None
            total_e = sum(item["total"] for item in existing)
            if total_e <= 0:
                return None
            coop_e = sum(item["coop"] for item in existing)
            betrayal_e = sum(item["betrayal"] for item in existing)
            trust_sum = sum(item["trust_sum"] for item in existing)
            trust_count = sum(item["trust_count"] for item in existing)
            mean_trust_value = trust_sum / trust_count if trust_count else None
            turn_list = sorted(set(turn_numbers))
            return {
                "turns": turn_list,
                "events": total_e,
                "cooperative_events": coop_e,
                "betrayal_events": betrayal_e,
                "cooperation_rate": round(coop_e / total_e, 4),
                "betrayal_rate": round(betrayal_e / total_e, 4),
                "mean_trust": round(mean_trust_value, 4) if mean_trust_value is not None else None,
            }

        shock_windows: Dict[str, Any] = {}
        shock_turns = [
            item["turn"] for item in turn_series if "shock" in item["phase"].lower()
        ]
        if shock_turns:
            shock_start = min(shock_turns)
            shock_end = max(shock_turns)
            recorded_turns = sorted(turn_stats)
            min_turn_recorded = recorded_turns[0]
            max_turn_recorded = recorded_turns[-1]
            window_span = 3

            def collect_range(start: int, end: int) -> List[int]:
                if start > end:
                    return []
                return [turn for turn in range(start, end + 1) if turn in turn_stats]

            pre_span = min(window_span, shock_start - min_turn_recorded)
            post_span = min(window_span, max_turn_recorded - shock_end)
            pre_turns = collect_range(shock_start - pre_span, shock_start - 1) if pre_span > 0 else []
            shock_range = collect_range(shock_start, shock_end)
            post_turns = (
                collect_range(shock_end + 1, shock_end + post_span) if post_span > 0 else []
            )
            extended_span = min(10, max_turn_recorded - shock_end)
            post_extended_turns = (
                collect_range(shock_end + 1, shock_end + extended_span)
                if extended_span > 0
                else []
            )
            shock_windows = {
                "phase_turns": shock_range,
                "window_size": window_span,
                "pre_shock": build_window(pre_turns),
                "shock": build_window(shock_range),
                "post_shock": build_window(post_turns),
                "post_shock_extended": build_window(post_extended_turns),
                "post_shock_extended_span": extended_span,
            }
        shock_matrix_summary: Dict[str, Any] = {}
        if shock_windows:
            def extract_block(key: str) -> Optional[Dict[str, Any]]:
                block = shock_windows.get(key)
                if not isinstance(block, Mapping):
                    return None
                return {
                    "turns": block.get("turns"),
                    "cooperation_rate": block.get("cooperation_rate"),
                    "mean_trust": block.get("mean_trust"),
                }

            shock_matrix_summary = {
                "shock_turns": shock_windows.get("phase_turns"),
                "pre_shock": extract_block("pre_shock"),
                "shock": extract_block("shock"),
                "post_shock": extract_block("post_shock"),
                "post_shock_extended": extract_block("post_shock_extended"),
            }

        metadata = {
            "generated_at": self._now_iso(),
            "log_path": str(log_path),
            "agents": sorted(agents),
            "turns": sorted(turns),
            "rules": self.rules.to_json(),
        }

        return MetricsResult(
            cooperation_rate=cooperation_rate,
            average_contribution=average_contribution,
            average_recovery_time=average_recovery_time,
            gini_coefficient=gini,
            dialogue_entropy=entropy,
            total_events=total_events,
            total_turns=len(turns),
            contributions={agent: round(contributions.get(agent, 0.0), 4) for agent in sorted(agents)},
            message_counts={agent: message_counts.get(agent, 0) for agent in sorted(agents)},
            phase_summary=phase_summary,
            turn_series=turn_series,
            shock_windows=shock_windows,
            message_action_mismatch_count=mismatch_total,
            message_action_mismatch_rate=round(mismatch_rate, 4),
            message_action_mismatches={agent: mismatch_counts.get(agent, 0) for agent in sorted(agents)},
            top_contributor_share=round(top_share, 4),
            leadership_distribution=leadership_distribution,
            persona_summary=persona_summary,
            shock_matrix_summary=shock_matrix_summary,
            message_action_alignment={
                "total_mismatches": mismatch_total,
                "mismatch_rate": round(mismatch_rate, 4),
                "by_agent": {agent: mismatch_counts.get(agent, 0) for agent in sorted(agents)},
            },
            metadata=metadata,
        )

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()


def _infer_message_intent(message: str) -> Optional[str]:
    message_lower = message.lower()
    coop_hits = {kw for kw in COOP_MESSAGE_KEYWORDS if kw in message_lower}
    defect_hits = {kw for kw in DEFECT_MESSAGE_KEYWORDS if kw in message_lower}

    if coop_hits and not defect_hits:
        return "coop"
    if defect_hits and not coop_hits:
        return "defect"
    if not message_lower.strip():
        return None
    # Detect explicit negations like "not cooperate"
    if coop_hits:
        for kw in coop_hits:
            if re.search(rf"not\s+{re.escape(kw)}", message_lower):
                return "defect"
    if defect_hits:
        for kw in defect_hits:
            if re.search(rf"not\s+{re.escape(kw)}", message_lower):
                return "coop"
    return None


def _gini(values: List[float]) -> float:
    filtered = [value for value in values if value >= 0]
    if not filtered:
        return 0.0
    total = sum(filtered)
    if math.isclose(total, 0.0):
        return 0.0
    sorted_values = sorted(filtered)
    n = len(sorted_values)
    cumulative = 0.0
    weighted_sum = 0.0
    for idx, value in enumerate(sorted_values, start=1):
        cumulative += value
        weighted_sum += idx * value
    return (2 * weighted_sum) / (n * total) - (n + 1) / n


def _entropy(counts: List[int]) -> float:
    filtered = [count for count in counts if count > 0]
    if len(filtered) <= 1:
        return 0.0
    total = sum(filtered)
    entropy = 0.0
    for count in filtered:
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


def _load_rules_override(path: Optional[str]) -> Mapping[str, Any] | None:
    if not path:
        return None
    rule_path = Path(path)
    with rule_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_cli(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Compute Village of Words metrics.")
    parser.add_argument("--config", required=True, help="Experiment config path (YAML or JSON).")
    parser.add_argument("--log", help="Override log file path.")
    parser.add_argument("--out", help="Override metrics output path.")
    parser.add_argument("--rules", help="JSON file overriding evaluation rules.")
    args = parser.parse_args(argv)

    config_path = Path(args.config).resolve()
    raw_config = load_config(config_path)
    base_dir = Path(raw_config["base_dir"])

    experiment = get_section(raw_config, "experiment")
    log_path = (
        Path(args.log)
        if args.log
        else resolve_path(base_dir, experiment.get("log_path", "results/events.jsonl"))
    )
    out_path = (
        Path(args.out)
        if args.out
        else resolve_path(base_dir, experiment.get("metrics_path", "results/metrics.json"))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    evaluation_section = get_section(raw_config, "evaluation")
    rules_config: MutableMapping[str, Any] = dict(evaluation_section)
    override = _load_rules_override(args.rules)
    if override:
        rules_config.update(override)

    rules = EvaluationRules.from_mapping(rules_config)
    evaluator = Evaluator(rules)
    metrics = evaluator.evaluate(log_path)
    metadata = metrics.metadata
    metadata.update(
        {
            "config_path": str(config_path),
            "metrics_path": str(out_path),
            "experiment": experiment.get("name"),
            "seed": experiment.get("seed"),
        }
    )
    metrics.metadata = metadata
    evaluator.save(metrics, out_path)

    print(  # noqa: T201 - CLI feedback
        json.dumps(
            {
                "status": "ok",
                "log": str(log_path),
                "output": str(out_path),
                "cooperation_rate": round(metrics.cooperation_rate, 4),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    run_cli()
