"""Tests for report generation pipeline."""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
import tempfile

from src.metrics import run_cli as metrics_cli
from src.report import ReportGenerator, run_cli as report_cli


class ReportGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_log = Path("results/vow-baseline/events.sample.jsonl").resolve()
        if not self.sample_log.exists():
            self.skipTest("Sample log missing.")

    def _build_config(self, base_dir: Path) -> Path:
        config_path = base_dir / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "experiment": {
                        "name": "report-test",
                        "seed": 42,
                        "log_path": str(self.sample_log),
                        "metrics_path": str(base_dir / "metrics.json"),
                        "summary_path": str(base_dir / "SUMMARY.md"),
                    }
                }
            ),
            encoding="utf-8",
        )
        return config_path

    def _build_metrics(self, config_path: Path, destination: Path) -> Path:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            metrics_cli(
                [
                    "--config",
                    str(config_path),
                    "--log",
                    str(self.sample_log),
                    "--out",
                    str(destination),
                ]
            )
        return destination

    def test_report_generator_outputs_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_path = Path(tmpdir) / "metrics.json"
            config_path = self._build_config(Path(tmpdir))
            self._build_metrics(config_path, metrics_path)
            metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))

            generator = ReportGenerator()
            markdown = generator.render_markdown(metrics_payload)
            self.assertIn("## Key Metrics", markdown)
            self.assertIn("Cooperation rate", markdown)

            json_payload = generator.render_json(metrics_payload)
            self.assertIn("summary", json_payload)
            self.assertIn("cooperation_rate", json_payload["summary"])

    def test_report_cli_produces_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_path = Path(tmpdir) / "metrics.json"
            config_path = self._build_config(Path(tmpdir))
            self._build_metrics(config_path, metrics_path)
            summary_path = Path(tmpdir) / "SUMMARY.md"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                report_cli(
                    [
                        "--config",
                        str(config_path),
                        "--metrics",
                        str(metrics_path),
                        "--out",
                        str(summary_path),
                        "--format",
                        "md",
                    ]
                )

            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("Village of Words Summary", summary_text)
            report_json = summary_path.with_name("report.json")
            payload = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertAlmostEqual(payload["summary"]["cooperation_rate"], 0.75, places=3)
            cli_output = json.loads(stdout.getvalue())
            self.assertEqual(cli_output["status"], "ok")
            self.assertEqual(cli_output["format"], "md")


if __name__ == "__main__":
    unittest.main()
