import pygame, heapq

T, W, H = 32, 20, 15
WALLS = {(x, 5) for x in range(2, 16)} | {(x, 10) for x in range(4, 18)} | {(8, y) for y in range(11, 15)}

def astar(start, goal):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    pq, came, g = [(h(start), start)], {start: None}, {start: 0}
    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal: break
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
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

pygame.init()
screen = pygame.display.set_mode((W * T, H * T))
clock = pygame.time.Clock()
player, npc, tick = [10, 7], (0, 0), 0

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
    k = pygame.key.get_pressed()
    dx, dy = k[pygame.K_RIGHT] - k[pygame.K_LEFT], k[pygame.K_DOWN] - k[pygame.K_UP]
    tick += 1
    if tick % 4 == 0:
        n = (player[0] + dx, player[1] + dy)
        if (dx or dy) and 0 <= n[0] < W and 0 <= n[1] < H and n not in WALLS:
            player = list(n)
        path = astar(npc, tuple(player))
        if len(path) > 1: npc = path[1]
    screen.fill((30, 30, 30))
    for w in WALLS: pygame.draw.rect(screen, (90, 90, 90), (w[0]*T, w[1]*T, T, T))
    pygame.draw.rect(screen, (60, 160, 255), (player[0]*T, player[1]*T, T, T))
    pygame.draw.rect(screen, (220, 60, 60), (npc[0]*T, npc[1]*T, T, T))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()