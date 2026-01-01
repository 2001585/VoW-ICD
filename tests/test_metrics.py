"""Tests for metrics computation pipeline."""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
import tempfile

from src.metrics import Evaluator, EvaluationRules, run_cli


class EvaluatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.log_path = Path("results/vow-baseline/events.sample.jsonl").resolve()
        if not self.log_path.exists():
            self.skipTest("Sample log not found; skipping metrics tests.")

    def test_evaluator_computes_expected_metrics(self) -> None:
        evaluator = Evaluator(EvaluationRules.default())
        result = evaluator.evaluate(self.log_path)

        self.assertEqual(result.total_events, 4)
        self.assertEqual(result.total_turns, 2)
        self.assertAlmostEqual(result.cooperation_rate, 0.75, places=3)
        self.assertAlmostEqual(result.average_contribution, 1.0, places=3)
        self.assertIsNone(result.average_recovery_time)
        self.assertAlmostEqual(result.gini_coefficient, 0.0, places=3)
        self.assertAlmostEqual(result.dialogue_entropy, 1.0, places=3)
        self.assertEqual(result.contributions["A"], 1.0)
        self.assertEqual(result.contributions["B"], 1.0)
        self.assertEqual(result.message_counts["A"], 2)
        self.assertEqual(result.message_counts["B"], 2)
        self.assertEqual(result.metadata["agents"], ["A", "B"])

    def test_evaluator_missing_log_raises(self) -> None:
        evaluator = Evaluator(EvaluationRules.default())
        with self.assertRaises(FileNotFoundError):
            evaluator.evaluate(Path("results/vow-baseline/nonexistent.jsonl"))

    def test_evaluator_handles_unsorted_entries(self) -> None:
        evaluator = Evaluator(EvaluationRules.default())
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            entries = [
                {
                    "turn": 2,
                    "phase": "autonomy",
                    "agent": "A",
                    "thought": "Later turn",
                    "decision": "Join",
                    "message": "Contributing",
                    "resources": {"stone": 1.0},
                },
                {
                    "turn": 1,
                    "phase": "formation",
                    "agent": "A",
                    "thought": "First entry",
                    "decision": "Join",
                    "message": "Starting",
                    "resources": {"stone": 2.0},
                },
                {
                    "turn": 1,
                    "phase": "formation",
                    "agent": "B",
                    "thought": "Observer",
                    "decision": "Observe",
                    "message": "Wait",
                    "resources": {"stone": 3.0},
                },
            ]
            log_path.write_text(
                "\n".join(json.dumps(entry) for entry in entries),
                encoding="utf-8",
            )
            result = evaluator.evaluate(log_path)
            self.assertEqual(result.total_turns, 2)
            self.assertAlmostEqual(result.contributions["A"], 1.0, places=3)
            self.assertEqual(result.contributions["B"], 0.0)


class MetricsCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.log_path = Path("results/vow-baseline/events.sample.jsonl").resolve()
        if not self.log_path.exists():
            self.skipTest("Sample log not found; skipping CLI test.")

    def test_cli_writes_metrics_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "experiment": {
                            "name": "metrics-test",
                            "seed": 42,
                            "log_path": str(self.log_path),
                            "metrics_path": str(Path(tmpdir) / "metrics.json"),
                        }
                    }
                ),
                encoding="utf-8",
            )
            out_path = Path(tmpdir) / "metrics.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                run_cli(
                    [
                        "--config",
                        str(config_path),
                        "--log",
                        str(self.log_path),
                        "--out",
                        str(out_path),
                    ]
                )
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIn("cooperation_rate", data)
            self.assertAlmostEqual(data["cooperation_rate"], 0.75, places=3)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(Path(payload["output"]).resolve(), out_path.resolve())


if __name__ == "__main__":
    unittest.main()
