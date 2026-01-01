# Phase 7 Plan — Persona & Memory Expansion

## 목표
- 에이전트 기억 구조에 신뢰 지수·배신/지원 카운터를 통합해 장기 동학을 기록한다.
- 페르소나 지침이 프롬프트·로그·지표에 반영되도록 파이프라인을 조정한다.
- 협력/배신 행동에 따른 상태 변화를 정의하고 지표 계산에서 활용한다.

## 작업 항목
1. `AgentState` 확장 (신뢰 지수, 배신/지원 카운터) 및 `AgentManager.update_state` 인자 추가 *(완료)*
2. `TurnManager`에서 행동별 신뢰 변동 로직 구현 *(완료)*
3. 로그(JSONL)에 모델/페르소나/신뢰 메트릭 기록 *(완료)*
4. `src/metrics.py`에 신뢰·배신·지원 기반 지표 추가 (예: 평균 신뢰, 배신 빈도) *(TODO)*
5. 페르소나 지침 문서 및 config 예시(`docs/ModelProfiles.md`, `experiments/vow-cultural-drift/config.yaml`) 갱신 *(완료)*
6. 장기 실험에서 신뢰 추세를 분석하는 노트북/스크립트 초안 *(TODO)*

## 검증 체크리스트
- [x] 단위 테스트 통과 (`python3 -m unittest discover -s tests`)
- [ ] 장기 dry-run(≥20턴)에서 신뢰·배신 카운터가 변화하는지 확인
- [ ] `results/*.jsonl` 로그에 새 필드가 기록되는지 확인
- [ ] 메트릭 모듈이 신뢰 지표를 노출하도록 업데이트 후 재검증

## 후속 단계
- Phase 8: 100턴 시나리오에서 신뢰 지표를 활용해 문화/모델 비교
- Phase 9: 반복 실험 통계화 및 리포트 자동화
