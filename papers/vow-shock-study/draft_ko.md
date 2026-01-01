# 1. 서론
대규모 언어 모델(Large Language Model, LLM)은 언어 이해와 생성 능력을 기반으로 다양한 자율 시뮬레이션 환경에서 활용되고 있다. 특히 다수의 LLM 기반 에이전트를 하나의 사회 시스템처럼 구성하여 규범 형성, 정보 확산, 협력 구조 등을 관찰하는 연구가 빠르게 증가하고 있다[1][2][3]. 최근에는 장기 기억 구조와 반영(reflection) 기능을 갖춘 에이전트를 통해 일상적 상호작용과 집단 이벤트를 시뮬레이션하는 실험이 보고되었으며[1], 공공재 기반 환경에서 협력의 붕괴 현상을 탐색하거나[2], 실물 경제 충격을 재현해 회복 전략을 분석하는 시도도 등장하고 있다[3].

이러한 연구들은 다수 에이전트의 상호작용 속에서 나타나는 집단적 사회 현상을 관찰하는 데 중점을 두며 협력과 규범의 자발적 형성, 다수 의견에 대한 동조, 일관된 기억 유지 등을 다루어 왔다[4][5][6]. 그러나 이들 접근은 대부분 특정 사건(예: 충격) 이후의 에이전트 반응을 현상적으로 기술하는 데 머무르며, 충격의 강도(intensity)와 지속시간(duration)을 실험 설계 변수로 다차원적으로 조합하여 협력의 붕괴와 회복을 정량적으로 비교한 사례는 확인되지 않았다.

또한 기존 연구들은 에이전트가 “협력하자”고 말하는 메시지와 실제 자원 기여 행동 사이의 불일치를 명확히 측정하지 않아, 언어적 약속이 실제 행동에 반영되는지를 평가하기 어렵다. 협력은 선언에 그치지 않고 실천을 동반해야 하며, LLM 에이전트 사회에서 언어와 행동의 괴리 여부를 정량적으로 재현 가능한 지표로 측정하는 작업은 아직까지 체계화되지 않았다.

이 연구는 위와 같은 공백을 해결하기 위해 다음의 목적을 가진다. 첫째, Village of Words(VOW) 시뮬레이션 환경을 기반으로 충격 강도와 지속시간을 교차 조합한 실험 시나리오를 설계하여 협력률(cooperation_rate), 평균 회복시간(average_recovery_time), 신뢰 변화(post-shock trust) 등을 정량적으로 비교한다. 둘째, 언어적 약속과 행동 간의 괴리를 측정하기 위해 메시지-행동 불일치율(message_action_mismatch)을 정의하고, 충격 속성 변화에 따른 불일치 양상의 변화를 분석한다. 셋째, 각 페르소나의 역할별 리더십 전환을 기여량 및 신뢰 지표 기반으로 추적한다. 마지막으로, 로컬 환경에서 실행 가능한 LLM(meta-llama-3-8b-instruct)을 활용함으로써 외부 API에 의존하지 않고 비용과 재현성의 장점을 확보한다[7].

이 연구의 기여는 충격을 설계 변수로 삼고, 협력 동역학을 수치 기반 지표로 해석할 수 있는 구조를 제시했다는 데 있다. 이를 통해 LLM 기반 에이전트 사회에서의 사회적 상호작용을 기술 중심이 아닌 실험 기반 계량 분석으로 전환하고자 한다.

# 2. 관련 연구
### 2.1 가상 사회 시뮬레이션과 충격 모델링의 공백
Generative Agents는 장기 기억과 일과 계획 구조를 갖춘 에이전트들이 자율적으로 일상을 구성하는 방식을 제시하였으나, 이벤트 충격은 대부분 사전 스크립트에 의해 고정된 형태로 처리되었다[1]. GovSim은 공공 자원 관리 실패를 모사하며 집단 행동의 변화 흐름을 관찰했지만, 외부 충격의 강도나 지속시간을 독립 변수로 조정하는 설계는 도입되지 않았다[2]. 또한 Shachi는 단일 세율 충격을 실험 요소로 포함했으나, 해당 변수의 반복 변화나 지속적 영향은 고려하지 않았다[3]. 이 논문은 동일한 페르소나 구성을 유지한 채 충격 강도와 지속시간을 교차 조합함으로써 이 공백을 보완하고자 한다.

### 2.2 사회적 동조와 언어-행동 괴리
LLM 기반 에이전트 집단이 다수 의견에 순응하거나 자율적으로 사회 규범을 형성하는 경향이 관찰되었다는 연구들이 보고되었다[4][5][6]. 그러나 이러한 연구들은 에이전트가 발화한 메시지와 실제 행동(예: 자원 기여) 간의 괴리를 측정하는 지표를 활용하지 않았기 때문에, 언어적 협력 선언이 실질적 협력으로 이어졌는지 여부를 판단하기 어렵다. 이 논문은 “협력하겠다”는 발화와 기여 행동의 일치 여부를 정량화하기 위해 메시지-행동 불일치율(message_action_mismatch)을 정의하며, 충격 강도 변화에 따라 불일치율이 증가하는 경향을 실험적으로 확인한다.

### 2.3 페르소나 기반 협상과 리더십 추적
기존의 다중 에이전트 협상 연구는 페르소나 별 자원 배분 전략을 분석하거나 역할 간 상호작용 양상을 정성적으로 기술하는 데 중점을 두었다[2][6]. 그러나 충격 이후 협력 구간에서 나타나는 리더십 전환이나 신뢰 회복을 정량적으로 추적한 사례는 드물다. 이 논문은 동일한 언어 모델로 구성된 에이전트 집단을 기반으로, 기여량(avg_contribution)과 post-shock trust 지표를 활용해 충격 전후 리더십의 변화를 계측할 수 있도록 실험 프레임을 구성하였다.


# 3. VOW‑ICD 시스템 아키텍처

### 3.1 시스템 구조
이 논문이 제안하는 VOW-ICD(Intensity × Duration) 시스템은 그림 1이 보여주듯이 외부 충격의 강도와 지속시간을 설계 변수로 다루어 협력 동역학을 정량 분석하기 위한 최소 구성의 아키텍처이다. 에이전트 계층은 메시지 채널(발화)과 행동 채널(자원 기여)을 분리해 수집하고, 시나리오 엔진은 calibration–autonomy–shock–negotiation–recovery로 이어지는 5단계의 흐름을 관리한다. Shock Matrix는 Shock window에 따라 강도×지속시간 조합(soft, baseline, double, extended)을 외부 이벤트로 삽입하며, 발생한 이벤트는 Event Logger로 기록된다. Consistency Optimizer는 메시지와 행동 간 불일치를 평가하고, Metrics Engine은 협력률(cooperation_rate), 평균 회복시간(average_recovery_time), shock 이후 신뢰(post_shock_trust), 메시지‑행동 불일치율(message_action_mismatch), 평균 기여량(avg_contribution) 등 핵심 지표를 계산한다. 계산 결과는 metrics.json과 run_summary.csv로 저장되며, Archive & Reports 모듈은 반복 실행 로그를 보관해 후속 분석과 보고서 작성을 지원한다.

### 3.2 시나리오와 충격 설계
실험은 20턴을 기본으로 하며 필요에 따라 30/40/50턴으로 확장된다. 초기에는 Calibration 단계에서 신뢰와 협력 규범을 형성하고, Autonomy 단계에서 제약을 완화하여 자율 행동을 관찰한다. Shock 단계에서 외생 충격을 투입하고, Negotiation 단계에서 메시지‑행동 정합성을 높이는 규칙을 적용해 진정성 있는 합의를 유도한다. Recovery 단계에서는 충격 이후의 회복과 안정화 과정을 추적한다. Shock의 강도와 지속시간은 soft/baseline/double/extended 네 가지 변형으로 조합되며, 각 변형의 시간창과 적용 방식은 [그림 2]와 [표 1]에 정리하였다.

표 1. Shock 설계 매트릭스(강도×지속시간)
Table 1. Shock Design Matrix (Intensity × Duration)

| Variant | Intensity (Δresource) | Duration (turns) | Injection (turn index) | Target (set)         | Alignment penalty | Notes                 |
|--------|------------------------|------------------|-------------------------|----------------------|-------------------|-----------------------|
| Soft   | stone −2               | 1                | 9                       | all except agent D   | off               | —                     |
| Baseline (single) | stone −3    | 1                | 9                       | all except agent D   | off               | —                     |
| Double (two waves) | stone −4    | 1 × 2            | 9 and 12                | all except agent D   | off               | window spacing ≈ 3    |
| Extended (continuous) | stone −3 | 3                | 9–11                    | all except agent D   | on                | continuous window     |

### 3.2 지표와 분석 절차
협력률은 턴별 협력 행동 비율의 평균으로 정의하고, 평균 회복시간은 Shock 창 종료 이후 정상화 임계치(전충격 평균의 90%)에 재도달하기까지의 평균 턴 수로 측정한다. post‑shock trust는 Shock 이후 10턴의 평균 신뢰로 요약하며, 메시지‑행동 불일치율은 “협력” 취지의 발화가 있었음에도 행동이 협력이 아닌 비율로 계산한다. 평균 기여량은 에이전트별/조건별 자원 기여의 평균이다. 조건별 비교는 평균과 표준편차를 기본으로 하고 반복 실행(≥3회) 간 변동을 함께 제시한다. 장기 러닝에서는 UNKNOWN 비율 임계치를 두어 결과의 신뢰성을 확보한다.

### 3.3 입증 결과
강도 효과를 확인하기 위해 변형 간 협력률과 평균 회복시간을 비교하였다. double 변형은 협력률이 가장 낮고(예: 0.627±0.030), 평균 회복시간이 가장 길어(예: 2.95턴) 충격 강도가 협력 붕괴 폭과 회복 지연을 동시에 키운다는 점을 보여준다. 반대로 soft 변형에서는 협력률이 높고(예: 0.703±0.047), 평균 회복시간이 가장 짧아(예: 1.46턴) 완만한 충격이 빠른 복원을 돕는 경향이 관찰되었다. 지속시간 효과에서는 extended 변형이 평균 회복시간이 다소 길지만(예: 1.93턴) post‑shock trust 평균이 높게 유지되는 양상을 보여 안정적 신뢰 복원이 가능함을 시사한다(예: 0.551). 

언어와 행동의 괴리는 충격이 강해질수록 증가했다. 메시지‑행동 불일치율은 soft에서 double로 갈수록 소폭 상승하여, 언어적 합의가 행동으로 곧바로 환류되지 않는 performative cooperation의 위험을 수치로 확인할 수 있었다. 리더십 측면에서는 평시와 완만한 충격에서는 소수 역할 중심의 기여가 유지되는 반면, 강한 충격(double)에서는 최고 기여자가 바뀌는 사례가 나타나 리더십 분산이 발생하였다. 이러한 결과는 [그림 2]의 시간 추세와 함께 해석될 때, 충격 설계가 협력의 붕괴‑회복 곡선뿐 아니라 역할 분배에도 영향을 준다는 점을 보여준다.

### 3.4 구현 및 재현성 메모
모든 에이전트는 로컬 LLM(meta‑llama‑3‑8b‑instruct)을 사용하여 모델 편차를 통제하였고, 동일 설정으로 각 조건을 반복 실행해 요약 파일(run_summary.csv)에 누적하였다. 실행 전 헬스체크와 진행 로그 옵션을 사용해 실패율을 낮추었고, 아카이브 경로를 고정해 실험 간 비교 가능성을 높였다. 그림과 표는 흑백 팔레트를 사용하고, 캡션은 한·영 병기로 표기한다.

# 4. 결론 및 향후 연구
이 연구는 VOW 환경에서 충격 강도와 지속시간이 협력·신뢰 회복에 미치는 영향을 정량적으로 분석하였다. 향후에는 (1) 60–100턴 장기 시나리오에서 2차 충격이나 외부 이벤트를 추가하고, (2) 서로 다른 모델(예: reasoning 특화 LLM vs. instruction 모델)을 혼합해 문화적 차이를 정량화하며, (3) 메시지-행동 불일치에 기반한 자동 개입 정책을 탐구할 계획이다.

# 5. 참고문헌
[1] Park, J. S., et al. Generative Agents: Interactive Simulacra of Human Behavior. arXiv:2304.03442, 2023.
[2] Piatti, G., et al. Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents. arXiv:2404.16698, 2024.
[3] Kuroki, T., et al. Shachi: An Agent-Based Simulation Evaluating Economic Policy on Real-World Data. arXiv:2501.03920, 2025.
[4] Zhong, H., et al. Disentangling the Drivers of LLM Social Conformity: An Uncertainty-Moderated Dual-Process Mechanism. arXiv:2508.14918, 2025.
[5] Zhu, X., et al. Conformity in Large Language Models. ACL 2025.
[6] Flint Ashery, A., et al. Emergent Social Conventions and Collective Bias in LLM Populations. Science Advances, 11(20), 2025.
[7] Meta. Meet Your New Assistant: Meta AI, Built With Llama 3. Meta Newsroom, 18 April 2024.
