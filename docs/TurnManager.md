# TurnManager Spec

## 목적
- Village of Words 실험에서 각 턴을 `발언 → 응답 → 행동` 순서로 오케스트레이션한다.
- 에이전트 행동을 JSONL 로그로 남기고 Evaluator에 지표 계산 트리거를 전달한다.

## 요구사항
- THOUGHT/DECISION/MESSAGE 3단계 출력 형식을 강제.
- CLI 기반 실행: `python -m src.run --config ...`에서 호출.
- 각 턴은 시나리오 설정에 정의된 이벤트(충격 이벤트 등)를 확인하고 적용.
- 랜덤 시드 고정(`random.seed`, `numpy.random.seed`).

## 인터페이스
```python
class TurnManager:
    def __init__(self, agent_manager: AgentManager, llm: LLMWrapper, config: TurnConfig): ...
    async def run(self) -> None:
        ...
    async def step(self, turn: int) -> TurnResult:
        ...
```
- `TurnConfig`: 총 턴 수, 이벤트 트리거, 로그 경로 포함.
- `TurnResult`: 각 에이전트의 행동 결과 및 지표 업데이트 상태.

## 구현 메모
- Phase 3 구현에서는 `PhaseConfig`/`TurnConfig` 데이터 클래스를 도입해 시나리오를 구조화함.
- 이벤트 적용은 현재 `resource_drop`만 지원하며, 최초 발생 턴에서 자원 델타를 적용.
- 결정값이 `Join/Cooperate/Contribute`인 경우 자원(예: stone) 1개 감소시켜 협력 행동을 반영.
- 이력(history)는 JSON 문자열 형태로 저장하여 DryRun에서도 구조화된 히스토리를 제공.
- Phase 5에서 로그 파일을 턴 실행 동안 한 번만 열어 버퍼링하며, 각 에이전트 업데이트 후 최신 자원 스냅샷을 직접 기록해 성능 저하를 줄였다.

## 로깅
- `results/<exp>/events.jsonl`에 append 모드로 작성.
- 필수 필드: `turn`, `phase`, `agent`, `thought`, `decision`, `message`, `action`, `resources`.
- 샘플: `results/vow-baseline/events.sample.jsonl` (Phase 3에서 생성).
- 로그는 턴 순서대로 기록되며, 버퍼는 턴 종료마다 flush 되어 중단 발생 시에도 데이터 손실을 최소화한다.

## 검증
- 단위 테스트에서 DummyWrapper 기반 1턴 시뮬레이션 (`tests/test_turn_manager.py`).
- Phase 3 완료 시 샘플 로그(`results/vow-baseline/events.sample.jsonl`) 생성 및 `phases/phase-03/log.md`에 결과 기록.
