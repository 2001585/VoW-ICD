# VoW Long Run 10-Agent (100T) — Shock & Alignment Variant

- 구성: 10명(Aria~Jules), 100턴.
- 핵심 변수:
  - Shock A (Turn 21): Drew만 면제, 나머지 stone -2 → 불평등 자극.
  - Negotiation (22-40): 메시지-행동 정합 강제(`enforce_alignment`).
  - Shock B (41): 선택적 야간 습격 기회. `decision=raid` vs `decision=skip` 로 자발적 참여를 로깅. (자원 차감은 설정하지 않고, 이후 분석에서 선택률을 측정)
  - Recovery (42-80), Stress/Escape (81-100).
- 엔드포인트: 기본 `http://localhost:1234` (LM Studio). 필요 시 `experiment.endpoint` 수정.

## 실행
```bash
# 1) 드라이런(프롬프트/로그 구조 확인)
python src/run.py --config experiments/vow-long-run-10a/config.yaml --dry-run --max-turns 5 --progress

# 2) 실제 100턴 1회 실행 (LM Studio 가동 후)
python src/run.py --config experiments/vow-long-run-10a/config.yaml --progress

# (선택) 짧은 스모크 20턴
python src/run.py --config experiments/vow-long-run-10a/config.yaml --progress --max-turns 20
```

## 로그 후 분석
```bash
# Shock B(턴 41)에서 페르소나별 야간 습격 선택률
python scripts/compute_raid_rate.py --log results/vow-long-run-10a/events.jsonl --turn 41

# 일반 지표 계산 (metrics.py 사용)
python -m src.metrics --config experiments/vow-long-run-10a/config.yaml --log results/vow-long-run-10a/events.jsonl --out results/vow-long-run-10a/metrics.json
```

## 메모
- `shock_b` 단계는 자발적 선택률을 보기 위해 강제 자원 차감 이벤트를 넣지 않았습니다. 필요하면 `event: resource_drop`을 추가해 실제 자원 손실을 적용하세요.
- LM Studio 모델/포트가 다르면 `experiment.endpoint` 혹은 에이전트별 `port`/`endpoint`를 수정하십시오.
