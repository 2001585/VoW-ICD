
"""Wrapper around LM Studio HTTP API for agent interactions."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import request
from urllib.error import URLError, HTTPError


@dataclass
class PromptPayload:
    system: str
    history: list[dict[str, str]]
    constraints: Optional[dict[str, Any]] = None


@dataclass
class AgentTurn:
    agent_id: str
    thought: str
    decision: str
    message: str
    raw_response: Dict[str, Any]


class LLMWrapper:
    """Async client for LM Studio endpoints with retry support."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.95,
        model: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.model = model

    async def chat(self, agent_id: str, payload: PromptPayload) -> AgentTurn:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = {
            "messages": self._build_messages(payload),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        if self.model:
            body["model"] = self.model

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                data = await asyncio.to_thread(self._send_request, url, headers, body)
                return self._parse_response(agent_id, data)
            except Exception as exc:  # noqa: BLE001 broad catch to log and retry
                last_error = exc
                await asyncio.sleep(3)

        raise RuntimeError(f"LM Studio request failed after retries: {last_error}")

    def _send_request(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        req = request.Request(url=url, data=payload, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                content = resp.read().decode("utf-8")
                return json.loads(content)
        except (HTTPError, URLError) as exc:  # pragma: no cover
            raise RuntimeError(f"LM Studio request failed: {exc}") from exc

    def _parse_response(self, agent_id: str, data: Dict[str, Any]) -> AgentTurn:
        output: Dict[str, Any] = data.get("output") or {}

        if not output and data.get("choices"):
            content = (
                data["choices"][0]
                .get("message", {})
                .get("content", "")
            )
            parsed = self._extract_structured_fields(content)
            if parsed:
                output = parsed
            else:
                output = {
                    "THOUGHT": "",
                    "DECISION": "UNKNOWN",
                    "MESSAGE": content,
                }

        thought = output.get("thought") or output.get("THOUGHT") or ""
        decision = output.get("decision") or output.get("DECISION") or "UNKNOWN"
        message = output.get("message") or output.get("MESSAGE") or ""
        return AgentTurn(
            agent_id=agent_id,
            thought=thought,
            decision=decision,
            message=message,
            raw_response=data,
        )

    def _build_messages(self, payload: PromptPayload) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": payload.system}
        ]

        for entry in payload.history:
            role = entry.get("role", "assistant")
            content = entry.get("content", "")
            messages.append({"role": role, "content": content})

        user_lines: list[str] = []
        if payload.constraints:
            user_lines.append("Constraints:")
            user_lines.append(json.dumps(payload.constraints, ensure_ascii=False, indent=2))
        user_lines.append(
            "Return a JSON object with keys THOUGHT, DECISION, MESSAGE. "
            "DECISION must be a single word action (e.g., Join, Defect, Observe). "
            "Respond ONLY with the JSON object and no additional narration."
        )

        messages.append({
            "role": "user",
            "content": "\n".join(user_lines),
        })

        return messages

    def _extract_structured_fields(self, content: str) -> Optional[Dict[str, Any]]:
        text = content.strip()
        if not text:
            return None

        import json as _json

        candidates: list[str] = []
        if text.startswith("```"):
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and part.endswith("}"):
                    candidates.append(part)
        elif "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and part.endswith("}"):
                    candidates.append(part)
        elif text.startswith("{") and text.endswith("}"):
            candidates.append(text)

        for candidate in candidates:
            try:
                data = _json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except _json.JSONDecodeError:
                continue

        # fallback heuristic for colon-separated lines
        fields: Dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().strip('"').upper()
                value = value.strip().strip(',').strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                if key in {"THOUGHT", "DECISION", "MESSAGE"}:
                    fields[key] = value
        return fields or None


__all__ = ["PromptPayload", "AgentTurn", "LLMWrapper"]
