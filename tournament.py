import time, random, itertools
import battle
from battle import apply, actions, winner, best
from mcts import mcts
from teams import random_teams, make_state

PLAYERS = {
    "Minimax": lambda s: best(s, 6, False),
    "AlphaBeta": lambda s: best(s, 6, True),
    "MCTS": lambda s: mcts(s, 200),
    "Random": lambda s: random.choice(actions(s)),
}

def play(p, s, cap=60):
    turns, times = 0, [[], []]
    while winner(s) is None and turns < cap:
        t = s[2]
        t0 = time.perf_counter()
        a = p[t](s)
        times[t].append(time.perf_counter() - t0)
        s = apply(s, a)
        turns += 1
    return winner(s), turns, times

def match(n1, n2, games=20, seed=0):
    rn = random.Random(seed)
    r = {"w1": 0, "w2": 0, "draw": 0, "turns": 0, "t1": [], "t2": []}
    for _ in range(games // 4):
        A, B = random_teams(rn)
        for mine, theirs in ((A, B), (B, A)):
            for first in (0, 1):
                w, turns, times = play((PLAYERS[n1], PLAYERS[n2]), make_state(mine, theirs, first))
                r["turns"] += turns; r["t1"] += times[0]; r["t2"] += times[1]
                if w is None: r["draw"] += 1
                elif w == 0: r["w1"] += 1
                else: r["w2"] += 1
    return r

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    labels, w1, w2, dr = [], [], [], []
    avg = lambda l: 1000 * sum(l) / max(1, len(l))
    for n1, n2 in itertools.combinations(PLAYERS, 2):
        battle.STATS[:] = [0, 0]
        r = match(n1, n2)
        print(f"{n1} vs {n2}: {r['w1']}-{r['w2']} draws {r['draw']} | avg turns {r['turns']/20:.1f} | "
              f"ms/move {avg(r['t1']):.1f} vs {avg(r['t2']):.1f} | nodes {battle.STATS[0]} pruned {battle.STATS[1]}")
        labels.append(f"{n1}\nvs {n2}")
        w1.append(r["w1"]); w2.append(r["w2"]); dr.append(r["draw"])
    x = range(len(labels))
    plt.figure(figsize=(12, 5))
    plt.bar([i - 0.27 for i in x], w1, 0.27, label="First algorithm wins")
    plt.bar(list(x), w2, 0.27, label="Second algorithm wins")
    plt.bar([i + 0.27 for i in x], dr, 0.27, label="Draws")
    plt.xticks(list(x), labels); plt.ylabel("Games (of 20)"); plt.legend()
    plt.savefig("tournament.png")