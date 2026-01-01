
"""Agent manager handles agent state, memory, and routing information."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional


@dataclass
class AgentConfig:
    agent_id: str
    name: str
    role: str
    port: int
    traits: Dict[str, str]
    resources: Dict[str, float]
    endpoint: Optional[str] = None
    model_slot: Optional[str] = None
    model_name: Optional[str] = None
    persona: Optional[str] = None
    llm_params: Dict[str, object] = field(default_factory=dict)


@dataclass
class AgentState:
    config: AgentConfig
    memory: List[str] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)
    last_decision: Optional[str] = None
    trust_score: float = 0.5
    betrayal_count: int = 0
    supports_given: int = 0


class AgentManager:
    """Manage agent states and provide thread-safe access."""

    def __init__(self, configs: List[AgentConfig]):
        self._lock = Lock()
        self._agents: Dict[str, AgentState] = {
            cfg.agent_id: AgentState(config=cfg, resources=cfg.resources.copy())
            for cfg in configs
        }

    def get_agent(self, agent_id: str) -> AgentState:
        with self._lock:
            if agent_id not in self._agents:
                raise KeyError(f"Unknown agent_id: {agent_id}")
            return self._agents[agent_id]

    def update_state(
        self,
        agent_id: str,
        *,
        memory_append: Optional[str] = None,
        resources_delta: Optional[Dict[str, float]] = None,
        decision: Optional[str] = None,
        trust_delta: Optional[float] = None,
        betrayal_increment: int = 0,
        support_increment: int = 0,
    ) -> None:
        with self._lock:
            state = self._agents.get(agent_id)
            if state is None:
                raise KeyError(f"Unknown agent_id: {agent_id}")
            if memory_append:
                state.memory.append(memory_append)
            if resources_delta:
                for key, delta in resources_delta.items():
                    state.resources[key] = state.resources.get(key, 0.0) + delta
            if decision is not None:
                state.last_decision = decision
            if trust_delta is not None:
                state.trust_score = max(0.0, min(1.0, state.trust_score + trust_delta))
            if betrayal_increment:
                state.betrayal_count += betrayal_increment
            if support_increment:
                state.supports_given += support_increment

    def snapshot(self) -> Dict[str, AgentState]:
        with self._lock:
            return {
                agent_id: AgentState(
                    config=state.config,
                    memory=list(state.memory),
                    resources=state.resources.copy(),
                    last_decision=state.last_decision,
                    trust_score=state.trust_score,
                    betrayal_count=state.betrayal_count,
                    supports_given=state.supports_given,
                )
                for agent_id, state in self._agents.items()
            }

    def save(self, path: Path) -> None:
        import json

        with self._lock:
            serializable = {
                agent_id: {
                    "config": {
                        "agent_id": state.config.agent_id,
                        "name": state.config.name,
                        "role": state.config.role,
                        "port": state.config.port,
                        "traits": state.config.traits,
                        "resources": state.config.resources,
                        "endpoint": state.config.endpoint,
                        "model_slot": state.config.model_slot,
                        "model_name": state.config.model_name,
                        "persona": state.config.persona,
                        "llm_params": state.config.llm_params,
                    },
                    "memory": state.memory,
                    "resources": state.resources,
                    "last_decision": state.last_decision,
                    "trust_score": state.trust_score,
                    "betrayal_count": state.betrayal_count,
                    "supports_given": state.supports_given,
                }
                for agent_id, state in self._agents.items()
            }
        path.write_text(
            json.dumps(serializable, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )


__all__ = ["AgentConfig", "AgentState", "AgentManager"]
