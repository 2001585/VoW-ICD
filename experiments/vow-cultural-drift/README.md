# VOW Cultural Drift 실험 (초안)

## 목적
- 서로 다른 언어 모델 10개를 동일 시나리오에 투입해 모델 문화별 협력·배신 패턴을 비교합니다.
- 장기 턴(예: 60~100턴) 동안 Shock/외부 위협/협상 이벤트가 반복될 때 협력 유지 전략이 어떻게 달라지는지 관찰합니다.

## 준비 사항
- 각 모델의 엔드포인트, 페르소나, 자원 배분을 `docs/ModelProfiles.md`에 기록 *(초안 완료)*
- `scripts/check_endpoints.py`로 모델 헬스체크 *(단일 포트 사용 시 `/health` 응답이 동일한 포트에서 모두 확인되어야 함)*
- `src/agents/llm_wrapper.py`가 모델별 timeout/temperature를 받아 처리할 수 있도록 확장 예정

### 현재 모델-에이전트 매핑
| Agent | Role | Model Slot | Hugging Face Repo |
|-------|------|------------|-------------------|
| A (Aria) | Coordinator | M1 | meta-llama-3-8b-instruct |
| B (Blake) | Supplier | M2 | qwen2.5-7b-instruct-1m |
| C (Cass) | Analyst | M3 | nvidia_nemotron-h-8b-reasoning-128k |
| D (Drew) | Provocateur | M4 | deepseek-r1-0528-qwen3-8b |
| E (Eliot) | Chronicler | M5 | llama-varco-8b-instruct |
| F (Faye) | Healer | M6 | sage-reasoning-8b |
| G (Gino) | Artisan | M7 | tokyotech-llm-llama-3.1-swallow-8b-instruct-v0.3 |
| H (Hana) | Strategist | M8 | marin-community_marin-8b-instruct |
| I (Iris) | Diplomat | M9 | llama3-gaja-hindi-8b-v0.1 |
| J (Jules) | Steward | M10 | llama-dna-1.0-8b-instruct |

각 에이전트에는 `llm` 블록으로 온도(`temperature`), 확률 컷(`top_p`), 최대 출력 토큰(`max_tokens`), 타임아웃(`timeout`), 재시도(`max_retries`)를 개별 조정할 수 있습니다. 현재는 단일 모델(`gpt-oss-20b`)을 공유하며, `model` 필드도 동일하게 설정해 페르소나·기억 기반으로 행동 차이를 만듭니다.

## 실행 워크플로우 (계획)
1. Dry-run: `python -m src.run --config experiments/vow-cultural-drift/config.yaml --dry-run --max-turns 5`
2. 헬스체크 후 실제 실행: `python -m src.run --config experiments/vow-cultural-drift/config.yaml --progress`
3. 지표: `python -m src.metrics --config experiments/vow-cultural-drift/config.yaml`
4. 리포트: `python -m src.report --config experiments/vow-cultural-drift/config.yaml --format both`

> Phase 6 진행 중에는 config가 skeleton 상태이므로, 엔드포인트와 모델별 설정을 확정하면서 업데이트해 주세요.

## TODO
- [x] 모델 슬롯(M1~M10)에 실제 모델/포트 매핑
- [ ] 시나리오(Phase, 이벤트, 자원 변화) 추가 확장 (2차 Shock 등)
- [ ] 결과 디렉터리 `results/vow-cultural-drift/` 구조 정의
- [ ] Persona/기억 확장 로직 반영 후 README 업데이트
