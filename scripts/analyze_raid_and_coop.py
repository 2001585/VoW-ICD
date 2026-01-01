from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

COOP_DECISIONS = {"join","cooperate","contribute","support","assist","help"}


def load_entries(path: Path):
    out = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def raid_rates(logs, turn=41, keyword="raid"):
    per_agent = defaultdict(list)
    for log in logs:
        entries = load_entries(Path(log))
        filtered = [e for e in entries if int(e.get('turn',-1))==turn]
        for e in filtered:
            agent = str(e.get('agent',''))
            decision = str(e.get('decision','')).lower()
            per_agent[agent].append(1 if keyword in decision else 0)
    stats = {a:{'mean': float(np.mean(v)), 'n': len(v)} for a,v in per_agent.items()}
    return stats


def coop_trust_series(logs, max_turns=100):
    coop_sum = np.zeros(max_turns)
    coop_cnt = np.zeros(max_turns)
    trust_sum = np.zeros(max_turns)
    trust_cnt = np.zeros(max_turns)
    for log in logs:
        for e in load_entries(Path(log)):
            t = int(e.get('turn',0))
            if t<1 or t>max_turns:
                continue
            decision = str(e.get('decision','')).lower()
            coop_sum[t-1] += 1 if decision in COOP_DECISIONS else 0
            coop_cnt[t-1] += 1
            trust = e.get('trust_score')
            if isinstance(trust,(int,float)):
                trust_sum[t-1] += trust
                trust_cnt[t-1] += 1
    coop_rate = np.divide(coop_sum, coop_cnt, out=np.zeros_like(coop_sum), where=coop_cnt>0)
    mean_trust = np.divide(trust_sum, trust_cnt, out=np.zeros_like(trust_sum), where=trust_cnt>0)
    return coop_rate, mean_trust


def plot_raid(stats, out_path):
    agents = sorted(stats.keys())
    means = [stats[a]['mean'] for a in agents]
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(agents, means, color="#C00000", edgecolor='black')
    ax.set_ylim(0,1)
    ax.set_ylabel('Raid selection rate (turn 41)')
    ax.set_title('Night Raid Opt-in by Persona (across seeds)')
    for i,m in enumerate(means):
        ax.text(i, m+0.02, f"{m:.2f}", ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor='white')


def plot_coop_trust(coop, trust, out_path):
    turns = np.arange(1, len(coop)+1)
    fig, ax1 = plt.subplots(figsize=(10,4.5))
    ax1.plot(turns, coop, color='#4472C4', label='Cooperation rate')
    ax1.set_ylabel('Coop rate', color='#4472C4')
    ax1.set_ylim(0,1)
    ax2 = ax1.twinx()
    ax2.plot(turns, trust, color='#ED7D31', label='Mean trust')
    ax2.set_ylabel('Mean trust', color='#ED7D31')
    ax2.set_ylim(0,1)
    ax1.set_xlabel('Turn')
    ax1.set_title('Cooperation & Trust over Time (mean across seeds)')
    lines, labels = [], []
    for ax in (ax1, ax2):
        l, lab = ax.get_legend_handles_labels()
        lines += l; labels += lab
    ax1.legend(lines, labels, loc='upper right')
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor='white')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--logs', nargs='+', required=True, help='List of events.jsonl files')
    ap.add_argument('--max-turns', type=int, default=100)
    ap.add_argument('--outdir', default='results/vow-long-run-10a')
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    stats = raid_rates(args.logs, turn=41)
    coop, trust = coop_trust_series(args.logs, max_turns=args.max_turns)

    plot_raid(stats, outdir/'raid_rate_bar.png')
    plot_coop_trust(coop, trust, outdir/'coop_trust_series.png')

    summary = {
        'raid_rate': stats,
        'coop_mean': float(np.mean(coop[0:args.max_turns])) if len(coop)>0 else 0,
        'trust_mean': float(np.mean(trust[0:args.max_turns])) if len(trust)>0 else 0,
        'logs': args.logs,
    }
    (outdir/'analysis_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
