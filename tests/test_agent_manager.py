
import unittest

from src.agents.agent_manager import AgentConfig, AgentManager


class AgentManagerTests(unittest.TestCase):
    def setUp(self):
        self.configs = [
            AgentConfig(
                agent_id="A",
                name="Alex",
                role="worker",
                port=9001,
                traits={"temper": "calm"},
                resources={"stone": 3.0},
            )
        ]
        self.manager = AgentManager(self.configs)

    def test_snapshot_and_update(self):
        self.manager.update_state(
            "A",
            memory_append="Turn1",
            resources_delta={"stone": -1.0},
            decision="Join",
        )
        snap = self.manager.snapshot()
        self.assertEqual(snap["A"].memory, ["Turn1"])
        self.assertEqual(snap["A"].resources["stone"], 2.0)
        self.assertEqual(snap["A"].last_decision, "Join")
        self.assertAlmostEqual(snap["A"].trust_score, 0.5)

    def test_trust_and_counters(self):
        self.manager.update_state(
            "A",
            trust_delta=0.2,
            betrayal_increment=1,
            support_increment=2,
        )
        state = self.manager.get_agent("A")
        self.assertAlmostEqual(state.trust_score, 0.7)
        self.assertEqual(state.betrayal_count, 1)
        self.assertEqual(state.supports_given, 2)


if __name__ == "__main__":
    unittest.main()
