"""Post-process logs to simulate targeted raid transfers at a given turn.

- Victim selection: each raider steals `reward` wood (default 1.5) from the richest victim by metric
  (total=stone+wood or wood-only). Victims chosen among non-raiders; if none, among all others.
- Transfer capped at victim's available wood (no negatives).
- Outputs per-agent delta and summary.

Usage:
  python scripts/simulate_targeted_raid.py --log results/vow-long-run-10a/events_seed1001.jsonl --turn 41 --reward 1.5 --metric total
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import defaultdict


def load_entries(log_path: Path):
    entries = []
    with log_path.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def state_before_turn(entries, turn):
    # return latest resources before or at given turn for each agent
    state = {}
    for e in entries:
        t = int(e.get('turn',0))
        if t > turn:
            continue
        agent = e.get('agent')
        res = e.get('resources', {})
        state[agent] = {'stone': float(res.get('stone',0.0)), 'wood': float(res.get('wood',0.0))}
    return state


def decisions_at_turn(entries, turn):
    dec = {}
    for e in entries:
        if int(e.get('turn',0)) == turn:
            dec[e.get('agent')] = str(e.get('decision','')).lower()
    return dec


def simulate(log_path: Path, turn: int, reward: float, metric: str):
    entries = load_entries(log_path)
    state = state_before_turn(entries, turn)
    decisions = decisions_at_turn(entries, turn)
    agents = sorted(state.keys())
    raiders = [a for a,d in decisions.items() if 'raid' in d]
    non_raiders = [a for a in agents if a not in raiders]

    deltas = {a:{'stone':0.0,'wood':0.0} for a in agents}

    def metric_val(agent):
        s,w = state[agent]['stone'], state[agent]['wood']
        return w if metric=='wood' else s+w

    victims_pool = non_raiders if non_raiders else [a for a in agents]

    for r in raiders:
        # choose richest victim excluding self if possible
        candidates = [a for a in victims_pool if a != r]
        if not candidates:
            continue
        victim = max(candidates, key=metric_val)
        take = min(reward, state[victim]['wood'] + deltas[victim]['wood'])  # deltas negative
        # apply transfer on wood
        deltas[r]['wood'] += take
        deltas[victim]['wood'] -= take

    results = []
    for a in agents:
        s0, w0 = state[a]['stone'], state[a]['wood']
        ds, dw = deltas[a]['stone'], deltas[a]['wood']
        results.append({
            'agent': a,
            'decision': decisions.get(a,''),
            'stone_before': s0,
            'wood_before': w0,
            'delta_stone': ds,
            'delta_wood': dw,
            'stone_after': s0+ds,
            'wood_after': w0+dw,
        })
    # summary
    most_gain = max(results, key=lambda r: r['delta_wood']) if results else None
    most_loss = min(results, key=lambda r: r['delta_wood']) if results else None
    summary = {
        'log': str(log_path),
        'turn': turn,
        'reward': reward,
        'metric': metric,
        'raiders': raiders,
        'non_raiders': non_raiders,
        'most_gain': most_gain,
        'most_loss': most_loss,
    }
    return {'agents': results, 'summary': summary}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', required=True)
    ap.add_argument('--turn', type=int, default=41)
    ap.add_argument('--reward', type=float, default=1.5)
    ap.add_argument('--metric', choices=['total','wood'], default='total')
    ap.add_argument('--out')
    args = ap.parse_args()
    res = simulate(Path(args.log), args.turn, args.reward, args.metric)
    text = json.dumps(res, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
    print(text)

if __name__ == '__main__':
    main()
