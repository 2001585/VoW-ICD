# Repository Guidelines

## Project Structure & Module Organization
- `docs/`: Houses drafts and specs. Keep PDFs as `vow-*.pdf` (e.g., `vow-draft-experiments.pdf`).
- `src/`: Production code, scripts, and optional `src/notebooks/` for exploratory work. Group related modules under subpackages.
- `experiments/`: One folder per study (e.g., `experiments/vow-baseline/`). Store configs, notes, and env locks.
- `results/`: Capture metrics, plots, and logs per experiment (mirrors `experiments/` naming).
- `tests/`: Automated suites mirroring `src/` structure.
- `data/`: Local-only datasets (`data/raw/`, `data/processed/`). Directory is git-ignored.

## Build, Test & Development Commands
- WSL prerequisites: `sudo apt update && sudo apt install -y python3 python3-venv python3-pip build-essential git`.
- Virtual environment: `python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip`.
- Dependencies: `pip install -r requirements.txt`.
- Tests: `pytest -q` once `pytest` is listed in requirements.
- Optional tooling: `black .` for format, `ruff .` for lint.

## Coding Style & Naming Conventions
- Filenames: ASCII, kebab-case (`vow-data-loader.py`, `experiments/vow-baseline/config.yaml`).
- Python: PEP 8, 4-space indents, 88-character lines.
- Notebooks: keep lightweight; move reusable code to `src/`.

## Testing Guidelines
- Framework of record: Pytest. Place tests in `tests/` with names like `test_preprocess.py` mirroring `src/preprocess.py`.
- Target ≥70% coverage as codebase stabilizes; document manual verification steps in experiment README files.

## Commit & Pull Request Guidelines
- Messages follow Conventional Commits (`docs:`, `feat:`, `fix:`, `refactor:`, `chore:`). Keep the summary ≤72 characters.
- PRs include: purpose, change log, linked issue (if any), validation evidence (tests, metrics, screenshots).

## Experiment Workflow (Village of Words)
- Ground new studies in `docs/vow-draft-experiments.pdf` and `experiments/vow-baseline/README.md`.
- Clone the baseline folder for new work until `scripts/mk_experiment.sh <name>` exists.
- Record seeds and commands (`pip freeze > experiments/<name>/requirements.lock`).
- Keep outputs in `results/<name>/` and add a short `SUMMARY.md`.

## Security & Data Handling
- Never commit raw participant data or credentials. Keep secrets in environment variables or local config files listed in `.gitignore`.
- Large assets (>50 MB) should live in external storage with links/checksums.

## Process & Checklists
- Follow the phased workflow in `docs/PHASE.md`; avoid off-plan work.
- Update the Phase checklist and `AGENTS.md` notes immediately after each milestone.
- 새 대화를 시작할 때 `AGENTS.md`, `docs/*.md`, `docs/PHASE.md`, `phases/` 로그를 먼저 확인한다.
- 스펙 문서(`docs/AgentManager.md` 등)를 구현 변화에 맞춰 갱신한다.
- 다른 방법을 사용했다면 사유를 기록하고 기본 계획으로 되돌릴지 확인한다.
- Phase 진행 현황: Phase 1 완료 (환경 점검), Phase 2 완료 (Agent core), Phase 3 완료 (Turn/CLI), Phase 4 완료 (Metrics/Report), Phase 5 완료 (실험 템플릿 정리·CLI FAQ 완성·성능 최적화·커버리지 측정·회고 작성). 로그: `phases/phase-01/log.md`, `phases/phase-02/log.md`, `phases/phase-03/log.md`, `phases/phase-04/log.md`; Phase 5 산출물: `docs/experiment-template.md`, `docs/CLI_FAQ.md`, `phases/phase-05/notes.md`, `phases/phase-05/log.md`, `phases/phase-05/retrospective.md`, `results/vow-baseline/coverage.txt`. PyPI 제한 시 `python3 -m unittest`로 대체 테스트.
