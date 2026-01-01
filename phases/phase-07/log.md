# Phase 7 Log — Persona & Memory Expansion

- 2025-11-03: AgentState에 `trust_score`, `betrayal_count`, `supports_given` 추가. `TurnManager`가 협력/배신 결정에 따라 신뢰 지수를 조정하고, 로그에 모델/페르소나/신뢰 메타데이터를 기록하도록 수정. 관련 테스트 갱신 및 통과 확인.
- 2025-11-03: 단일 모델(`gpt-oss-20b`) 기반 20턴 테스트 구성으로 전환. 페르소나/기억 주입으로 행동 차이를 유지하며, 장기 실험 전에 자원 사용량을 안정화하도록 계획.
