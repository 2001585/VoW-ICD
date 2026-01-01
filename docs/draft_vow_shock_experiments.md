# Village of Words Shock Experiment Draft

## 1. Introduction (to expand)
- Motivation: quantify how intentional resource shocks impact cooperation/trust in multi-agent language-play environments.
- Gap: prior Generative Agents focus on emergent behavior without controlled shock intensity/duration manipulations.
- Contribution: compare three shock intensities (soft/baseline/double) plus prolonged duration, using persona-rich LM agents with message/action tracking.

## 2. Methods
### 2.1 Configuration Overview
- Agents: 10 personas (coordinator, supplier, analyst, provocateur, etc.) mapped to LM Studio endpoints (meta-llama-3-8b-instruct).
- Scenario phases: calibration (1–10), autonomy (11–22), shock block (23–24 or 23–25), negotiation (25–36), recovery (37–50).
- Metrics pipeline (`src/metrics.py`): cooperation rate, average recovery time, Gini of contributions, message/action mismatch, shock-window aggregates (pre/shock/post/extended).
- Automation: `scripts/run_series.py --variant <id> --runs <n>` for repeated trials; outputs archived in `results/vow-cultural-drift/archives/run-*/` and summarized in `run_summary.csv`.

### 2.2 Shock Variants
| ID | Description | Schedule |
|----|-------------|----------|
| `soft-wave` | −2 then −1 stone | turns 23–24 |
| `baseline-single` | −3 stone ×2 | turns 23–24 |
| `double-wave` | −4 then −2 stone | turns 23–24 |
| `extended-wave` | −3 stone ×3 | turns 23–25 |

## 3. Results (summary)
- Aggregated metrics: see `results/vow-cultural-drift/analysis_summary.md` and plots (`shock_comparison_bw.png`, `shock_comparison_bar_bw.png`).
- Cooperation: mean rates {soft 0.703, baseline 0.709, extended 0.716, double 0.627} with soft/extended > double.
- Recovery duration: double shock slows recovery (~3 turns), prolonged shock adds +0.2 turn vs baseline, soft shock fastest (~1.46 turns).
- Message/action mismatch: increases with shock severity (0.001 → 0.003 → 0.008 → 0.010).
- Trust: soft-wave highest post-shock+10 mean trust (0.562), prolonged holds 0.551, double lowest (~0.375). 
- Leadership: Agent G dominates contributions; double shock occasionally shifts top contributor to B (1/3 runs) indicating leadership redistribution when shocks are harsher.

## 4. Discussion Points (outline)
- Intensity vs duration: compare double-wave vs extended-wave to highlight that longer shocks degrade cooperation less than stronger ones but still raise mismatch/trust lag.
- Persona robustness: note stability of Agent G (artisan) across conditions; discuss design implications.
- Message-action mismatch as diagnostic for “performative cooperation”.
- Limitations: single LM endpoint, fixed turn length, deterministic seeds.

## 5. Figures & Tables to Produce
- Fig. 1: Shock comparison line plot (already generated, path: `results/vow-cultural-drift/archives/shock_comparison_bw.png`).
- Fig. 2: Aggregated bar plot with error bars (`.../shock_comparison_bar_bw.png`).
- Table 1: Aggregated metrics (from `analysis_summary.md`).
- Optional Table: Top contributor frequency per variant (derive from `run_summary.csv`).

## 6. Next Steps
- Expand discussion text using bullet points above.
- Double-check reproducibility (list command invocations & seeds).
- Incorporate trust trajectories per agent (optional future figure).
