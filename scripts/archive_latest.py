"""Archive latest run outputs into results/<experiment>/archives/."""
from __future__ import annotations

import argparse
import datetime
import shutil
from pathlib import Path


def archive(base: Path) -> Path:
    archive_dir = base / "archives"
    archive_dir.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = archive_dir / f"run-{stamp}"
    dest.mkdir()
    moved = False
    for name in ["events.jsonl", "metrics.json", "SUMMARY.md"]:
        src = base / name
        if src.exists() and src.stat().st_size > 0:
            shutil.copy2(src, dest / name)
            moved = True
    if not moved:
        dest.rmdir()
        raise FileNotFoundError("No results to archive (events/metrics missing or empty)")
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive latest experiment outputs")
    parser.add_argument(
        "experiment_dir",
        nargs="?",
        default="results/vow-cultural-drift",
        help="Base results directory (default: results/vow-cultural-drift)",
    )
    args = parser.parse_args()
    dest = archive(Path(args.experiment_dir))
    print(f"Archived outputs to {dest}")


if __name__ == "__main__":
    main()
