# VoW Long Run Tales Experiment

- **Purpose**: replay the 60일 섬 시나리오 with the beefed-up 페르소나 to see whether 다른 시드와 로그가 서사적으로 어떻게 변하는지 비교하기 위한 더미.
- **Config**: `experiments/vow-long-run-tales/config.yaml` (seed 4044, 동일 shock 구조, log/output은 `results/vow-long-run-tales/` 하위에 기록).
- **How to run**:
  ```bash
  python3 -m src.run --config experiments/vow-long-run-tales/config.yaml --progress
  python3 -m src.metrics --config experiments/vow-long-run-tales/config.yaml --log experiments/vow-long-run-tales/results/vow-long-run-tales/events.jsonl --out experiments/vow-long-run-tales/results/vow-long-run-tales/metrics.json
  python3 -m src.report --config experiments/vow-long-run-tales/config.yaml --metrics experiments/vow-long-run-tales/results/vow-long-run-tales/metrics.json --out experiments/vow-long-run-tales/results/vow-long-run-tales/SUMMARY.md --format md
  ```
