VOW-ICD(Intensity × Duration) 시스템은 로컬 LLM 기반의 다중 에이전트 환경에서 외부 충격의 강도와 지속시간을 설계 변수로 다루어 협력 동역학을 정량 분석하기 위한 통합 아키텍처다. 에이전트 계층은 메시지 채널(발화)과 행동 채널(자원 기여)을 분리 수집하고, 시나리오 엔진은 calibration–autonomy–shock–negotiation–recovery의 5단계를 관리한다. 충격 매트릭스는 soft/baseline/double/extended 변형으로 강도×지속시간을 교차 조합하며, 지표 엔진은 cooperation_rate, average_recovery_time, post‑shock trust, message_action_mismatch, avg_contribution을 산출한다. 이벤트는 events.jsonl로 축적되고 metrics.json/run_summary.csv로 요약된다.

+-------------------+     +-------------------+     +---------------------+
| Agent Layer       | --> | Scenario Engine   | --> | Shock Matrix (I×D)  |
| (10 personas)     |     | (5 Phases)        |     | soft/baseline/      |
| Message | Action  |     |                   |     | double/extended     |
+-------------------+     +-------------------+     +---------------------+
          |                            |                        |
          |                            v                        v
          |                  +-------------------+     +-------------------+
          |                  | Consistency Opt.  |     | Event Logger      |
          |                  | (msg–act penalties)|    | events.jsonl      |
          |                  +-------------------+     +-------------------+
          v
+--------------------+       metrics.json         +-----------------------+
| Metrics Engine     |  <-----------------------  | Archive & Reports     |
| cooperation_rate   |                            | run_summary.csv       |
| average_recovery…  |  ----------------------->  | figures / tables      |
| post‑shock trust   |    summaries, plots        | analysis_summary.md   |
| message_action_…   |                            +-----------------------+
| avg_contribution   |
+--------------------+

그림 1. VOW‑ICD 시스템 개요
Fig. 1. Overview of the VOW‑ICD System

Time --->

[Calibration][Autonomy][ Shock ] [ Negotiation ] [     Recovery     ]
            |            | I×D   |  alignment   |
            |            |window |  penalties   |

그림 2. 시나리오·충격 타임라인(개념)
Fig. 2. Scenario and Shock Timeline (Concept)

표 1. Shock 설계 매트릭스(강도×지속시간)
Table 1. Shock Design Matrix (Intensity × Duration)
