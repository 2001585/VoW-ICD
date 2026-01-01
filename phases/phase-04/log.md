# Phase 4 Log — Metrics & Reporting

## 실행 요약 (2025-10-31)
- `python3 -m unittest discover -s tests`
  - 8 tests 통과 (`tests/test_metrics.py`, `tests/test_report.py` 포함)
- `python3 -m src.metrics --config experiments/vow-baseline/config.yaml --log results/vow-baseline/events.sample.jsonl --out results/vow-baseline/metrics.json`
  - 협력 비율 0.75, 평균 기여량 1.0 계산
- `python3 -m src.report --config experiments/vow-baseline/config.yaml --metrics results/vow-baseline/metrics.json --out results/vow-baseline/SUMMARY.md --format md`
  - `results/vow-baseline/SUMMARY.md`, `results/vow-baseline/report.json` 생성

## 산출물
- `src/metrics.py`: Evaluator/CLI 구현, 규칙 오버라이드 지원
- `src/report.py`: Summary/JSON 리포트 생성
- `tests/test_metrics.py`, `tests/test_report.py`: 메트릭/리포트 파이프라인 단위 테스트
- `results/vow-baseline/metrics.json`, `results/vow-baseline/SUMMARY.md`, `results/vow-baseline/report.json`

## 메모
- config 상대 경로 기본 기준은 실험 디렉터리(`experiments/<exp>/`)이므로 결과 파일은 `--out` 옵션으로 프로젝트 루트 `results/` 아래에 저장.
- 배신 행동 로그 부재로 회복 시간 지표는 `null`로 기록됨. 추후 시나리오 확장 시 케이스 추가 필요.
- PyYAML 미설치 환경 대응을 위해 테스트에서는 임시 JSON config를 생성하여 Metrics/Report CLI를 호출.
