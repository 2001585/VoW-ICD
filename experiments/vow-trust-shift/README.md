# VOW Trust Shift 실험

## 목표
- 10명의 에이전트가 배신 이벤트 이후 협력률을 어떻게 회복하는지 추적합니다.
- Shock 단계에서 특정 에이전트(Drew)가 손실을 회피할 때 신뢰 리더가 누구인지 파악합니다.
- 메시지와 행동이 불일치할 때 협상 페이즈에서 얼마나 빨리 재정렬되는지를 측정합니다.

## 에이전트 구성
- 공통 설정: `seed=73`, `max_turns=20`, 로그 출력은 `results/vow-trust-shift/`에 저장합니다.
- 에이전트 초기 자원과 성향은 아래 표를 참고하세요.

| ID | 이름  | 역할       | 자원(stone/wood) | 성향 | 동기 | 포트 |
|----|-------|------------|------------------|------|------|------|
| A  | Aria  | 조정자     | 5 / 4            | 외교적 | 공동체 | 9011 |
| B  | Blake | 공급자     | 4 / 6            | 현실적 | 생존 | 9012 |
| C  | Cass  | 분석가     | 4 / 5            | 신중 | 공정 | 9013 |
| D  | Drew  | 모험가     | 6 / 3            | 변덕 | 개인주의 | 9014 |
| E  | Eliot | 기록가     | 3 / 5            | 관찰자 | 지식 | 9015 |
| F  | Faye  | 치료사     | 5 / 5            | 온화 | 조화 | 9016 |
| G  | Gino  | 장인       | 7 / 4            | 고집 | 자부심 | 9017 |
| H  | Hana  | 전략가     | 4 / 7            | 논리 | 보호 | 9018 |
| I  | Iris  | 외교관     | 5 / 3            | 낙관 | 중재 | 9019 |
| J  | Jules | 자원관리자 | 6 / 6            | 계획적 | 균형 | 9020 |

## 시나리오
| Phase | 턴 범위 | 주요 설정 |
|-------|---------|-----------|
| Calibration | 1-5 | `enforce_cooperation: true`로 초기 협력 강화 |
| Autonomy | 6-8 | Drew에게 배신을 유도하는 기대치 전달 |
| Shock | 9 | `resource_drop` 이벤트로 Drew를 제외한 전원 `stone -2` |
| Negotiation | 10-14 | `enforce_alignment: true`로 메시지/행동 불일치 페널티 활성화 |
| Recovery | 15-20 | 협력 회복 모니터링, 자발적 리더십 부상 관찰 |

Shock 단계는 Drew가 손실을 면하게 설계해 배신자의 이득을 강조하고, 이후 협상/회복 단계에서 협력 리더가 누구인지 `src.metrics` 지표(협력률, 평균 기여도, 회복 시간, 메시지 편중도)로 확인합니다.

## 실행
1. Dry-run: `python -m src.run --config experiments/vow-trust-shift/config.yaml --dry-run --max-turns 2`
2. 본 실행: `python -m src.run --config experiments/vow-trust-shift/config.yaml`
  3. 지표 계산: `python -m src.metrics --config experiments/vow-trust-shift/config.yaml`
  4. 리포트 생성: `python -m src.report --config experiments/vow-trust-shift/config.yaml --format both`

실행 결과는 프로젝트 루트의 `results/vow-trust-shift/events.jsonl`, `metrics.json`, `SUMMARY.md`, `report.json`에 저장합니다. 필요 시 `results/vow-trust-shift/logs/`에서 세부 로그를 유지하세요.

> LM Studio 서버를 `http://127.0.0.1:1234`로 실행해 두면 모든 에이전트가 동일 엔드포인트를 공유합니다. 다른 포트를 사용하려면 `config.yaml`의 `experiment.endpoint` 값을 변경하세요.

> 진행 상황이 필요하면 `--progress` 플래그를 추가하세요. 예: `python -m src.run --config ... --progress`

## 재현 및 노트
- 환경 스냅샷: `pip freeze > experiments/vow-trust-shift/requirements.lock`
- Phase 기록: `phases/phase-05/log.md`에 실험 진행 상황을 업데이트합니다.
- Dry-run이나 실험 중 특이사항이 있다면 본 README 하단 또는 `results/vow-trust-shift/SUMMARY.md`에 메모를 남깁니다.

## 다음 단계 체크리스트
- [ ] Dry-run에서 Shock 이벤트 적용 여부 확인 (Drew 제외)
- [ ] 실제 실행 후 협력률/회복 시간 지표 기록
- [ ] 결과 요약을 `results/vow-trust-shift/SUMMARY.md`에 추가
- [ ] 필요 시 턴 수 조정(회복이 충분히 포착되지 않으면 22턴까지 확장 고려)
