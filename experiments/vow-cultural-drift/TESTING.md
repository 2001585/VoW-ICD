# VOW Cultural Drift — 20턴 안정화 테스트 가이드

## 목적
- 20턴 구성에서 `decision: "UNKNOWN"` 응답이 5% 이하로 안정화되는지 확인
- Shock(턴 11~12) 이후 신뢰 회복 패턴을 빠르게 검증
- 장기 실험(60턴 이상) 전에 LLM 파라미터(timout/max_tokens)를 튜닝

## 환경 체크리스트
- LM Studio에서 `gpt-oss-20b` 모델을 로드하고 `http://127.0.0.1:1234`에 서버 실행
- 헬스 체크: `python3 scripts/check_endpoints.py --config experiments/vow-cultural-drift/config.yaml`
- 로그 초기화: `> results/vow-cultural-drift/events.jsonl && > results/vow-cultural-drift/metrics.json`

## 실행 절차
1. Dry-run (연결/토큰 길이 확인)
   ```bash
   python3 -m src.run --config experiments/vow-cultural-drift/config.yaml --dry-run --max-turns 5 --progress
   ```
2. 실제 20턴 테스트
   ```bash
   python3 -m src.run --config experiments/vow-cultural-drift/config.yaml --progress
   ```
3. 지표 계산
   ```bash
   python3 -m src.metrics --config experiments/vow-cultural-drift/config.yaml
   ```
4. UNKNOWN 확인 (임시 스크립트)
   ```bash
   python3 scripts/analyze_unknown.py results/vow-cultural-drift/events.jsonl
   ```
   > 미구현 시 `jq` 또는 ad-hoc Python 사용

## 파라미터 튜닝 가이드
- `llm.max_tokens`: 280~320 범위 유지. UNKNOWN 많으면 240~280까지 낮추기.
- `llm.timeout`: 25~30초. 응답 지연 시 35까지 증가 가능하지만, 장기 실험에서는 응답 누락이 더 중요.
- `llm.max_retries`: 2~3으로 유지. 0으로 두면 일시적인 모델 오류에 취약.
- `temperature`: 행동 다양성이 부족하면 0.1 정도씩 상향 조정.

## 로그 보관
- 실행 후 `results/vow-cultural-drift/archives/`에 복사
  ```bash
  python3 scripts/archive_latest.py
  ```
  (스크립트 미구현 시 수동 복사)

## 안정화 기준
- `decision == "UNKNOWN"` 비율 ≤ 5%
- Shock 이후 평균 신뢰가 5턴 내에 0.65 이상으로 회복
- 협력률 35~55% 범위 유지 (Shock 영향 확인을 위한 목표)

이 기준을 충족하면 Phase 8에서 턴 수와 이벤트를 확장하고, 장기 실험으로 넘어갑니다.
