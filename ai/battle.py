"""Battle engine: deterministic rules, heuristics and Minimax / Alpha-Beta search.

state = (teams, active, turn)
  teams  = (team0, team1); each team = (fighter, fighter)
  fighter = (hp, attack, defense, element)
  active = (active index of team 0, active index of team 1)
  turn   = 0 or 1 (whose move it is)
"""
STRONG = {("Fire", "Earth"), ("Water", "Fire"), ("Earth", "Lightning"), ("Lightning", "Water")}
STATS = [0, 0]  # [nodes visited, branches pruned]


def mult(a, d):
    if (a, d) in STRONG: return 1.5
    if (d, a) in STRONG: return 0.75
    return 1.0


def dmg(a, d):
    """Damage fighter a deals to fighter d."""
    return max(1, round(a[1] * mult(a[3], d[3])) - d[2])


def actions(s):
    teams, act, t = s
    return ["A"] + (["S"] if teams[t][1 - act[t]][0] > 0 else [])


def winner(s):
    for t in (0, 1):
        if all(f[0] <= 0 for f in s[0][t]): return 1 - t
    return None


def apply(s, a):
    teams, act, t = s
    act = list(act); teams = [list(x) for x in teams]; o = 1 - t
    if a == "S":
        act[t] = 1 - act[t]
    else:
        target = teams[o][act[o]]
        teams[o][act[o]] = (max(0, target[0] - dmg(teams[t][act[t]], target)), target[1], target[2], target[3])
        if teams[o][act[o]][0] == 0 and teams[o][1 - act[o]][0] > 0:
            act[o] = 1 - act[o]
    return (tuple(map(tuple, teams)), tuple(act), o)


# ---- heuristics (scored from team 0's point of view) ----
def evaluate(s):
    """Basic: HP difference."""
    w = winner(s)
    if w is not None: return 1000 if w == 0 else -1000
    hp = lambda t: sum(f[0] for f in s[0][t])
    return hp(0) - hp(1)


def evaluate2(s):
    """Smarter: HP difference + fighters alive + current elemental matchup."""
    w = winner(s)
    if w is not None: return 1000 if w == 0 else -1000
    t0, t1 = s[0]
    a0, a1 = t0[s[1][0]], t1[s[1][1]]
    hp = sum(f[0] for f in t0) - sum(f[0] for f in t1)
    alive = 20 * (sum(f[0] > 0 for f in t0) - sum(f[0] > 0 for f in t1))
    return hp + alive + 2 * (dmg(a0, a1) - dmg(a1, a0))


# ---- search ----
def ordered(s, h):
    """Most promising action first (better pruning)."""
    acts = actions(s)
    if len(acts) < 2: return acts
    sign = 1 if s[2] == 0 else -1
    return sorted(acts, key=lambda x: -sign * h(apply(s, x)))


def ab(s, depth, a, b, prune=True, h=evaluate, order=False):
    STATS[0] += 1
    if depth == 0 or winner(s) is not None: return h(s)
    moves = ordered(s, h) if order else actions(s)
    if s[2] == 0:
        v = -1e9
        for x in moves:
            v = max(v, ab(apply(s, x), depth - 1, a, b, prune, h, order)); a = max(a, v)
            if prune and a >= b:
                STATS[1] += 1
                break
        return v
    v = 1e9
    for x in moves:
        v = min(v, ab(apply(s, x), depth - 1, a, b, prune, h, order)); b = min(b, v)
        if prune and a >= b:
            STATS[1] += 1
            break
    return v


def analyze(s, depth=6, h=evaluate, order=False, prune=True):
    """Score every root action from the current player's point of view."""
    sign = 1 if s[2] == 0 else -1
    n0, p0 = STATS
    sc = {x: sign * ab(apply(s, x), depth - 1, -1e9, 1e9, prune, h, order) for x in actions(s)}
    return max(sc, key=sc.get), sc, STATS[0] - n0, STATS[1] - p0


def best(s, depth=6, prune=True, h=evaluate, order=False):
    return analyze(s, depth, h, order, prune)[0]
