"""Shared helpers for loading experiment configuration files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping


PYAML_MESSAGE = "PyYAML이 필요합니다. `pip install pyyaml`로 설치 후 다시 시도하세요."


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML or JSON config and attach base directory metadata."""
    text = config_path.read_text(encoding="utf-8")
    suffix = config_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(PYAML_MESSAGE) from exc
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Config file must define a mapping at the top level.")
    data["base_dir"] = config_path.parent
    return data


def resolve_path(base_dir: Path, value: str | Path) -> Path:
    """Resolve experiment-relative paths to absolute ones."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def get_section(raw_config: Mapping[str, Any], key: str) -> Dict[str, Any]:
    """Return a dictionary section from the config, or an empty dict."""
    section = raw_config.get(key, {})
    return dict(section) if isinstance(section, Mapping) else {}
