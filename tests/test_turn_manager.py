import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from src.agents.agent_manager import AgentConfig, AgentManager
from src.agents.llm_wrapper import AgentTurn, LLMWrapper, PromptPayload
from src.simulator.turn_manager import PhaseConfig, TurnConfig, TurnManager


class DummyWrapper(LLMWrapper):
    def __init__(self):
        super().__init__(base_url="dummy")

    async def chat(self, agent_id: str, payload: PromptPayload) -> AgentTurn:  # type: ignore[override]
        return AgentTurn(
            agent_id=agent_id,
            thought="Evaluate options",
            decision="Join",
            message="I will contribute",
            raw_response={"test": True},
        )


class TurnManagerTests(unittest.TestCase):
    def test_step_writes_log(self) -> None:
        agent_cfgs = [
            AgentConfig(
                agent_id="A",
                name="Alex",
                role="planner",
                port=9001,
                traits={},
                resources={"stone": 2.0},
            )
        ]
        agent_manager = AgentManager(agent_cfgs)
        wrapper = {"A": DummyWrapper()}

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            turn_config = TurnConfig(
                seed=7,
                max_turns=1,
                log_path=log_path,
                phases=[PhaseConfig(name="formation", start=1, end=3)],
            )
            manager = TurnManager(agent_manager, wrapper, turn_config)
            asyncio.run(manager.run())

            self.assertTrue(log_path.exists())
            content = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(content), 1)
            entry = json.loads(content[0])
            self.assertEqual(entry["turn"], 1)
            self.assertEqual(entry["agent"], "A")
            self.assertEqual(entry["decision"], "Join")
            self.assertIn("trust_score", entry)
            self.assertGreater(entry["trust_score"], 0.5)

    def test_resource_drop_targets_exclusions(self) -> None:
        agent_cfgs = [
            AgentConfig(
                agent_id="A",
                name="Alex",
                role="planner",
                port=9001,
                traits={},
                resources={"stone": 3.0},
            ),
            AgentConfig(
                agent_id="B",
                name="Blake",
                role="supplier",
                port=9002,
                traits={},
                resources={"stone": 3.0},
            ),
        ]
        agent_manager = AgentManager(agent_cfgs)
        wrappers = {agent.agent_id: DummyWrapper() for agent in agent_cfgs}

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            phase = PhaseConfig(
                name="shock",
                start=1,
                end=1,
                event="resource_drop",
                parameters={
                    "target": "all_except",
                    "exclude": ["B"],
                    "delta": {"stone": -2.0},
                },
            )
            turn_config = TurnConfig(
                seed=11,
                max_turns=1,
                log_path=log_path,
                phases=[phase],
            )
            manager = TurnManager(agent_manager, wrappers, turn_config)
            asyncio.run(manager.run())

            state_a = agent_manager.get_agent("A")
            state_b = agent_manager.get_agent("B")
            self.assertEqual(state_a.resources["stone"], 0.0)
            self.assertEqual(state_b.resources["stone"], 2.0)
            self.assertGreater(state_a.trust_score, 0.5)

    def test_progress_callback_receives_turns(self) -> None:
        agent_cfgs = [
            AgentConfig(
                agent_id="A",
                name="Alex",
                role="planner",
                port=9001,
                traits={},
                resources={"stone": 1.0},
            )
        ]
        agent_manager = AgentManager(agent_cfgs)
        wrapper = {"A": DummyWrapper()}

        calls: list[int] = []

        def progress(result):
            calls.append(result.turn)

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            turn_config = TurnConfig(
                seed=3,
                max_turns=1,
                log_path=log_path,
                phases=[PhaseConfig(name="formation", start=1, end=1)],
            )
            manager = TurnManager(
                agent_manager,
                wrapper,
                turn_config,
                progress_callback=progress,
            )
            asyncio.run(manager.run())

        self.assertEqual(calls, [1])


if __name__ == "__main__":
    unittest.main()
