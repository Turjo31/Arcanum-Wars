STRONG = {("Fire","Earth"),("Water","Fire"),("Earth","Lightning"),("Lightning","Water")}
# state = (teams, active, turn); fighter = (hp, atk, element)

def mult(a, d):
    if (a, d) in STRONG: return 1.5
    if (d, a) in STRONG: return 0.75
    return 1.0

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
        _, atk, _, el = teams[t][act[t]]
        dh, da, dd, de = teams[o][act[o]]
        dmg = max(1, round(atk * mult(el, de)) - dd)
        teams[o][act[o]] = (max(0, dh - dmg), da, dd, de)
        if teams[o][act[o]][0] == 0 and teams[o][1 - act[o]][0] > 0:
            act[o] = 1 - act[o]
    return (tuple(map(tuple, teams)), tuple(act), o)

def evaluate(s):
    w = winner(s)
    if w is not None: return 1000 if w == 0 else -1000
    hp = lambda t: sum(f[0] for f in s[0][t])
    return hp(0) - hp(1)

STATS = [0, 0]  # [nodes visited, branches pruned]

def ab(s, depth, a, b, prune=True):
    STATS[0] += 1
    if depth == 0 or winner(s) is not None: return evaluate(s)
    if s[2] == 0:
        v = -1e9
        for x in actions(s):
            v = max(v, ab(apply(s, x), depth - 1, a, b, prune)); a = max(a, v)
            if prune and a >= b:
                STATS[1] += 1
                break
        return v
    v = 1e9
    for x in actions(s):
        v = min(v, ab(apply(s, x), depth - 1, a, b, prune)); b = min(b, v)
        if prune and a >= b:
            STATS[1] += 1
            break
    return v

def best(s, depth=6, prune=True):
    sign = 1 if s[2] == 0 else -1
    return max(actions(s), key=lambda x: sign * ab(apply(s, x), depth - 1, -1e9, 1e9, prune))

if __name__ == "__main__":
    s = ((((100,20,5,"Fire"),(100,20,5,"Water")),
  ((100,20,5,"Earth"),(100,20,5,"Lightning"))), (0, 0), 0)
    for turn in range(60):
        if winner(s) is not None: break
        s = apply(s, best(s))
    print(turn, winner(s), s)

def analyze(s, depth=6):
    sign = 1 if s[2] == 0 else -1
    n0, p0 = STATS
    sc = {x: sign * ab(apply(s, x), depth - 1, -1e9, 1e9, True) for x in actions(s)}
    return max(sc, key=sc.get), sc, STATS[0] - n0, STATS[1] - p0