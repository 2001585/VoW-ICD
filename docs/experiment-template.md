# Experiment Template Workflow

Village of Words 실험을 확장할 때는 기존 `experiments/vow-baseline/` 구조를 복제하고, 관련 산출물(`results/<name>/`)을 짝지어 관리합니다. 아래 절차를 따라 새 실험 폴더를 만들고 문서·로그·환경을 정리하세요.

## 1. 준비
- 실험 이름은 kebab-case 사용: 예) `experiments/vow-empathy-swap/`.
- 대응 결과 디렉터리를 `results/<name>/`에 생성.
- `phases/phase-05/log.md` 또는 해당 실험 전용 로그에 작업 내역을 기록.

## 2. 기본 구조 복제
```bash
cp -R experiments/vow-baseline experiments/<new-exp>
rm -f experiments/<new-exp>/requirements.lock
```
- `README.md`: 실험 목적, 차별점, 커맨드, Phase 노트 섹션을 새로 작성.
- `config.yaml`: 아래 항목 업데이트
  - `experiment.name`, `log_path`, `metrics_path`, `summary_path`
  - 시나리오 단계(`scenario.phases`)와 에이전트 자원/포트 등 맞춤 설정
- 필요 시 `notes/`, `configs/`, `data/` 하위 디렉터리를 추가해 보조 파일을 분리.

## 3. 결과·로그 디렉터리 세팅
```bash
mkdir -p results/<new-exp> results/<new-exp>/logs
touch results/<new-exp>/README.md  # 요약/실험 메모
```
- 실행 후 `events.jsonl`, `metrics.json`, `SUMMARY.md`, `report.json`을 저장.
- 요약 문서는 `SUMMARY.md`에 핵심 지표/하이라이트를 기록하고, 추가 그래프는 `plots/` 하위로 분리.

## 4. 실행 체크리스트
1. (옵션) 전처리: `python -m src.preprocess --config experiments/<new-exp>/config.yaml`
2. 본 실험: `python -m src.run --config experiments/<new-exp>/config.yaml [--seed ...]`
3. Dry-run으로 사전 검증: `python -m src.run --config ... --dry-run --max-turns 2`
4. 메트릭 계산: `python -m src.metrics --config experiments/<new-exp>/config.yaml`
5. 리포트 생성: `python -m src.report --config experiments/<new-exp>/config.yaml --format both`

## 5. 문서 & 로그 업데이트
- `docs/PHASE.md`, `AGENTS.md`에 실험 추가/진행 현황 반영.
- `experiments/<new-exp>/README.md`에 실행 커맨드, 하이퍼파라미터, 결과 요약 기록.
- `results/<new-exp>/SUMMARY.md`에 지표 스냅샷과 주요 관찰사항 추가.

## 6. 검증 및 버전 관리
- 최소 테스트: `python -m unittest discover -s tests` (또는 `pytest`) 실행 결과 캡처.
- 커버리지(선택): `python3 -m trace --count --summary --missing --ignore-dir=/usr/lib/python3.12 --ignore-dir=/usr/lib/python3/dist-packages --ignore-dir=.venv scripts/run_unittests.py`
- 환경 스냅샷: `pip freeze > experiments/<new-exp>/requirements.lock`.
- 실험 완료 시 커밋 전 체크:
  - [ ] config/README/summary 최신화
  - [ ] `phases/<phase>/log.md` 기록
  - [ ] 민감 데이터(`data/`) 미추적 확인

추가 자동화 스크립트(`scripts/mk_experiment.sh`)가 준비되기 전까지는 위 수동 절차를 따른 뒤, 개선 아이디어를 `phases/phase-05/notes.md`에 기록해주세요.
