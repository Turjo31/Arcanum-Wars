import battle
from battle import best

s = ((((100,20,5,"Fire"),(100,20,5,"Water")),
  ((100,20,5,"Earth"),(100,20,5,"Lightning"))), (0, 0), 0)

for prune in (False, True):
    battle.STATS[:] = [0, 0]
    m = best(s, 6, prune)
    print("prune" if prune else "minimax", m, battle.STATS)