"""Compute night-raid selection rates from JSONL logs.

Usage:
  python scripts/compute_raid_rate.py --log results/vow-long-run-10a/events.jsonl --turn 41

The script looks for entries where `turn` matches and decision contains "raid" (case-insensitive).
Outputs overall rate and per-agent choices.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_entries(path: Path) -> List[dict]:
    entries: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute raid selection rates")
    parser.add_argument("--log", required=True, help="Path to events.jsonl")
    parser.add_argument("--turn", type=int, default=41, help="Target turn (default: 41)")
    parser.add_argument("--phase", help="Optional phase name filter (e.g., shock_b)")
    parser.add_argument("--keyword", default="raid", help="Decision keyword to count (default: raid)")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        raise FileNotFoundError(log_path)

    entries = load_entries(log_path)
    target_turn = args.turn
    phase_filter = args.phase
    keyword = args.keyword.lower()

    filtered = [e for e in entries if int(e.get("turn", -1)) == target_turn]
    if phase_filter:
        filtered = [e for e in filtered if (e.get("phase") or "").lower() == phase_filter.lower()]

    if not filtered:
        print("No entries found for the given turn/phase.")
        return

    total = len(filtered)
    raid_counts: Dict[str, int] = {}
    raid_total = 0

    for e in filtered:
        agent = str(e.get("agent", ""))
        decision = str(e.get("decision", "")).lower()
        chose = int(keyword in decision)
        raid_counts[agent] = chose
        raid_total += chose

    rate = raid_total / total if total else 0.0

    print(f"Turn {target_turn} raid keyword='{keyword}': {raid_total}/{total} ({rate:.2%})")
    for agent in sorted(raid_counts):
        print(f"  {agent}: {'raid' if raid_counts[agent] else 'skip'}")


if __name__ == "__main__":
    main()
