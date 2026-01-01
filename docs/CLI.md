# CLI Spec

## 목적
- Village of Words 실험을 커맨드라인에서 관리·실행할 수 있는 일관된 도구 세트를 제공한다.
- 주요 진입점: `python -m src.preprocess`, `python -m src.run`, `python -m src.metrics`, `python -m src.report`.

## 공통 규칙
- 모든 커맨드는 `--config experiments/<exp>/config.yaml`을 기본 인자로 받는다.
- WSL 환경에서 실행되며 `.venv` 활성화가 선행되어야 한다.
- 로그/결과 경로는 `config.yaml`에서 명시하고 절대경로 대신 프로젝트 상대경로 사용.

## 서브커맨드 요구사항
1. `preprocess`
   - 입력: `data/raw/` 소재 데이터, 초기 상태 템플릿.
   - 출력: `data/processed/state_init.json`, `scenario_turns.json`.
2. `run`
   - TurnManager를 호출해 실험을 수행.
   - 지원 옵션: `--seed`, `--max-turns`, `--dry-run` (로컬 deterministic wrapper 사용).
   - 로그 경로/metrics 경로는 config에 정의되며 상대경로는 config 파일 기준으로 해석.
3. `metrics`
   - `src.metrics` 모듈을 통해 Evaluator를 호출해 `metrics.json` 생성.
   - 옵션: `--log`(로그 경로 override), `--out`(출력 경로 override), `--rules`(평가 규칙 JSON).
4. `report`
   - `src.report` 모듈이 `metrics.json`을 읽어 `SUMMARY.md`와 `report.json`을 생성.
   - 옵션: `--metrics`(입력 메트릭 경로), `--out`(요약 파일 경로), `--format`(`md`/`json`).

## UX 고려사항
- `--help` 옵션으로 각 커맨드 설명 제공.
- 성공 시 결과 파일 경로를 출력하고 체크리스트 업데이트를 안내.

## 구현 메모 (Phase 3)
- `src/run.py`는 YAML(`pyyaml`) 또는 JSON config를 로드하며, `--dry-run` 시 `DryRunWrapper`를 사용하여 네트워크 의존성을 제거.
- 실행 결과는 `metrics_path`가 지정된 경우 요약 JSON을 기록.

## 검증
- Phase별로 smoke test를 작성하여 CLI 진입점이 최소 실행 성공 여부를 확인한다 (`tests/test_cli.py`, `tests/test_metrics.py`, `tests/test_report.py`).
- Phase 5에서 CLI 사용 설명서를 `docs/`에 추가 업데이트.
