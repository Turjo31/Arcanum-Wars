import time, random, itertools
import matplotlib.pyplot as plt
import battle
from battle import apply, actions, winner, best
from mcts import mcts

START = ((((100,20,5,"Fire"),(100,20,5,"Water")),
  ((100,20,5,"Earth"),(100,20,5,"Lightning"))), (0, 0), 0)

PLAYERS = {
    "Minimax": lambda s: best(s, 6, False),
    "AlphaBeta": lambda s: best(s, 6, True),
    "MCTS": lambda s: mcts(s, 200),
    "Random": lambda s: random.choice(actions(s)),
}

def play(p0, p1, cap=60):
    s, turns, times = START, 0, [[], []]
    while winner(s) is None and turns < cap:
        t = s[2]
        t0 = time.perf_counter()
        a = (p0, p1)[t](s)
        times[t].append(time.perf_counter() - t0)
        s = apply(s, a)
        turns += 1
    return winner(s), turns, times

def match(n1, n2, games=20):
    r = {"w1": 0, "w2": 0, "draw": 0, "turns": 0, "t1": [], "t2": []}
    for g in range(games):
        swap = g % 2  # alternate who moves first
        a, b = (n1, n2) if not swap else (n2, n1)
        w, turns, times = play(PLAYERS[a], PLAYERS[b])
        r["turns"] += turns
        r["t1"] += times[swap]
        r["t2"] += times[1 - swap]
        if w is None: r["draw"] += 1
        elif (w == 0) != bool(swap): r["w1"] += 1
        else: r["w2"] += 1
    return r

if __name__ == "__main__":
    labels, w1, w2, dr = [], [], [], []
    for n1, n2 in itertools.combinations(PLAYERS, 2):
        battle.STATS[:] = [0, 0]
        r = match(n1, n2)
        avg = lambda l: 1000 * sum(l) / max(1, len(l))
        print(f"{n1} vs {n2}: {r['w1']}-{r['w2']} draws {r['draw']} | "
              f"avg turns {r['turns']/20:.1f} | ms/move {avg(r['t1']):.1f} vs {avg(r['t2']):.1f} | "
              f"nodes {battle.STATS[0]} pruned {battle.STATS[1]}")
        labels.append(f"{n1}\nvs {n2}")
        w1.append(r["w1"]); w2.append(r["w2"]); dr.append(r["draw"])
    x = range(len(labels))
    plt.figure(figsize=(12, 5))
    plt.bar([i - 0.27 for i in x], w1, 0.27, label="First player wins")
    plt.bar(list(x), w2, 0.27, label="Second player wins")
    plt.bar([i + 0.27 for i in x], dr, 0.27, label="Draws")
    plt.xticks(list(x), labels); plt.ylabel("Games (of 20)"); plt.legend()
    plt.savefig("tournament.png"); plt.show()
