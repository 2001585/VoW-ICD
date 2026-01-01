"""CLI entry point for executing Village of Words experiments."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from src.agents.agent_manager import AgentConfig, AgentManager
from src.agents.llm_wrapper import AgentTurn, LLMWrapper, PromptPayload
from src.simulator.turn_manager import (
    PhaseConfig,
    TurnConfig,
    TurnManager,
    TurnResult,
)
from src.utils.config import get_section, load_config, resolve_path


def build_agent_configs(config: Dict[str, Any]) -> List[AgentConfig]:
    agents_config: List[AgentConfig] = []
    for agent in config.get("agents", []):
        raw_endpoint = agent.get("endpoint")
        persona = agent.get("persona")
        model_slot = agent.get("model_slot")
        model_name = agent.get("model_name")
        llm_params = agent.get("llm") or agent.get("llm_params") or {}
        if not isinstance(llm_params, dict):
            llm_params = {}
        agents_config.append(
            AgentConfig(
                agent_id=str(agent["agent_id"]),
                name=str(agent.get("name", agent["agent_id"])),
                role=str(agent.get("role", "")),
                port=int(agent.get("port", 0)),
                traits={k: str(v) for k, v in agent.get("traits", {}).items()},
                resources={k: float(v) for k, v in agent.get("resources", {}).items()},
                endpoint=str(raw_endpoint) if raw_endpoint is not None else None,
                model_slot=str(model_slot) if model_slot is not None else None,
                model_name=str(model_name) if model_name is not None else None,
                persona=str(persona) if persona is not None else None,
                llm_params=llm_params,
            )
        )
    return agents_config


def build_turn_config(raw: Dict[str, Any], override_max_turns: int | None = None) -> TurnConfig:
    experiment = get_section(raw, "experiment")
    scenario = get_section(raw, "scenario")

    base_dir = Path(raw.get("base_dir", "."))
    log_path = resolve_path(base_dir, experiment.get("log_path", "results/events.jsonl"))

    seed = int(experiment.get("seed", 42))
    max_turns = int(override_max_turns or experiment.get("max_turns", 10))

    phases: List[PhaseConfig] = []
    for phase in scenario.get("phases", []):
        turns = phase.get("turns", [1, max_turns])
        phases.append(
            PhaseConfig(
                name=str(phase.get("name", "phase")),
                start=int(turns[0]),
                end=int(turns[1]),
                event=phase.get("event"),
                parameters=phase.get("parameters", {}),
                constraints=phase.get("constraints", {}),
            )
        )

    return TurnConfig(
        seed=seed,
        max_turns=max_turns,
        log_path=log_path,
        phases=phases,
    )


class DryRunWrapper(LLMWrapper):
    """Simple deterministic wrapper for --dry-run executions."""

    RESPONSES = (
        ("Assessing the plan", "Join", "I'll contribute resources."),
        ("Unsure about current plan", "Observe", "I'll wait this turn."),
        ("Gathering feedback", "Cooperate", "Let's coordinate efforts."),
    )

    def __init__(self, agent_id: str):
        super().__init__(base_url="dry-run")
        self.agent_id = agent_id
        self._cursor = 0

    async def chat(self, agent_id: str, payload: PromptPayload) -> AgentTurn:  # type: ignore[override]
        thought, decision, message = self.RESPONSES[self._cursor % len(self.RESPONSES)]
        self._cursor += 1
        return AgentTurn(
            agent_id=agent_id,
            thought=thought,
            decision=decision,
            message=message,
            raw_response={"dry_run": True, "history_length": len(payload.history)},
        )


async def run_experiment(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    raw_config = load_config(config_path)

    agent_configs = build_agent_configs(raw_config)
    agent_manager = AgentManager(agent_configs)

    experiment_section = get_section(raw_config, "experiment")
    seed = args.seed if args.seed is not None else experiment_section.get("seed", 42)
    turn_config = build_turn_config(raw_config, override_max_turns=args.max_turns)
    turn_config.seed = int(seed)

    default_endpoint = experiment_section.get("endpoint")
    endpoint_map_raw = experiment_section.get("endpoint_map", {})
    endpoint_map: Dict[str, str] = {}
    if isinstance(endpoint_map_raw, dict):
        endpoint_map = {
            str(key): str(value)
            for key, value in endpoint_map_raw.items()
        }

    if args.dry_run:
        wrappers = {
            cfg.agent_id: DryRunWrapper(cfg.agent_id) for cfg in agent_configs
        }
    else:
        wrappers: Dict[str, LLMWrapper] = {}
        for cfg in agent_configs:
            params = cfg.llm_params or {}
            temperature = float(params.get("temperature", 0.7))
            top_p = float(params.get("top_p", 0.95))
            max_tokens = int(params.get("max_tokens", 512))
            timeout = float(params.get("timeout", 30.0))
            max_retries = int(params.get("max_retries", 2))
            model_id = str(params.get("model")) if params.get("model") else cfg.model_name

            if cfg.endpoint:
                base_url = cfg.endpoint.rstrip("/")
            elif cfg.model_slot and cfg.model_slot in endpoint_map:
                base_url = endpoint_map[cfg.model_slot].rstrip("/")
            elif default_endpoint:
                base_url = str(default_endpoint).rstrip("/")
            else:
                base_url = f"http://localhost:{cfg.port}"
            wrappers[cfg.agent_id] = LLMWrapper(
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                model=model_id,
            )

    progress_cb = None
    if getattr(args, "progress", False):
        total_turns = turn_config.max_turns

        def progress_cb(result: TurnResult) -> None:
            events = ",".join(result.events) if result.events else "none"
            decisions = ", ".join(
                f"{turn.agent_id}:{turn.decision}" for turn in result.agent_turns
            )
            print(  # noqa: T201 - intentional progress output
                f"[Turn {result.turn}/{total_turns}] phase={result.phase or '-'} "
                f"events={events} decisions={decisions}",
                flush=True,
            )

    manager = TurnManager(
        agent_manager,
        wrappers,
        turn_config,
        progress_callback=progress_cb,
    )
    results = await manager.run()

    metrics_path = experiment_section.get("metrics_path")
    if metrics_path:
        metrics_path = resolve_path(Path(raw_config["base_dir"]), metrics_path)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(
            json.dumps(
                {
                    "turns": len(results),
                    "log_path": str(turn_config.log_path),
                    "dry_run": bool(args.dry_run),
                },
                indent=2,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

    print(  # noqa: T201 - CLI status output
        "Run completed.",
        json.dumps(
            {
                "turns": len(results),
                "log": str(turn_config.log_path),
                "dry_run": bool(args.dry_run),
            }
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Village of Words experiments")
    parser.add_argument("--config", required=True, help="Path to experiment config (YAML or JSON)")
    parser.add_argument("--seed", type=int, help="Override RNG seed")
    parser.add_argument("--max-turns", type=int, help="Override maximum turns")
    parser.add_argument("--dry-run", action="store_true", help="Use deterministic local responses")
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Print per-turn progress (phase, events, decisions).",
    )
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    asyncio.run(run_experiment(args))


if __name__ == "__main__":
    main()
