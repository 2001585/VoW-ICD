# Phase 6 Plan — 모델 다양화 기반 구축

## 목표
- 10개 에이전트에 서로 다른 언어 모델을 매핑하여 문화/전략 차이를 관찰할 수 있는 환경 마련
- 모델별 엔드포인트/자원 요구량/페르소나를 문서화하고 config로 반영
- 다중 엔드포인트 호출 시 타임아웃, 로깅, 에러 처리를 정비

## 핵심 작업
1. **모델 후보 선정 및 자원 측정**
   - LM Studio 또는 Ollama를 활용해 8B/14B/미소형 모델 혼합 실행 실험
   - VRAM/RAM/추론 속도 기록 → `docs/ModelProfiles.md` 갱신
2. **엔드포인트 구성**
   - 모델별 포트를 명시 (`M1~M10` 슬롯 사용)
   - 헬스체크 스크립트 초안 작성 (예: `scripts/check_endpoints.py`)
3. **config 스켈레톤 작성**
   - `experiments/vow-cultural-drift/config.yaml`에 slot 기반 엔드포인트/에이전트 매핑 작성
   - README에 실험 목적, 모델 배치, 실행 명령 추가
4. **코드 지원 준비**
   - `TurnManager` 로그에 `model_id` 추가 방안 설계
   - `LLMWrapper`에서 모델별 timeout/temperature 조정 기능 구상

## 산출물
- `docs/ModelProfiles.md` 업데이트된 표 및 페르소나 초안
- `experiments/vow-cultural-drift/README.md`, `config.yaml`
- `scripts/check_endpoints.py` (초안)
- 진행 로그: `phases/phase-06/log.md`

## 검증 체크리스트
- [ ] 모든 엔드포인트에서 `/health` 혹은 샘플 요청이 성공한다
- [ ] Dry-run 5턴 실행으로 config 구조 검증
- [ ] 실제 모델 혼합으로 5턴 이상 실행 성공
- [ ] 로그에 모델 식별 정보가 기록된다 (또는 기록 계획 문서화)

## 다음 단계 링크
- Phase 7: 페르소나 및 기억 확장 (Phase 6 완료 후 착수)
- Phase 8: 장기 시나리오 구축 (멀티 모델 환경 안정화 후 진행)
