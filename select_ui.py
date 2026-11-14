import pygame, sys, random
from teams import POOL, fighter, make_state

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
AGENTS = ["AlphaBeta", "MCTS", "Random"]
LABEL = {"AlphaBeta": "Alpha-Beta", "MCTS": "MCTS", "Random": "Random"}
FIRST = ["Random", "Team 1", "Team 2"]
P = {p[0]: p for p in POOL}
WHITE, MUTED, GOLD, TEAL, PANEL = (244, 239, 230), (169, 165, 184), (242, 184, 75), (94, 194, 183), (32, 29, 48)

def select_match():
    pygame.init()
    scr = pygame.display.set_mode((960, 540))
    ft, f1, f2 = (pygame.font.SysFont(None, n) for n in (46, 28, 22))
    clock = pygame.time.Clock()
    teams, agents, first, active = [[], []], [0, 1], 0, 0
    panel = lambda s: pygame.Rect(24 + s * 492, 60, 420, 150)
    abtn = lambda s: pygame.Rect(24 + s * 492 + 250, 68, 154, 36)
    slot = lambda s, k: pygame.Rect(24 + s * 492 + 16 + k * 198, 114, 190, 80)
    b_first, b_rand, b_start, b_back = (pygame.Rect(x, 222, w, 40) for x, w in ((24, 220), (256, 220), (488, 220), (720, 216)))
    pool = [pygame.Rect(24 + (i % 4) * 228, 282 + (i // 4) * 122, 216, 112) for i in range(len(POOL))]

    def button(r, text, on=True, accent=TEAL):
        pygame.draw.rect(scr, PANEL if on else (24, 22, 34), r, border_radius=10)
        pygame.draw.rect(scr, accent if on else (58, 53, 80), r, 3, border_radius=10)
        t = f2.render(text, True, WHITE if on else (90, 86, 110))
        scr.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    while True:
        used = {n for t in teams for n in t}
        ready = len(teams[0]) == 2 and len(teams[1]) == 2
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = e.pos
                hit = False
                for s in (0, 1):
                    if abtn(s).collidepoint(pos): agents[s] = (agents[s] + 1) % 3; hit = True
                    for k in (0, 1):
                        if slot(s, k).collidepoint(pos):
                            if k < len(teams[s]): teams[s].pop(k)
                            active, hit = s, True
                    if not hit and panel(s).collidepoint(pos): active, hit = s, True
                if hit: continue
                if b_first.collidepoint(pos): first = (first + 1) % 3
                elif b_rand.collidepoint(pos):
                    a = random.sample(POOL, 4); teams = [[a[0][0], a[1][0]], [a[2][0], a[3][0]]]
                elif b_back.collidepoint(pos): return None
                elif b_start.collidepoint(pos) and ready:
                    f = random.randint(0, 1) if FIRST[first] == "Random" else int(FIRST[first][-1]) - 1
                    st = make_state(tuple(fighter(P[n]) for n in teams[0]), tuple(fighter(P[n]) for n in teams[1]), f)
                    return st, (AGENTS[agents[0]], AGENTS[agents[1]])
                for i, p in enumerate(POOL):
                    if pool[i].collidepoint(pos) and p[0] not in used and len(teams[active]) < 2:
                        teams[active].append(p[0])
                        if len(teams[active]) == 2 and len(teams[1 - active]) < 2: active = 1 - active
        for k in range(18): pygame.draw.rect(scr, (13 + k * 3, 11 + k * 2, 31 + k * 4), (0, k * 30, 960, 30))
        scr.blit(ft.render("Arena: Choose Your Match", True, GOLD), (24, 14))
        scr.blit(f2.render("Click a fighter to add it to the highlighted team", True, MUTED), (560, 28))
        for s in (0, 1):
            r = panel(s)
            pygame.draw.rect(scr, (20, 18, 31), r, border_radius=14)
            pygame.draw.rect(scr, GOLD if active == s else (58, 53, 80), r, 3, border_radius=14)
            scr.blit(f1.render(f"Team {s + 1}", True, WHITE), (r.x + 16, r.y + 14))
            button(abtn(s), f"Agent: {LABEL[AGENTS[agents[s]]]}")
            for k in (0, 1):
                sr = slot(s, k)
                pygame.draw.rect(scr, PANEL, sr, border_radius=10)
                if k < len(teams[s]):
                    p = P[teams[s][k]]
                    pygame.draw.rect(scr, COL[p[4]], (sr.x, sr.y, 8, sr.h), border_radius=4)
                    scr.blit(f1.render(p[0], True, WHITE), (sr.x + 18, sr.y + 10))
                    scr.blit(f2.render(f"HP {p[1]}  ATK {p[2]}  DEF {p[3]}", True, MUTED), (sr.x + 18, sr.y + 46))
                else:
                    scr.blit(f2.render("Empty slot", True, (90, 86, 110)), (sr.x + 18, sr.y + 30))
        scr.blit(f1.render("VS", True, GOLD), (468, 120))
        button(b_first, f"First move: {FIRST[first]}"); button(b_rand, "Random teams")
        button(b_start, "Start battle", ready, GOLD); button(b_back, "Back (ESC)", True, (138, 134, 153))
        mx, my = pygame.mouse.get_pos()
        for i, p in enumerate(POOL):
            r, taken = pool[i], p[0] in used
            pygame.draw.rect(scr, (24, 22, 34) if taken else (44, 40, 66) if r.collidepoint(mx, my) else PANEL, r, border_radius=12)
            pygame.draw.rect(scr, (58, 53, 80) if taken else COL[p[4]], (r.x, r.y, 10, r.h), border_radius=5)
            c1, c2 = ((90, 86, 110),) * 2 if taken else (WHITE, MUTED)
            scr.blit(f1.render(p[0], True, c1), (r.x + 22, r.y + 14))
            scr.blit(f2.render(p[4], True, c2), (r.x + 22, r.y + 48))
            scr.blit(f2.render(f"HP {p[1]}  ATK {p[2]}  DEF {p[3]}", True, c2), (r.x + 22, r.y + 78))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    print(select_match())