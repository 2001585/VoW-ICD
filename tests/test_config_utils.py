"""Tests for shared configuration utilities."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.utils.config import get_section, load_config, resolve_path

try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_YAML = False


class ConfigUtilsTest(unittest.TestCase):
    def test_load_config_json_includes_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(
                json.dumps({"experiment": {"name": "test-exp"}}), encoding="utf-8"
            )
            data = load_config(config_path)
            self.assertEqual(Path(tmpdir), data["base_dir"])
            experiment = get_section(data, "experiment")
            self.assertEqual("test-exp", experiment["name"])

    def test_resolve_path_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            resolved = resolve_path(base, "results/output.json")
            self.assertTrue(str(resolved).startswith(str(base.resolve())))
            absolute = resolve_path(base, Path("/tmp/absolute.json"))
            self.assertEqual(Path("/tmp/absolute.json"), absolute)

    @unittest.skipUnless(HAS_YAML, "PyYAML not installed")
    def test_load_config_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(
                yaml.safe_dump({"experiment": {"name": "yaml-exp"}}), encoding="utf-8"
            )
            data = load_config(config_path)
            experiment = get_section(data, "experiment")
            self.assertEqual("yaml-exp", experiment["name"])


if __name__ == "__main__":
    unittest.main()
