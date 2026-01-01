"""Turn manager orchestrates multi-agent turns and logging."""
from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TextIO

from src.agents.agent_manager import AgentManager
from src.agents.llm_wrapper import AgentTurn, LLMWrapper, PromptPayload


@dataclass
class PhaseConfig:
    name: str
    start: int
    end: int
    event: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

    def includes(self, turn: int) -> bool:
        return self.start <= turn <= self.end


@dataclass
class TurnConfig:
    seed: int
    max_turns: int
    log_path: Path
    phases: List[PhaseConfig]


@dataclass
class TurnResult:
    turn: int
    phase: Optional[str]
    events: List[str]
    agent_turns: List[AgentTurn]


class TurnManager:
    """Run experiment turns, call LLM wrappers, and persist JSONL logs."""

    def __init__(
        self,
        agent_manager: AgentManager,
        wrappers: Dict[str, LLMWrapper],
        config: TurnConfig,
        *,
        progress_callback: Optional[Callable[[TurnResult], None]] = None,
    ) -> None:
        self.agent_manager = agent_manager
        self.wrappers = wrappers
        self.config = config
        self.log_path = config.log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.history: Dict[str, List[Dict[str, str]]] = {
            agent_id: [] for agent_id in wrappers
        }
        self._applied_events: set[tuple[str, int]] = set()
        self._log_handle: Optional[TextIO] = None
        self._progress_callback = progress_callback

    async def run(self) -> List[TurnResult]:
        self._set_seed(self.config.seed)
        results: List[TurnResult] = []
        with self.log_path.open("a", encoding="utf-8") as handle:
            self._log_handle = handle
            try:
                for turn in range(1, self.config.max_turns + 1):
                    result = await self.step(turn)
                    results.append(result)
            finally:
                handle.flush()
                self._log_handle = None
        return results

    async def step(self, turn: int) -> TurnResult:
        phase = self._phase_for_turn(turn)
        events_applied = self._apply_phase_event(phase, turn)

        agent_turns: List[AgentTurn] = []
        for agent_id, wrapper in self.wrappers.items():
            state = self.agent_manager.get_agent(agent_id)
            persona = state.config.persona or ""
            model_name = state.config.model_name or ""
            model_slot = state.config.model_slot or ""
            payload = PromptPayload(
                system=(
                    f"You are {state.config.name} ({state.config.role}). "
                    f"Current phase: {phase.name if phase else 'free'}. "
                    "Respond with THOUGHT, DECISION, MESSAGE fields."
                    + (
                        f"\nModel identifier: {model_name or model_slot}."
                        if (model_name or model_slot)
                        else ""
                    )
                    + (
                        "\nPersona guidelines:\n" + persona
                        if persona
                        else ""
                    )
                ),
                history=self.history[agent_id],
                constraints=phase.constraints if phase else {},
            )

            try:
                turn_result = await wrapper.chat(agent_id, payload)
            except Exception as exc:  # pragma: no cover - drastic failure path
                turn_result = AgentTurn(
                    agent_id=agent_id,
                    thought="",
                    decision="ERROR",
                    message=f"Wrapper failure: {exc}",
                    raw_response={"error": str(exc)},
                )

            self._update_state_from_turn(agent_id, turn, turn_result)
            updated_state = self.agent_manager.get_agent(agent_id)
            self._append_history(agent_id, turn, turn_result)
            self._write_log_entry(
                turn,
                phase,
                turn_result,
                resources=dict(updated_state.resources),
                model_slot=model_slot,
                model_name=model_name,
                persona=persona,
                trust_score=updated_state.trust_score,
                betrayal_count=updated_state.betrayal_count,
                supports_given=updated_state.supports_given,
            )
            agent_turns.append(turn_result)

        if self._log_handle:
            self._log_handle.flush()

        result = TurnResult(
            turn=turn,
            phase=phase.name if phase else None,
            events=events_applied,
            agent_turns=agent_turns,
        )

        if self._progress_callback:
            try:
                self._progress_callback(result)
            except Exception:  # pragma: no cover - progress should not break flow
                pass

        return result

    def _phase_for_turn(self, turn: int) -> Optional[PhaseConfig]:
        for phase in self.config.phases:
            if phase.includes(turn):
                return phase
        return None

    def _apply_phase_event(self, phase: Optional[PhaseConfig], turn: int) -> List[str]:
        if not phase:
            return []

        events: List[str] = []
        event_key = (phase.name, turn)
        if phase.event == "resource_drop" and event_key not in self._applied_events:
            delta = phase.parameters.get("delta", {})
            targets = self._resolve_event_targets(phase.parameters)
            if delta and targets:
                for agent_id in targets:
                    self.agent_manager.update_state(
                        agent_id,
                        memory_append=f"event:{phase.event}",
                        resources_delta=delta,
                    )
                events.append(
                    "resource_drop:" + ",".join(sorted(targets)) + f":{delta}"
                )
                self._applied_events.add(event_key)
        return events

    def _resolve_event_targets(self, parameters: Dict[str, Any]) -> List[str]:
        target_mode = parameters.get("target", "all")
        all_agents = set(self.wrappers.keys())

        if target_mode == "all":
            return list(all_agents)

        if target_mode == "all_except":
            exclusions = set(parameters.get("exclude", []))
            return [agent_id for agent_id in all_agents if agent_id not in exclusions]

        if target_mode in {"only", "include"}:
            includes = set(parameters.get("include", [])) or set(parameters.get("target_ids", []))
            return [agent_id for agent_id in all_agents if agent_id in includes]

        if isinstance(target_mode, list):
            requested = set(target_mode)
            return [agent_id for agent_id in all_agents if agent_id in requested]

        # Fallback: apply to everyone when the mode is unrecognized.
        return list(all_agents)

    def _update_state_from_turn(self, agent_id: str, turn: int, turn_result: AgentTurn) -> None:
        delta: Dict[str, float] = {}
        state = self.agent_manager.get_agent(agent_id)

        decision_val = turn_result.decision
        if isinstance(decision_val, dict):
            decision_str = str(decision_val.get("decision") or decision_val.get("action") or "")
        else:
            decision_str = str(decision_val)
        decision_lower = decision_str.lower()
        trust_delta = 0.0
        betrayal_inc = 0
        support_inc = 0

        if decision_lower in {"join", "cooperate", "contribute", "support", "assist"}:
            if "stone" in state.resources and state.resources["stone"] > 0:
                delta["stone"] = -1.0
            trust_delta += 0.05
            support_inc = 1
        elif decision_lower in {"collect", "gather"}:
            delta["stone"] = delta.get("stone", 0.0) + 1.0
            trust_delta += 0.02
        elif decision_lower in {"defect", "betray", "sabotage", "steal"}:
            trust_delta -= 0.1
            betrayal_inc = 1

        self.agent_manager.update_state(
            agent_id,
            memory_append=f"turn:{turn}:{turn_result.decision}",
            resources_delta=delta or None,
            decision=turn_result.decision,
            trust_delta=trust_delta if trust_delta != 0.0 else None,
            betrayal_increment=betrayal_inc,
            support_increment=support_inc,
        )

    def _append_history(self, agent_id: str, turn: int, turn_result: AgentTurn) -> None:
        entry = {
            "role": "assistant",
            "content": json.dumps(
                {
                    "turn": turn,
                    "decision": turn_result.decision,
                    "message": turn_result.message,
                }
            ),
        }
        self.history[agent_id].append(entry)

    def _write_log_entry(
        self,
        turn: int,
        phase: Optional[PhaseConfig],
        result: AgentTurn,
        *,
        resources: Dict[str, float],
        model_slot: str,
        model_name: str,
        persona: str,
        trust_score: float,
        betrayal_count: int,
        supports_given: int,
    ) -> None:
        if not self._log_handle:
            raise RuntimeError("Log handle not initialized; run() must set it before logging.")
        entry = {
            "turn": turn,
            "phase": phase.name if phase else None,
            "agent": result.agent_id,
            "thought": result.thought,
            "decision": result.decision,
            "message": result.message,
            "action": result.decision,
            "resources": resources,
            "model_slot": model_slot or None,
            "model_name": model_name or None,
            "persona": persona or None,
            "trust_score": trust_score,
            "betrayal_count": betrayal_count,
            "supports_given": supports_given,
        }
        self._log_handle.write(json.dumps(entry, ensure_ascii=True) + "\n")

    @staticmethod
    def _set_seed(seed: int) -> None:
        random.seed(seed)
        try:  # pragma: no cover - optional dependency
            import numpy as np  # type: ignore

            np.random.seed(seed)
        except ImportError:
            pass
