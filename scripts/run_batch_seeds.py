from __future__ import annotations
import argparse, subprocess, tempfile, shutil, yaml, json
from pathlib import Path


def run_seed(base_config: Path, seed: int, max_turns: int | None = None) -> Path:
    with base_config.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    base_dir = base_config.parent.resolve()
    # mutate paths per seed
    exp = cfg.get('experiment', {})
    exp['seed'] = seed
    def with_suffix(path: str, suffix: str) -> str:
        p = (base_dir / path).resolve()
        stem = p.stem
        new = f"{stem}_{suffix}{p.suffix}"
        return str(p.with_name(new))
    for key in ['log_path','metrics_path','summary_path']:
        if key in exp:
            exp[key] = with_suffix(exp[key], f"seed{seed}")
    cfg['experiment'] = exp
    if max_turns is not None:
        exp['max_turns'] = max_turns
    tmp = Path(tempfile.mkdtemp()) / f"config_seed{seed}.yaml"
    with tmp.open('w', encoding='utf-8') as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    try:
        subprocess.run([
            '.venv/bin/python','-m','src.run',
            '--config', str(tmp),
            '--progress'
        ], check=True)
    finally:
        shutil.rmtree(tmp.parent)
    return Path(exp['log_path']).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--seeds', nargs='+', type=int, required=True)
    ap.add_argument('--max-turns', type=int)
    args = ap.parse_args()
    base_config = Path(args.config)
    logs = []
    for s in args.seeds:
        print(f"\n=== Running seed {s} ===", flush=True)
        log_path = run_seed(base_config, s, args.max_turns)
        logs.append(str(log_path))
    print("\nBatch complete. Logs:")
    print(json.dumps(logs, indent=2))

if __name__ == '__main__':
    main()
