import random

POOL = [
    ("Fire Knight", 100, 22, 5, "Fire"), ("Flame Archer", 80, 28, 2, "Fire"),
    ("Water Mage", 90, 24, 4, "Water"), ("Tide Guard", 120, 16, 8, "Water"),
    ("Earth Golem", 130, 18, 10, "Earth"), ("Stone Monk", 100, 20, 6, "Earth"),
    ("Storm Rogue", 85, 26, 3, "Lightning"), ("Volt Duelist", 95, 22, 5, "Lightning"),
]
NAMES = {(p[2], p[3], p[4]): p[0] for p in POOL}

def nm(f): return NAMES.get((f[1], f[2], f[3]), f[3])
def fighter(p): return (p[1], p[2], p[3], p[4])

def random_teams(rn=random):
    while True:
        a, b = rn.sample(POOL, 2), rn.sample(POOL, 2)
        if not {x[0] for x in a} & {x[0] for x in b}:
            return tuple(map(fighter, a)), tuple(map(fighter, b))

def make_state(a, b, first=0): return ((a, b), (0, 0), first)

def new_state(rn=random):
    a, b = random_teams(rn)
    return make_state(a, b, rn.randint(0, 1))