# CLI FAQ (초안)

> Phase 5에서 정식 FAQ 문서를 작성하기 위한 초안입니다. 주요 질문과 답변은 실험 자동화가 안정화되는 대로 보완하세요.

## 1. 기본 실행 순서는?
- `python -m src.run --config experiments/<exp>/config.yaml`
- `python -m src.metrics --config experiments/<exp>/config.yaml`
- `python -m src.report --config experiments/<exp>/config.yaml --format both`

## 2. PyYAML이 없다면?
- `src.utils.config.load_config`가 JSON을 지원하므로 동일 구조의 `.json` 설정을 사용하거나 PyYAML을 설치합니다.
- PyYAML 설치: `.venv/bin/pip install PyYAML` (네트워크가 필요함).

## 3. 로그·결과 경로는 어떻게 해석되나?
- 모든 경로는 기본적으로 설정 파일이 위치한 디렉터리를 기준으로 상대 경로를 해석합니다 (`src.utils.config.resolve_path`).
- CLI 옵션으로 `--out`, `--metrics`, `--log` 등을 지정하면 동일한 기준으로 절대 경로로 변환됩니다.

## 4. Dry-run 옵션은 언제 쓰나요?
- `python -m src.run --config ... --dry-run --max-turns 2`처럼 사용하면 LLM 호출 없이 결정적 응답을 반환합니다.
- 실험 전 파이프라인이 정상 동작하는지, 로그/메트릭 경로가 올바른지 빠르게 검증할 때 활용하세요.

## 5. 여러 실험을 배치로 돌리려면?
- 동일 스크립트에서 설정 목록을 순회하며 `src.run`, `src.metrics`, `src.report`를 순차 실행하세요.
- 각 실험마다 `results/<exp>/` 하위에 로그/메트릭/리포트를 저장하도록 config에서 경로를 분리해야 합니다.

## 6. 자주 만나는 오류와 복구 방법은?
- `ModuleNotFoundError: No module named 'yaml'` → PyYAML 미설치 상태, 2번 항목 참고.
- `FileNotFoundError` (metrics/report) → 로그나 메트릭 파일이 아직 생성되지 않은 경우이므로 `src.run` 또는 `src.metrics` 순서를 확인하세요.
- `RuntimeError: LM Studio request failed after retries` → LLM 엔드포인트 연결 문제. `--dry-run`으로 파이프라인만 확인하거나, `src/agents/llm_wrapper.py`의 `base_url`과 포트를 재확인하세요.

## 7. 주요 CLI 플래그 요약

| 커맨드 | 옵션 | 설명 |
| --- | --- | --- |
| `python -m src.run` | `--config` | YAML/JSON config 경로(필수) |
|  | `--seed` | RNG 시드 override |
|  | `--max-turns` | 최대 턴 수 제한 |
|  | `--dry-run` | 결정적 응답으로 시뮬레이션 (LLM 호출 X) |
| `python -m src.metrics` | `--config` | 실험 config (필수) |
|  | `--log` | 로그 경로 재정의 |
|  | `--out` | metrics 출력 경로 재정의 |
|  | `--rules` | 평가 규칙 JSON override |
| `python -m src.report` | `--config` | 실험 config (필수) |
|  | `--metrics` | metrics 입력 경로 재정의 |
|  | `--out` | SUMMARY/JSON 출력 경로 |
|  | `--format` | `md` / `json` / `both` |

## 8. 플랫폼/경로 팁
- **WSL/리눅스**: 상대 경로는 config 파일이 위치한 폴더 기준으로 해석되므로, 실험별 config를 `experiments/<name>/`에 두고 `results/<name>/`를 같이 두면 편합니다.
- **Windows PowerShell**: 스크립트 실행 시 `python` 대신 `.venv\Scripts\python.exe`를 명시해야 할 수 있습니다. 경로 구분자는 `\` 대신 `/`을 사용해도 동작합니다.
- **Mac/Linux 가상환경**: `. ~/.venv/bin/activate` 후 CLI를 호출하면 `src.*` 모듈을 찾지 못하는 문제를 줄일 수 있습니다.

## TODO
- [ ] FAQ에 예시 로그/메트릭 파일 링크 추가
- [ ] `src.preprocess` 단계가 준비되면 관련 항목 업데이트
