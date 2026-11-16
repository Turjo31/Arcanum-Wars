"""Heuristic and baseline study: basic vs smart evaluation, Greedy and Random baselines.
Usage: python experiments/heuristic_experiment.py [games_per_row]"""
from _common import *

G = games_arg(100)
PAIRS = [("AlphaBetaPlus:6", "AlphaBeta:6"), ("AlphaBeta:6", "Greedy"), ("AlphaBetaPlus:6", "Greedy"),
         ("AlphaBeta:6", "Random"), ("AlphaBetaPlus:6", "Random"), ("Greedy", "Random"),
         ("AlphaBeta:6", "MCTS:200"), ("AlphaBetaPlus:6", "MCTS:200")]
rows = []
for a, b in PAIRS:
    w1, w2, d = head_to_head(a, b, G)
    print(f"{a:16s} vs {b:16s} {w1:3d} - {w2:3d}  draws {d}")
    rows.append([a, b, w1, w2, d])
save_csv("heuristic_experiment.csv", ["first", "second", "first wins", "second wins", "draws"], rows)
