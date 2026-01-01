import json
import tempfile
import unittest
from pathlib import Path

from src.run import main


class CLITests(unittest.TestCase):
    def test_dry_run_creates_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            config = {
                "experiment": {
                    "name": "test",
                    "seed": 3,
                    "max_turns": 1,
                    "log_path": "events.jsonl",
                    "metrics_path": "metrics.json",
                },
                "agents": [
                    {
                        "agent_id": "A",
                        "name": "Alex",
                        "role": "planner",
                        "port": 9101,
                        "traits": {},
                        "resources": {"stone": 2},
                    }
                ],
                "scenario": {
                    "phases": [
                        {"name": "formation", "turns": [1, 1]},
                    ]
                },
            }
            config_path = base / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            main([
                "--config",
                str(config_path),
                "--dry-run",
            ])

            log_path = base / "events.jsonl"
            self.assertTrue(log_path.exists())
            data = log_path.read_text(encoding="utf-8").strip()
            self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
