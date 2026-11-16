"""Agent registry. An agent is a spec string such as "AlphaBeta:6" or "MCTS:200"."""
import random
from ai.battle import actions, analyze, evaluate, evaluate2
from ai.mcts import mcts_info, greedy_move

SPECS = ["AlphaBeta:2", "AlphaBeta:4", "AlphaBeta:6", "AlphaBetaPlus:4", "AlphaBetaPlus:6",
         "MCTS:50", "MCTS:200", "MCTS:1000", "Greedy", "Random"]


def parse(spec):
    kind, _, lvl = spec.partition(":")
    return kind, (int(lvl) if lvl else None)


def label(spec):
    k, l = parse(spec)
    return {"AlphaBeta": f"Alpha-Beta d{l or 6}", "AlphaBetaPlus": f"Alpha-Beta+ d{l or 6}",
            "Minimax": f"Minimax d{l or 6}", "MCTS": f"MCTS {l or 200}",
            "Greedy": "Greedy", "Random": "Random"}[k]


def think(spec, s):
    """Return (action, info). info feeds the thinking panel in the battle screen."""
    kind, lvl = parse(spec)
    if kind in ("AlphaBeta", "AlphaBetaPlus", "Minimax"):
        plus = kind == "AlphaBetaPlus"
        a, sc, nodes, pruned = analyze(s, lvl or 6, evaluate2 if plus else evaluate, order=plus, prune=kind != "Minimax")
        return a, {"kind": "ab", "scores": sc, "nodes": nodes, "pruned": pruned}
    if kind == "MCTS":
        iters = lvl or 200
        a, st = mcts_info(s, iters)
        return a, {"kind": "mcts", "stats": st, "iters": iters}
    if kind == "Greedy":
        return greedy_move(s), {"kind": "rule"}
    return random.choice(actions(s)), {"kind": "rand"}


def act(spec, s):
    return think(spec, s)[0]
