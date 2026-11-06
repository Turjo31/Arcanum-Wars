import pygame, heapq, sys
from battle_ui import run

T, W, H = 32, 24, 14
WALLS = {(x, 0) for x in range(W)} | {(x, H-1) for x in range(W)} | {(0, y) for y in range(H)} | {(W-1, y) for y in range(H)}
WALLS |= {(10, y) for y in range(1, 9)} | {(13, y) for y in range(5, 13)} | {(16, y) for y in range(1, 10)}
HOUSE = set()
for hx, hy in ((2, 2), (5, 2), (2, 8)):
    HOUSE |= {(hx + i, hy + j) for i in range(2) for j in range(2)}
WALLS |= HOUSE | {(19, 3), (22, 3), (19, 10), (22, 10)}
START_P, START_N = (1, 6), (14, 2)

def astar(start, goal):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    pq, came, g = [(h(start), start)], {start: None}, {start: 0}
    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal: break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in WALLS and g[cur] + 1 < g.get(n, 1e9):
                g[n] = g[cur] + 1
                came[n] = cur
                heapq.heappush(pq, (g[n] + h(n), n))
    path, p = [], goal
    while p in came and p is not None:
        path.append(p)
        p = came[p]
    return path[::-1]

def draw(screen, player, npc):
    for x in range(W):
        for y in range(H):
            c = (88, 162, 76) if x < 10 else (43, 96, 52) if x < 17 else (216, 192, 138)
            if (x, y) in HOUSE: c = (150, 100, 60)
            elif (x, y) in WALLS: c = (30, 80, 40) if x < 17 else (140, 140, 150)
            pygame.draw.rect(screen, c, (x * T, y * T, T, T))
    pygame.draw.rect(screen, (60, 140, 255), (player[0] * T + 4, player[1] * T + 4, T - 8, T - 8))
    pygame.draw.rect(screen, (230, 70, 50), (npc[0] * T + 4, npc[1] * T + 4, T - 8, T - 8))

def adventure():
    pygame.init()
    screen = pygame.display.set_mode((W * T, H * T))
    clock = pygame.time.Clock()
    player, npc, t_move, t_npc = list(START_P), START_N, 0, 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        now = pygame.time.get_ticks()
        k = pygame.key.get_pressed()
        dx, dy = k[pygame.K_RIGHT] - k[pygame.K_LEFT], k[pygame.K_DOWN] - k[pygame.K_UP]
        if dx: dy = 0
        if (dx or dy) and now - t_move > 110:
            n = (player[0] + dx, player[1] + dy)
            if n not in WALLS: player = list(n)
            t_move = now
        if now - t_npc > 320:
            path = astar(npc, tuple(player))
            if len(path) > 1: npc = path[1]
            t_npc = now
        if abs(player[0] - npc[0]) + abs(player[1] - npc[1]) <= 1:
            run("AlphaBeta", "MCTS")
            screen = pygame.display.set_mode((W * T, H * T))
            player, npc = list(START_P), START_N
        draw(screen, player, npc)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    adventure()