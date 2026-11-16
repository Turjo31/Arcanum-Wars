"""Monte Carlo Tree Search with element-aware playouts."""
import math, random
from ai.battle import apply, actions, winner, evaluate, dmg


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state, self.parent, self.action = state, parent, action
        self.children = []
        self.untried = actions(state) if winner(state) is None else []
        self.n, self.w = 0, 0.0


def greedy_move(s):
    """Attack unless the bench fighter has a clearly better matchup."""
    acts = actions(s)
    if len(acts) == 1: return acts[0]
    teams, act, t = s
    me, opp, bench = teams[t][act[t]], teams[1 - t][act[1 - t]], teams[t][1 - act[t]]
    now = dmg(me, opp) - dmg(opp, me)
    alt = dmg(bench, opp) - dmg(opp, bench)
    return "S" if alt > now + 10 else "A"


def policy(s):
    """Playout policy: mostly greedy, 20% random so simulations stay varied."""
    if random.random() < 0.2: return random.choice(actions(s))
    return greedy_move(s)


def rollout(s, smart=True, cap=60):
    for _ in range(cap):
        w = winner(s)
        if w is not None: return w
        s = apply(s, policy(s) if smart else random.choice(actions(s)))
    return 0 if evaluate(s) > 0 else 1


def mcts_info(state, iters=200, c=1.4, smart=True):
    root = Node(state)
    for _ in range(iters):
        node = root
        while not node.untried and node.children:
            node = max(node.children, key=lambda ch: ch.w / ch.n + c * math.sqrt(math.log(node.n) / ch.n))
        if node.untried:
            a = node.untried.pop(random.randrange(len(node.untried)))
            ch = Node(apply(node.state, a), node, a)
            node.children.append(ch)
            node = ch
        w = rollout(node.state, smart)
        while node:
            node.n += 1
            if node.parent and w == node.parent.state[2]:
                node.w += 1
            node = node.parent
    top = max(root.children, key=lambda ch: ch.n)
    return top.action, {ch.action: (ch.n, ch.w / ch.n) for ch in root.children}


def mcts(state, iters=200, c=1.4, smart=True):
    return mcts_info(state, iters, c, smart)[0]
