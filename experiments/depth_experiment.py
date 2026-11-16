"""Search cost study: nodes searched by depth for Minimax, Alpha-Beta and ordered Alpha-Beta+,
and playing strength of Alpha-Beta by depth. Usage: python experiments/depth_experiment.py [games_per_row]"""
from _common import *
from ai import battle
from ai.battle import analyze, evaluate, evaluate2
from ai.teams import new_state

G = games_arg(60)
rn = random.Random(7)
states = [new_state(rn) for _ in range(40)]
rows = []
print(f"{'depth':>5} {'minimax':>10} {'alpha-beta':>11} {'ab + order':>11}   (average nodes per decision)")
for depth in range(1, 9):
    out = []
    for kw in (dict(prune=False), dict(prune=True), dict(prune=True, order=True, h=evaluate2)):
        total = 0
        for s in states:
            total += analyze(s, depth, **kw)[2]
        out.append(total / len(states))
    print(f"{depth:5d} {out[0]:10.0f} {out[1]:11.0f} {out[2]:11.0f}")
    rows.append([depth] + out)
save_csv("depth_nodes.csv", ["depth", "minimax nodes", "alphabeta nodes", "ordered alphabeta nodes"], rows)

print("\nPlaying strength by depth (vs Greedy):")
srows = []
for depth in (1, 2, 3, 4, 6):
    w1, w2, d = head_to_head(f"AlphaBeta:{depth}", "Greedy", G)
    print(f"  Alpha-Beta d{depth} vs Greedy: {w1} - {w2}  draws {d}")
    srows.append([depth, w1, w2, d])
save_csv("depth_strength.csv", ["depth", "wins", "losses", "draws"], srows)

try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(7, 4))
    for i, name in enumerate(["Minimax", "Alpha-Beta", "Alpha-Beta + ordering"]):
        plt.plot([r[0] for r in rows], [r[i + 1] for r in rows], marker="o", label=name)
    plt.yscale("log"); plt.xlabel("Search depth (plies)"); plt.ylabel("Nodes per decision"); plt.legend(); plt.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(RESULTS / "depth_nodes.png"); print("saved", RESULTS / "depth_nodes.png")
except ImportError:
    print("matplotlib not installed: skipped chart")
