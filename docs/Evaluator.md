# Evaluator Spec

## 목적
- 실험 로그(`events.jsonl`)를 순차적으로 읽어 협력 지표를 계산하고 `metrics.json`으로 출력한다.
- CLI에서 `python -m src.metrics --config ...` 형태로 호출하며, 필요 시 `--log`·`--out` 옵션으로 경로를 재정의한다.
- 계산된 지표는 Phase 4 리포트(`src/report.py`) 작성의 입력으로 사용된다.

## 평가 규칙
- `EvaluationRules` 데이터 클래스는 판정 집합을 제공한다.
  - `cooperative_decisions`: 기본값 `{"join", "cooperate", "contribute", "support", "assist"}`.
  - `betrayal_decisions`: 기본값 `{"defect", "betray", "steal", "sabotage"}`.
  - `resource_key`: 기본 자원 `"stone"`으로 기여량 산출에 활용.
- 규칙은 CLI `--rules` 인자로 JSON 파일을 전달해 오버라이드할 수 있다.

## 지표 정의
> 세부 이론적 정의와 출처는 `docs/Evaluator_MetricsTheory.md` 참조.

- **협력 비율**: 협력 판정(decision ∈ cooperative) 횟수 ÷ 전체 로그 행 수.
- **평균 기여량**: 턴 순서대로 자원 스냅샷을 비교했을 때 `resource_key` 감소분(기여량) 평균. 첫 기록은 기준치로 간주한다.
- **회복 시간**: 배신(decision ∈ betrayal) 이후 같은 에이전트가 협력 판정을 받을 때까지의 턴 차 평균. 회복 사례가 없으면 `null`.
- **Gini 계수**: 에이전트별 누적 기여량 분포의 불평등도. 모든 기여량이 0이면 0으로 설정한다.
- **대화량 편중도**: 에이전트별 메시지 수의 Shannon entropy. 참여자 수가 1명이면 0으로 설정한다.
- **메타데이터**: 총 턴 수, 에이전트 목록, Dry-run 여부, 로그 경로 등을 함께 기록한다.
- 로그는 턴 순서대로 처리되며, 순서가 어긋난 경우 내부적으로 정렬을 보정한 뒤 지표를 계산한다.

## 인터페이스
```python
@dataclass
class EvaluationRules:
    cooperative_decisions: set[str]
    betrayal_decisions: set[str]
    resource_key: str

class Evaluator:
    def __init__(self, rules: EvaluationRules) -> None: ...
    def evaluate(self, log_path: Path) -> MetricsResult: ...
    def save(self, metrics: MetricsResult, out_path: Path) -> None: ...
```
- `MetricsResult`는 위 지표와 메타데이터, 에이전트별 기여량/발화량을 포함한다.

## 파이프라인 연계
- TurnManager 실행 후 생성된 JSONL 로그를 대상으로 사후 분석 모드로 호출한다.
- `src/report.py`는 `MetricsResult`를 받아 `SUMMARY.md`와 보조 표(`results/<exp>/report.json`)를 생성한다.
- CLI 서브커맨드:
  - `python -m src.metrics --config experiments/<exp>/config.yaml`
  - `python -m src.report --config experiments/<exp>/config.yaml`

## 검증
- 샘플 로그(`results/vow-baseline/events.sample.jsonl`)를 통해 계산 결과를 단위 테스트한다 (`tests/test_metrics.py`, `tests/test_report.py`).
- Phase 4 작업 후 계산 결과와 실행 명령을 `phases/phase-04/log.md`에 기록한다.
