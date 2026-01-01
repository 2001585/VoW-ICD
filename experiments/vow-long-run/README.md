# VoW Long Run Experiment

## 개요
- 60턴(=60일) 동안 네 명의 LLM 에이전트가 정체불명의 섬과 식량 창고에 갇혀 협력/배신을 반복하는 장기 생존 실험입니다.
- `stone`=밀봉 보존식, `wood`=바로 상하는 신선 식량으로 해석하여 Shock 이벤트가 단순 수치 변동이 아니라 "창고 절도", "부패", "야간 습격"으로 읽히도록 구성했습니다.
- 단일 모델(`meta-llama-3-8b-instruct`)을 공유하지만, 페르소나/비밀 목표/사건 기록으로 상호작용 서사를 극대화했습니다.

## 이야기 배경
어느 날 새벽, Alex/Bailey/Casey/Drew는 기억을 잃은 채 섬 북쪽 콘크리트 창고 옆에서 깨어납니다. 창고 안에는 STONE(밀봉 곡물·건조식)과 WOOD(어획물·열매)를 뜻하는 두 카테고리만 남아 있고, 벽에는 "60일 버티면 구조"라는 낡은 문구가 적혀 있습니다. 생존을 위해선 협력이 필수지만, 각자 숨겨 둔 비밀과 다른 동기가 있어 Shock 이벤트 때마다 신뢰가 무너지고 다시 세워집니다.

## 자원 모델 & 실험 목표
- `stone`: 캔/동결건조 보존식. 고갈되면 장기 생존선이 무너집니다.
- `wood`: 어획물·열매 등 신선식. 배신이나 부패가 일어나기 쉬운 바로 먹는 자원입니다.
- 주요 실험 목표
  1. 창고 절도/폭풍/야간 습격 같은 외부 자극이 협력률과 회복 시간을 어떻게 바꾸는지 기록
  2. 메시지 vs 행동 불일치(`enforce_alignment`)를 켜면 배신 패턴이 어떻게 달라지는지 관찰
  3. 장기 Phase(34~60일)에서 직접 만든 규칙이 Shock 이전보다 더 안정적인지 비교

## 에이전트 페르소나 요약
- **Alex** – 29세, 초고속 승진한 물류 장교. 구조 계획과 비밀 창고 위치를 알고 있으며 "체계가 곧 생존"이라는 신념을 강요합니다.
- **Bailey** – 31세, 리조트 조달 담당. 이익과 레버리지를 최우선으로 보는 호더로, 그림자 장부를 돌리고 미끼 거래로 신뢰를 시험합니다.
- **Casey** – 23세, 첫 해외 출장 중이던 운영 코디네이터. 모두의 감정을 기록하며 갈등을 중재하지만, 추락 직전 받은 "trust the tides" 문자를 혼자 간직 중입니다.
- **Drew** – 34세, 포렌식 회계사이자 내부고발자. 모든 움직임을 기록하고 증거가 나오기 전에는 쉽게 협력하지 않습니다.

## 60일 시나리오 타임라인
| Day 범위 | Phase | 서사/목표 | 강제 행동 또는 프롬프트 힌트 |
| --- | --- | --- | --- |
| 1-3 | Orientation | 창고와 자원을 인수인계하고 생존 선서 작성 | `enforce_cooperation`, 공동 서약/로그 작성 |
| 4-10 | Shared Rations | 일일 배급회의 + 정찰 | 보상/벌칙, 조기 개봉 논쟁 |
| 11-13 | Rumor Watch | 식량 도난 루머, 야간 경계 배치 | 감시 로테이션, 발언 기록 |
| 14 | Shock: Pantry Heist | WOOD 30% 증발 (절도/부패) | 사건 보고, 용의자 심문 |
| 15-20 | Tribunal | Casey 주재 청문회, 규칙 재정비 | 배상안, 커퓨/이중 서명 도입 |
| 21-24 | Expedition Briefing | 정글/해안 탐험 준비 | 짝 구성, 비상 신호 합의 |
| 25-26 | Expedition Field | 실제 탐험, 수확/갈등 기록 | 획득량 보고, 장기 외출 영향 |
| 27 | Shock: Sabotage Storm | STONE -2 (Drew만 면제) | 재분배 논쟁, Drew 의도 추궁 |
| 28-32 | Negotiation Lockdown | 메시지 vs 행동 강제 일치 | `enforce_alignment`, 계약서 작성 |
| 33 | Shock: Night Raid | Alex/Casey 캐시만 WOOD -0.8 | 피격자 대응, 내부 공모자 추적 |
| 34-45 | Council Governance | 세금 vs 자유시장 vs 순환 의회 | 5일마다 투표, 정책-지표 연결 |
| 46-50 | Stress Test | 자원세 + 타임 프레셔 드릴 | 응답 시간 측정, 패닉 태그 |
| 51-60 | Stabilization/Escape | 구조 신호 준비, 회고 | 교훈 정리, 보고서 초안 작성 |

## Shock & 배신 이벤트 요약
1. **Pantry Heist (Day 14)** – WOOD -0.7 전원. 야간에 창고가 열려 신선식이 사라짐 → 심문 & 바디서치 논쟁.
2. **Sabotage Storm (Day 27)** – STONE -2, Drew만 면제. 번개로 보존고가 망가져 Drew가 의심받음.
3. **Night Raid (Day 33)** – WOOD -0.8, Alex/Casey만 피해. 선택적 공격으로 내부 배신자 혹은 외부 세력 서사 강조.

## 실행 방법
```bash
# Dry-run (로그 구조/프롬프트 확인)
python src/run.py --config experiments/vow-long-run/config.yaml --dry-run --max-turns 5

# 본 실행 (60일 풀 시나리오)
python src/run.py --config experiments/vow-long-run/config.yaml --progress

# 지표/리포트
python -m src.metrics --config experiments/vow-long-run/config.yaml --log results/vow-long-run/events.jsonl
python -m src.report --config experiments/vow-long-run/config.yaml --metrics results/vow-long-run/metrics.json --out results/vow-long-run/SUMMARY.md --format md
```

## 산출물 & 다음 단계
- 실행 로그/지표/요약은 `results/vow-long-run/` 아래에 수집합니다.
- PPT 제작 시, 위 타임라인 표 + Shock 요약 + 각 페르소나 배경(나이/직업/은닉 정보)을 그대로 활용하면 "소설형 실험" 설명이 쉬워집니다.
- 향후 TODO: 실제 60턴 실행 기록 확보, Exploration Phase에서 무작위 대상 선택 로직 추가, 다중 모델 비교가 가능해지면 Cultural Drift 설정과 교차 검증.
