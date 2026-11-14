import math, random
from battle import apply, actions, winner, evaluate

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state, self.parent, self.action = state, parent, action
        self.children = []
        self.untried = actions(state) if winner(state) is None else []
        self.n, self.w = 0, 0.0  # w = wins for the player who moved into this node

def rollout(s, cap=60):
    for _ in range(cap):
        w = winner(s)
        if w is not None: return w
        s = apply(s, random.choice(actions(s)))
    return 0 if evaluate(s) > 0 else 1

def mcts_info(state, iters=200, c=1.4):
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
        w = rollout(node.state)
        while node:
            node.n += 1
            if node.parent and w == node.parent.state[2]:
                node.w += 1
            node = node.parent
        top = max(root.children, key=lambda ch: ch.n)
    return top.action, {ch.action: (ch.n, ch.w / ch.n) for ch in root.children}

def mcts(state, iters=200, c=1.4):
    return mcts_info(state, iters, c)[0]

if __name__ == "__main__":
    start = ((((100,20,5,"Fire"),(100,20,5,"Water")),
            ((100,20,5,"Earth"),(100,20,5,"Lightning"))), (0, 0), 0)
    wins = 0
    for g in range(100):
        side = g % 2  # MCTS plays team 0 in even games, team 1 in odd
        s = start
        for _ in range(60):
            if winner(s) is not None: break
            s = apply(s, mcts(s) if s[2] == side else random.choice(actions(s)))
        wins += winner(s) == side
    print("MCTS wins:", wins, "/ 100")
