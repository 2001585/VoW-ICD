# Phase 5 Log — Experiment Expansion & QA

## 2025-10-31
- 공통 설정 로더 `src/utils/config.py` 추가 및 `src/run.py`, `src.metrics`, `src.report`에서 재사용하도록 리팩토링.
- TurnManager 로그 처리 개선: 파일 핸들 버퍼링, 상태 스냅샷 중복 제거, 턴별 flush 도입.
- Evaluator 최적화: 로그 순서 검사 후 필요 시 정렬, 실패 케이스/비정상 로그 테스트 추가.
- 신규 테스트: `tests/test_config_utils.py`, `tests/test_metrics.py` 보완으로 총 11개 유닛 테스트 통과.
- 문서 업데이트: `docs/TurnManager.md`, `docs/Evaluator.md`, Phase 5 백로그/체크리스트, `docs/CLI_FAQ.md` 초안 작성.
- 커버리지 측정: `python3 -m trace --count --summary --missing ...` 명령으로 측정 (`results/vow-baseline/coverage.txt` 기록). 주요 모듈 커버리지 — `run` 96%, `turn_manager` 86%, `llm_wrapper` 86%.

## 2025-10-31 (2차 업데이트)
- `docs/CLI_FAQ.md`를 플래그 표·플랫폼 팁·오류 대응으로 보완해 공식 참고 문서화 완료.
- LLMWrapper 재시도 경로 테스트 추가로 커버리지 ≥86% 달성, trace 재실행 후 결과 파일 갱신.
- 남은 후속 제안: coverage.py 통합 및 FAQ에 추가 예시 링크 정리(추후 여유 있을 때 진행).

## 실행 명령
- `python3 -m unittest discover -s tests`
