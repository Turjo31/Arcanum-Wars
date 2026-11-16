"""MCTS study: smart vs random playouts, simulation budget, exploration constant.
Usage: python experiments/mcts_experiment.py [games_per_row]"""
from _common import *
from ai.mcts import mcts
from ai.battle import best

G = games_arg(100)
rows = []


def play_callables(f1, f2, games, seed=1):
    rn = random.Random(seed); w1 = w2 = d = 0
    for _ in range(max(1, games // 4)):
        A, B = random_teams(rn)
        for mine, theirs in ((A, B), (B, A)):
            for first in (0, 1):
                s = make_state(mine, theirs, first)
                for _ in range(60):
                    if winner(s) is not None: break
                    s = apply(s, (f1, f2)[s[2]](s))
                w = winner(s)
                if w == 0: w1 += 1
                elif w == 1: w2 += 1
                else: d += 1
    return w1, w2, d


smart = lambda s: mcts(s, 200, 1.4, True)
plain = lambda s: mcts(s, 200, 1.4, False)
ab6 = lambda s: best(s, 6, True)
tests = [("smart vs random playouts (200 sims)", smart, plain),
         ("smart MCTS vs Alpha-Beta d6", smart, ab6),
         ("plain MCTS vs Alpha-Beta d6", plain, ab6)]
for it in (50, 1000):
    tests.append((f"smart {it} sims vs smart 200 sims", lambda s, it=it: mcts(s, it, 1.4, True), smart))
for c in (0.7, 2.0):
    tests.append((f"exploration c={c} vs c=1.4", lambda s, c=c: mcts(s, 200, c, True), smart))
for label, f1, f2 in tests:
    w1, w2, d = play_callables(f1, f2, G)
    print(f"{label:42s} {w1:3d} - {w2:3d}  draws {d}")
    rows.append([label, w1, w2, d])
save_csv("mcts_experiment.csv", ["match-up", "first wins", "second wins", "draws"], rows)
