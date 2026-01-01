# Phase 2 Log — Agent Core Skeletons

## Spec Review
- AgentManager, LLMWrapper 문서 재확인: 상태 스냅샷, 재시도 로직 요구사항 확인
- config.yaml 요구 필드(포트, 시드, 시나리오 phases) 반영

## 구현/산출물
- `src/agents/agent_manager.py`: 상태 관리, 스냅샷, JSON 저장
- `src/agents/llm_wrapper.py`: aiohttp 기반 비동기 호출 + 재시도/파싱 로직
- `tests/test_agent_manager.py`: unittest 기반 스냅샷/업데이트 검증 테스트
- `tests/test_llm_wrapper.py`: urllib monkeypatch를 활용한 응답 파싱 테스트
- `experiments/vow-baseline/config.yaml`: 4 에이전트, 시나리오 단계 정의

## 제약 및 TODO
- pytest 패키지 설치 불가 (네트워크 제한) → 표준 `unittest`로 대체
- LLMWrapper는 `urllib` 기반이므로 실제 LM Studio 연결 테스트 필요
- 다음 단계: TurnManager/CLI 구현 전 config 구조 재사용성 점검

## 다음 액션
- Phase 2 체크리스트를 `docs/PHASE.md`에 반영
- `AGENTS.md` Process 섹션에 Phase 2 상태 기록
- Phase 3 착수 전 tests/ 디렉터리 구조 검토
