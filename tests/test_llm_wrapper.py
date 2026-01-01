
import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from src.agents.llm_wrapper import AgentTurn, LLMWrapper, PromptPayload


class LLMWrapperTests(unittest.TestCase):
    def test_parse_response(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001")

        fake_payload = {
            "output": {
                "THOUGHT": "Need to help",
                "DECISION": "Join",
                "MESSAGE": "I'll contribute",
            }
        }
        turn = wrapper._parse_response("A", fake_payload)

        self.assertIsInstance(turn, AgentTurn)
        self.assertEqual(turn.decision, "Join")
        self.assertEqual(turn.message, "I'll contribute")

    def test_parse_response_defaults(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001")
        data = {"output": {"thought": "", "message": None}}
        turn = wrapper._parse_response("B", data)
        self.assertEqual(turn.thought, "")
        self.assertEqual(turn.decision, "UNKNOWN")
        self.assertEqual(turn.message, "")

    def test_parse_response_from_choices_json(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001")
        data = {
            "choices": [
                {
                    "message": {
                        "content": '{"THOUGHT": "Plan", "DECISION": "Cooperate", "MESSAGE": "Working together"}'
                    }
                }
            ]
        }
        turn = wrapper._parse_response("C", data)
        self.assertEqual(turn.decision, "Cooperate")
        self.assertEqual(turn.message, "Working together")

    def test_parse_response_from_choices_heuristic(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001")
        data = {
            "choices": [
                {
                    "message": {
                        "content": '"THOUGHT": "Reflect"\n"DECISION": "Observe"\n"MESSAGE": "Waiting to see the outcome"'
                    }
                }
            ]
        }
        turn = wrapper._parse_response("D", data)
        self.assertEqual(turn.decision, "Observe")
        self.assertEqual(turn.message, "Waiting to see the outcome")

    def test_chat_retries_then_succeeds(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001", max_retries=2)
        attempts = {"count": 0}

        def fake_send(url, headers, body):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RuntimeError("temporary failure")
            return {
                "output": {"thought": "Recovered", "decision": "Join", "message": "Back online"}
            }

        async def run_chat():
            with patch.object(wrapper, "_send_request", side_effect=fake_send):
                with patch("src.agents.llm_wrapper.asyncio.sleep", new=AsyncMock(return_value=None)) as mocked_sleep:
                    async def fake_to_thread(func, *args, **kwargs):
                        return func(*args, **kwargs)

                    with patch("src.agents.llm_wrapper.asyncio.to_thread", side_effect=fake_to_thread):
                        payload = PromptPayload(system="sys", history=[])
                        result = await wrapper.chat("A", payload)
                        mocked_sleep.assert_awaited()
                        return result

        turn = asyncio.run(run_chat())
        self.assertEqual(attempts["count"], 2)
        self.assertEqual(turn.decision, "Join")
        self.assertEqual(turn.message, "Back online")

    def test_chat_raises_after_exhausting_retries(self):
        wrapper = LLMWrapper(base_url="http://localhost:9001", max_retries=1)

        async def run_chat():
            with patch.object(wrapper, "_send_request", side_effect=RuntimeError("boom")):
                with patch("src.agents.llm_wrapper.asyncio.sleep", new=AsyncMock(return_value=None)):
                    async def fake_to_thread(func, *args, **kwargs):
                        return func(*args, **kwargs)

                    with patch("src.agents.llm_wrapper.asyncio.to_thread", side_effect=fake_to_thread):
                        payload = PromptPayload(system="sys", history=[])
                        return await wrapper.chat("A", payload)

        with self.assertRaisesRegex(RuntimeError, "failed after retries"):
            asyncio.run(run_chat())


if __name__ == "__main__":
    unittest.main()
