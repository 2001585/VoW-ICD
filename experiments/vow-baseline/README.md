# VOW Baseline 실험

## 목표
- Village of Words 실험 초안(docs/vow-draft-experiments.pdf)에 맞춰 최소 재현 가능한 베이스라인 구현.

## 데이터
- 위치: `data/raw/` (비공개, 깃 추적 제외)
- 전처리 산출물: `data/processed/`

## 환경
- WSL + Python venv
- 생성: `python3 -m venv .venv && source .venv/bin/activate`
- 설치: `pip install -r requirements.txt` (초기에 `pytest`, 필요시 `numpy`, `pandas` 등 추가)

## 설정
- 공통 랜덤시드: `42`
- 경로: 입력 `data/processed/`, 출력 `results/vow-baseline/`
- 설정 예시: `experiments/vow-baseline/config.yaml` (필요 시 생성)

## 실행
- 전처리: `python -m src.preprocess --in data/raw --out data/processed`
- 학습/평가: `python -m src.train --data data/processed --out results/vow-baseline --seed 42`

## 지표
- 정확도/정밀도/재현율, 또는 초안에 기재된 핵심 지표.
- 결과 저장: `results/vow-baseline/metrics.json`, `results/vow-baseline/logs/`

## 재현
- 환경 고정: `pip freeze > experiments/vow-baseline/requirements.lock`
- 커밋 시: 스크립트/설정 변화 설명, 커맨드 기록 포함

## Phase Notes
- 2025-10-30 (Phase 2):
  - `experiments/vow-baseline/config.yaml` 초안 작성 (4 agents, shock 이벤트 포함)
  - 외부 패키지 설치 제한 → 테스트는 표준 `unittest` 기반으로 유지
  - LM Studio 호출용 래퍼는 `urllib.request` 사용 (추후 실제 엔드포인트 연결 시 검증 필요)
- 2025-10-30 (Phase 3):
  - `src/simulator/turn_manager.py`, `src/run.py` 구현 및 DryRun 모드 추가
  - 샘플 로그 `results/vow-baseline/events.sample.jsonl` 생성
  - `python -m unittest discover -s tests`로 4개 테스트 통과 (venv 활성화 필요)
- 2025-10-31 (Phase 4):
  - `src/metrics.py`, `src/report.py` 추가로 협력 지표 계산 및 SUMMARY 생성 자동화
  - `python3 -m src.metrics --config ... --log results/vow-baseline/events.sample.jsonl --out results/vow-baseline/metrics.json`
  - `python3 -m src.report --config ... --metrics results/vow-baseline/metrics.json --out results/vow-baseline/SUMMARY.md --format md`
  - `results/vow-baseline/metrics.json`, `SUMMARY.md`, `report.json` 산출 (회복 시간 지표는 배신 로그 부재로 `null`)

## 참고
- 설계 기준: `docs/vow-draft-experiments.pdf`
