"""Count UNKNOWN decisions in an events.jsonl log."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(path: Path) -> None:
    total = 0
    unknown = 0
    by_agent: dict[str, int] = {}

    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += 1
            data = json.loads(line)
            decision = str(data.get("decision", "")).upper()
            if decision == "UNKNOWN":
                unknown += 1
                agent = str(data.get("agent", "?"))
                by_agent[agent] = by_agent.get(agent, 0) + 1

    rate = (unknown / total * 100) if total else 0.0
    print(f"Total entries: {total}")
    print(f"UNKNOWN decisions: {unknown} ({rate:.2f}% )")
    if by_agent:
        print("Per agent UNKNOWN counts:")
        for agent, count in sorted(by_agent.items()):
            print(f"  {agent}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze UNKNOWN decisions in events log")
    parser.add_argument("log", help="Path to events.jsonl")
    args = parser.parse_args()
    analyze(Path(args.log))


if __name__ == "__main__":
    main()
