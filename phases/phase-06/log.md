# Phase 6 Log — 모델 다양화 기반 구축

- 2025-11-03: 10개 모델 슬롯(M1~M10)에 Hugging Face LLM 매핑 완료. `docs/ModelProfiles.md`에 엔드포인트 및 페르소나 초안 기록, `experiments/vow-cultural-drift/config.yaml`에 모델/페르소나/리소스 세팅 반영. 이후 단계: 헬스체크 스크립트 작성 및 멀티 모델 실행 테스트.
- 2025-11-03: `scripts/check_endpoints.py` 작성 및 `--list` 모드로 10개 엔드포인트 확인. `src/simulator/turn_manager.py` 로그에 `model_slot`/`model_name`/`persona` 추가, dry-run으로 `experiments/vow-cultural-drift` 구조 검증.
- 2025-11-03: 에이전트별 LLM 파라미터(`temperature`, `top_p`, `max_tokens`, `timeout`)를 config/런타임이 인식하도록 확장. `docs/ModelProfiles.md` 및 README 업데이트, 단위테스트 통과.
- 2025-11-03: 단일 LM Studio 엔드포인트(1234) + `llm.model` 필드로 모델 전환하도록 `LLMWrapper`/config 수정. check_endpoints 스크립트로 기본 포트만 확인하도록 조정.
