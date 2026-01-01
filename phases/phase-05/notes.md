# Phase 5 — Refactor & Performance Backlog

| Priority | Area | Issue / Opportunity | Notes | Status |
| --- | --- | --- | --- | --- |
| P0 | Config loading | `_load_text_config` duplicated in `src/metrics.py` and `src/report.py` while `src/run.py` has similar logic. | Extract shared loader (e.g., `src/utils/config.py`) to remove divergence and centralize PyYAML fallback handling. | ✅ Done (2025-10-31) |
| P1 | Logging I/O | `TurnManager._write_log_entry` opens/closes the log file for every agent turn (`with self.log_path.open("a")`). | Switch to buffered writer (open once per run) or use `asyncio.StreamWriter` to cut file descriptor churn during long experiments. Requires lifecycle management. | ✅ Done (2025-10-31) |
| P1 | State snapshot costs | `TurnManager._write_log_entry` calls `agent_manager.snapshot()` for each agent turn. | Capture snapshot once per turn or expose `AgentState` directly to avoid redundant JSON serialization. | ✅ Done (2025-10-31) |
| P1 | Metrics performance | `Evaluator._compute_metrics` sorts the entire log each call. | Accept order-preserving iterator; ensure TurnManager writes chronological logs so sorting can be skipped. | ✅ Done (2025-10-31) |
| P2 | CLI churn | Metrics/report CLIs recompute derived paths on every call; repeated `Path.resolve()` and `mkdir`. | Cache base directories and add helper for experiment-relative paths. Minor but reduces overhead in batch evaluations. | ✅ Done (2025-10-31) |
| P2 | Test coverage | Current `python -m unittest` only covers happy paths. | Trace 기반 커버리지 측정 완료(2025-10-31); `src/agents/llm_wrapper.py` 추가 테스트로 86% 달성. 향후 coverage.py 도구 도입 시 자동화 계획. | ✅ Done |
| P3 | Dry-run UX | `DryRunWrapper` cycles static responses and writes minimal metadata. | Expose CLI toggle to vary scripted behaviours for regression suites; low risk but improves realism. | ⏳ Pending |
| P3 | Tooling | 커버리지 리포트를 coverage.py/HTML로 자동화. | 추후 네트워크 허용 시 coverage.py 설치 후 CI 또는 스크립트 통합 검토. | ⏳ Pending |

*Legend — Priority:* P0 (must fix before long runs), P1 (high value), P2 (nice to have soon), P3 (stretch). Status icons: ✅ 완료, 🔄 진행 중, ⏳ 대기.
