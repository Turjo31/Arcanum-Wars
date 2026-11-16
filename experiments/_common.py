import sys, pathlib, csv, random
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

from ai.battle import apply, winner
from ai.agents import act
from ai.teams import random_teams, make_state


def head_to_head(spec1, spec2, games=100, seed=1):
    """Fair mirrored games: both agents play both teams and both move first. Returns (wins1, wins2, draws)."""
    rn = random.Random(seed); w1 = w2 = d = 0
    for _ in range(max(1, games // 4)):
        A, B = random_teams(rn)
        for mine, theirs in ((A, B), (B, A)):
            for first in (0, 1):
                s = make_state(mine, theirs, first)
                for _ in range(60):
                    if winner(s) is not None: break
                    s = apply(s, act((spec1, spec2)[s[2]], s))
                w = winner(s)
                if w == 0: w1 += 1
                elif w == 1: w2 += 1
                else: d += 1
    return w1, w2, d


def save_csv(name, header, rows):
    path = RESULTS / name
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print("saved", path)


def games_arg(default):
    return int(sys.argv[1]) if len(sys.argv) > 1 else default
