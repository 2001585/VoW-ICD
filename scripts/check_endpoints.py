"""Endpoint health check utility for multi-model experiments."""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Optional

import urllib.error
import urllib.request

from pathlib import Path


PYAML_MESSAGE = "PyYAML 필요: `pip install pyyaml`"


def load_config(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(PYAML_MESSAGE) from exc
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Config top-level은 매핑이어야 합니다.")
    return data


@dataclass
class Endpoint:
    slot: str
    url: str
    agent_ids: list[str]


def collect_endpoints(config: Dict[str, object]) -> Iterable[Endpoint]:
    experiment = config.get("experiment", {})
    if not isinstance(experiment, dict):
        experiment = {}
    endpoint_map = experiment.get("endpoint_map", {})
    if not isinstance(endpoint_map, dict):
        endpoint_map = {}

    agents = config.get("agents", [])
    if not isinstance(agents, list):
        agents = []

    slot_to_agents: Dict[str, list[str]] = {}
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        slot = str(agent.get("model_slot")) if agent.get("model_slot") else None
        agent_id = str(agent.get("agent_id")) if agent.get("agent_id") else None
        if slot and agent_id:
            slot_to_agents.setdefault(slot, []).append(agent_id)

    if endpoint_map:
        for slot, url in endpoint_map.items():
            yield Endpoint(slot=str(slot), url=str(url), agent_ids=slot_to_agents.get(str(slot), []))
    else:
        default_endpoint = experiment.get("endpoint")
        if default_endpoint:
            yield Endpoint(slot="default", url=str(default_endpoint), agent_ids=[cfg for agent_list in slot_to_agents.values() for cfg in agent_list] or [agent.get("agent_id") for agent in agents if isinstance(agent, dict)])


def ping(url: str, timeout: float = 3.0) -> tuple[bool, Optional[str], float]:
    req = urllib.request.Request(url=url.rstrip("/") + "/health", method="GET")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed = time.time() - start
            return True, body.decode("utf-8", errors="replace"), elapsed
    except urllib.error.URLError as exc:  # pragma: no cover - depends on environment
        return False, str(exc), time.time() - start


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check model endpoint availability")
    parser.add_argument("--config", required=True, help="Experiment config (YAML/JSON)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Request timeout (sec)")
    parser.add_argument("--list", action="store_true", help="Only list endpoints without pinging")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    data = load_config(config_path)

    rows = list(collect_endpoints(data))
    if not rows:
        print("No endpoints found in config.")
        return 0

    print(f"Checking {len(rows)} endpoints from {config_path}")
    for endpoint in rows:
        agents = ",".join(endpoint.agent_ids) or "(no agents)"
        if args.list:
            print(f"- {endpoint.slot}: {endpoint.url} -> agents [{agents}]")
            continue

        ok, info, elapsed = ping(endpoint.url, timeout=args.timeout)
        status = "OK" if ok else "FAIL"
        extra = info or ""
        print(f"- {endpoint.slot}: {endpoint.url} [{status}] {elapsed:.2f}s {extra}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
