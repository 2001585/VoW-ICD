# Phase 3 Log — Turn Manager & CLI

## 스펙 검토
- `docs/TurnManager.md`, `docs/CLI.md` 요구사항 재확인: THOUGHT/DECISION/MESSAGE 강제, 이벤트 처리, CLI 옵션(`--dry-run`, `--max-turns`)
- config 구조(`experiments/vow-baseline/config.yaml`)를 TurnConfig, PhaseConfig로 매핑하는 방식 정리

## 구현 사항
- `src/simulator/turn_manager.py`: PhaseConfig, TurnConfig, TurnManager 구현 (시드 고정, 이벤트 적용, 로그 작성)
- `src/run.py`: CLI 파서, DryRunWrapper, config 로더(JSON/YAML) 작성
- 샘플 로그 `results/vow-baseline/events.sample.jsonl` 생성 (2턴, 2명 에이전트 예시)

## 테스트
- `tests/test_turn_manager.py`: DummyWrapper 기반 run() 실행 및 로그 검증
- `tests/test_cli.py`: `--dry-run`으로 CLI 스모크 테스트 (임시 config.json 사용)
- `tests/test_agent_manager.py`, `tests/test_llm_wrapper.py`: 기존 테스트 유지 (unittest 기반)
- 명령: `python -m unittest discover -s tests` (venv 활성화 후 실행) — 4 tests OK

## 제약 및 TODO
- PyYAML 설치가 어렵다면 config를 JSON으로 제공하거나 README에 설치 방법 안내 필요
- TurnManager 이벤트 로직은 `resource_drop`만 지원 — 이후 Phase에서 확장 예정
- CLI는 metrics.json에 최소 정보만 기록 — Phase 4에서 Evaluator 연동 필요

## 다음 단계 준비
- Phase 4에서 Evaluator/Report 구현 시 TurnManager 로그 스키마 재사용
- CLI help 메시지와 사용자 문서 업데이트 필요 (Phase 5에서 FAQ 작성 예정)
