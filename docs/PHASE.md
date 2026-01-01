# Village of Words Phases

이 문서는 Codex와 협업할 때 반드시 따라야 할 단계별 개발 순서를 정의합니다. 각 Phase 완료 후에는 체크리스트 상태를 이 문서와 `AGENTS.md` 노트에 즉시 반영하세요. 현재 기준으로 Phase 1~5는 완료되었으며, Phase 6 이후는 다중 모델 실험 확장을 위한 계획 단계입니다.

## Phase 1 — 환경 & 스펙 기반 정비
- [x] WSL 필수 패키지 설치 확인 (`python3`, `python3-venv`, `python3-pip`, `git`, `build-essential`)
- [x] `.venv` 생성, `pip install -U pip pytest` 실행 시도 및 `which python`으로 활성 상태 기록 *(PyPI 네트워크 차단으로 설치 보류 — `phases/phase-01/log.md` 참고)*
- [x] 프로젝트 디렉터리 구조 점검 (`docs/`, `src/`, `experiments/`, `results/`, `tests/`, `data/`, `phases/`)
- [x] `.gitignore` 최신 상태 유지(데이터/로그/가상환경 제외 여부 확인)
- [x] `docs/01~05` 내용 요약 및 Phase 1 로그를 `phases/phase-01/`에 남김
- [x] 컴포넌트 스펙 문서 초안 작성/검토 (`docs/AgentManager.md`, `docs/LLMWrapper.md`, `docs/TurnManager.md`, `docs/Evaluator.md`, `docs/CLI.md`)
- [x] Phase 1 완료 후 `AGENTS.md` 체크리스트 및 메모 갱신 *(Process 섹션 유지, Phase 로그 링크 추가 예정)*

- [x] 스펙 문서(AgentManager, LLMWrapper) 기반 설계 검증 메모 기록 (`phases/phase-02/log.md`)
- [x] `src/agents/agent_manager.py` 스켈레톤 + 주요 메서드 구현 (상태 로드/업데이트/스냅샷)
- [x] `src/agents/llm_wrapper.py` 구현 (LM Studio 호출, 타임아웃·재시도·파싱)
- [x] `experiments/vow-baseline/config.yaml` 초안 생성 (에이전트 목록, 포트, 시드)
- [x] 단위 테스트 뼈대 (`tests/test_agent_manager.py`, `tests/test_llm_wrapper.py`) 작성 *(pytest 설치 대기)*
- [x] Phase 2 진행 중 이슈/우회 방법을 `experiments/vow-baseline/README.md`와 `phases/phase-02/log.md`에 기록
- [x] `docs/AgentManager.md`, `docs/LLMWrapper.md`에 구현 내용 반영(인터페이스/결정 사항 업데이트)

## Phase 3 — 턴 매니저 및 실행 파이프라인
- [x] 스펙 문서(TurnManager, CLI) 검토 후 필요한 보완 작성
- [x] `src/simulator/turn_manager.py` 구현 (턴 절차, 이벤트 처리, JSON 출력 강제)
- [x] `src/run.py` CLI 엔트리 작성 (`python -m src.run --config ...`)
- [x] 샘플 실행 로그 `results/vow-baseline/events.sample.jsonl` 생성 및 검토 메모 작성
- [x] 턴 시뮬레이션 기본 테스트 (`tests/test_turn_manager.py`, `tests/test_cli.py`) 추가 — `python -m unittest discover -s tests`
- [x] Phase 3 로그와 체크리스트 업데이트 (`phases/phase-03/log.md`, `AGENTS.md`)

## Phase 4 — 평가 및 리포트 자동화
- [x] `docs/Evaluator.md` 요구사항 재검토 후 업데이트
- [x] `src/metrics.py` 구현 (협력 비율, 평균 기여, 회복 시간 등)
- [x] `src/report.py` 작성 (SUMMARY.md, 표/그래프 생성)
- [x] `python -m src.metrics` / `python -m src.report` 실행 예시와 결과를 `phases/phase-04/`에 기록
- [x] `results/vow-baseline/SUMMARY.md` 초안 작성 및 버전관리
- [x] 전체 테스트(`pytest`) 및 리그레션 체크, 커버리지 측정 시작 *(네트워크 제한으로 `python3 -m unittest` 대체 실행)*
- [x] Phase 4 완료 후 체크리스트 업데이트

## Phase 5 — 실험 확장 및 품질 점검
- [x] 추가 실험 템플릿 (`experiments/<new-exp>/`) 생성 절차를 `docs/`에 문서화
- [x] 리팩토링/성능 개선 이슈 목록화 후 우선순위 결정 (`phases/phase-05/notes.md`)
- [x] 공통 config 로더 및 TurnManager 로깅 최적화 적용 (Phase 5 백로그 P0/P1 정리)
- [x] 커버리지 목표(≥70%) 달성 여부 점검 및 리포트 저장 *(2025-10-31 trace 측정: 핵심 모듈 74~96%, `src/agents/llm_wrapper.py` 86%)*
- [x] CLI 사용 가이드 및 FAQ를 `docs/`에 추가/보완 *(완성 문서: `docs/CLI_FAQ.md`)*
- [x] 최종 문서/체크리스트 리뷰, 릴리스 준비 및 회고 작성 *(회고: `phases/phase-05/retrospective.md`)*

## Phase 6 — 모델 다양화 기반 구축 *(진행 예정)*
- [ ] LM Studio/Ollama 등에서 다중 모델 동시 구동 방식 조사 및 자원 요구량 기록
- [ ] 에이전트별 `endpoint`/모델/페르소나 정의 초안 작성 (`docs/ModelProfiles.md` 개설)
- [ ] 멀티 모델 실험용 config 스켈레톤 생성 (`experiments/vow-cultural-drift/config.yaml`)
- [ ] `TurnManager`/로그 포맷에 모델 식별자 추가 여부 검토 후 구현 계획 수립
- [ ] `phases/phase-06/plan.md`에 실험 준비 체크리스트 정리

## Phase 7 — 페르소나 및 기억 확장 *(진행 중)*
- [x] `AgentState`에 장기 목표·신뢰지수·배신 이력 등 확장 필드 설계
- [x] 프롬프트 구조화(히스토리 반영, 장기 의사결정 근거 서술) 가이드 문서화 *(`docs/ModelProfiles.md` 업데이트)*
- [x] 모델/역할별 페르소나 시트 완성(`docs/ModelProfiles.md` 업데이트)
- [ ] Dry-run 및 실제 모델로 10~15턴 검증 실행, 캐릭터성 유효성 평가
- [ ] 평가 결과를 `phases/phase-07/log.md`에 기록 *(부분 기록 완료 — 장기 실험 후 보강)*

## Phase 8 — 장기 시나리오 및 이벤트 확장 *(진행 예정)*
- [ ] 100턴 규모 시나리오 설계 (Shock/외부 위협/교역 등 이벤트 블록 정의)
- [ ] `scenario.phases` 확장: Phase별 규칙·자원 변화·페널티 상세화
- [ ] 대용량 로그 처리를 위한 결과 디렉터리 구조/압축 전략 수립
- [ ] 타임아웃/성능 모니터링 로깅 추가 (API 호출 시간, 실패율)
- [ ] 시범 실행 후 문제점 및 자원 사용량을 `phases/phase-08/log.md`에 정리

## Phase 9 — 분석 지표 고도화 및 반복 실험 *(진행 예정)*
- [ ] 불신 점수, 리더십 전환, 메시지-행동 불일치 누적 등 추가 메트릭 설계·구현
- [ ] Shock 강도/모델 조합/시드 등 변수를 조합한 반복 실험 배치 계획 수립
- [ ] 결과 집계를 위한 통계/시각화 스크립트 초안 작성 (`scripts/` 또는 `notebooks/`)
- [ ] `results/` 리포트 템플릿에 그래프/표 자동 삽입 기능 추가
- [ ] 반복 실험 요약을 `phases/phase-09/log.md` 및 `AGENTS.md`에 업데이트

## Phase 10 — 문서화 및 논문화 준비 *(진행 예정)*
- [ ] Phase 6~9 성과를 기반으로 `docs/experiment-template.md`와 스펙 문서 최신화
- [ ] `docs/ModelProfiles.md`, `docs/PHASE.md`, `AGENTS.md` 간 링크 구조 정비
- [ ] 주요 실험 보고서 초안 (`docs/experiments/vow-cultural-drift.md` 등) 작성
- [ ] 재현 절차 문서화: 실행 커맨드, 모델 설정, 데이터 정리 가이드 명문화
- [ ] 학회/논문 제출을 위한 요약본·그래프·부록 구성 초안 마련

> 새 대화로 전환할 때는 **Phase별 체크박스**, `AGENTS.md`, 그리고 관련 `docs/*.md` 내용을 먼저 읽어 현재 상태를 파악해야 합니다. 즉흥 개발은 금지이며, 지정된 단계 밖의 작업이 필요하면 먼저 문서를 수정하고 승인을 받은 후 진행합니다.
