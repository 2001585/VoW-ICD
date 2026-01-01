# AgentManager Spec

## 목적
- 다중 LLM 에이전트의 상태(기억, 자원, 목표)를 관리하고 포트 라우팅 정보를 보존한다.
- 실험 중 발생하는 이벤트 로그와 지표 계산 단계가 일관된 에이전트 스냅샷을 참조하도록 보장한다.

## 책임
- `agents_seed.json` 등 초기 설정에서 에이전트 정보를 로드.
- 각 턴 이후 상태 업데이트(자원 증감, 감정/태그, 관계 지표) 처리.
- LM Studio 엔드포인트 포트 매핑과 인증 토큰(필요 시)을 제공.
- 충돌/에러 발생 시 직전 상태를 `crash_state.json`으로 덤프.

## 인터페이스
```python
class AgentManager:
    def __init__(self, agents: list[AgentConfig]): ...
    def get_agent(self, agent_id: str) -> AgentState: ...
    def update_state(
        self,
        agent_id: str,
        *,
        memory_append: str | None = None,
        resources_delta: dict[str, float] | None = None,
        decision: str | None = None,
        trust_delta: float | None = None,
        betrayal_increment: int = 0,
        support_increment: int = 0,
    ) -> None
    def snapshot(self) -> dict[str, AgentState]: ...
    def save(self, path: Path) -> None: ...
```
- `AgentConfig`: 이름, 초기 자원, 성향, LM Studio 포트뿐 아니라 모델 슬롯, 모델 이름, 페르소나, LLM 파라미터(dict)를 포함.
- `AgentState`: 현재 자원, 기억(리스트), 마지막 결정 외에 신뢰 점수(`trust_score`), 배신 횟수(`betrayal_count`), 지원 횟수(`supports_given`)를 유지.
- 상태 저장 포맷: JSON (UTF-8, ASCII 키 사용).

## 동시성/안정성
- 쓰레드 세이프 보장: Lock 또는 asyncio.Queue 기반으로 상태 업데이트 관리.
- 타임아웃 또는 LLMWrapper 실패 시 재시도 2회 적용.

## 구현 메모
- Phase 2에서 Lock 기반 thread-safe 구현 완료 (`src/agents/agent_manager.py`).
- `snapshot()`은 깊은 복사된 `AgentState` 사본을 반환해 TurnManager 측 변조 방지.
- `save()`는 JSON 직렬화를 수행하며 `ensure_ascii=True`로 cross-WSL 호환 확인.

## 검증
- 단위 테스트 `tests/test_agent_manager.py`에서 초기화, 업데이트, 스냅샷 검증.
- Phase 2 로그: `phases/phase-02/log.md`.
