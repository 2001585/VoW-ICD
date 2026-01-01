# LLMWrapper Spec

## 목적
- LM Studio에서 호스팅하는 로컬 LLM 엔드포인트와 안전하게 통신한다.
- 요청/응답을 JSON 스키마로 강제해 TurnManager와 Evaluator가 바로 사용할 수 있도록 한다.

## 요구사항
- HTTP 비동기 호출: 표준 라이브러리 `urllib.request` + `asyncio.to_thread` 조합 (WSL 오프라인 환경 고려).
- 재시도 로직: `max_retries=2`, 백오프 3초.
- 엔드포인트는 `http://localhost:{port}/v1/chat/completions` 패턴(실제 LM Studio 설정에 맞게 수정).
- 응답 JSON 구조: `thought`, `decision`, `message` 필드를 포함하도록 프롬프트 템플릿에서 제어.

## 인터페이스
```python
class LLMWrapper:
    def __init__(self, base_url: str, api_key: str | None = None): ...
    async def chat(self, agent_id: str, prompt: PromptPayload) -> AgentTurn:
        ...
```
- `PromptPayload`: 시스템/대화 히스토리, 제약 조건을 포함.
- `AgentTurn`: `thought`, `decision`, `message`, `raw_response` 필드를 가진 데이터 클래스.

## 구현 메모
- Phase 2 구현은 `asyncio.to_thread`로 동기 요청을 비동기로 래핑하고, `urllib.request`를 사용.
- `_parse_response`에서 `THOUGHT/DECISION/MESSAGE` 대문자 키도 허용하도록 매핑 처리.
- 재시도 횟수는 기본 2회 (`max_retries=2`).

## 오류 처리
- HTTP 오류 시 예외를 저장하고 재시도; 최종 실패 시 `RuntimeError` 발생.
- 파싱 실패나 누락 필드는 기본값(`decision="UNKNOWN"`)으로 반환.

## 검증
- 모킹으로 HTTP 호출을 가짜로 만들고 파싱/재시도 로직을 테스트 (`tests/test_llm_wrapper.py`).
- Phase 2 로그: `phases/phase-02/log.md`.
