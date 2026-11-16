"""Match setup screen. With config=None it is the free arena; with config it is a rival fight."""
import pygame, sys, random
from ai.teams import POOL, P, fighter, make_state
from ai.agents import SPECS, label
from core import audio

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
FIRST = ["Random", "Team 1", "Team 2"]
WHITE, MUTED, GOLD, TEAL, PANEL = (244, 239, 230), (169, 165, 184), (242, 184, 75), (94, 194, 183), (32, 29, 48)
DIM = (90, 86, 110)


def select_match(config=None):
    """config: dict(title, unlocked, team2, agent2). Returns (state, (agent1, agent2)) or None."""
    scr = pygame.display.set_mode((960, 540))
    ft, f1, f2 = (pygame.font.SysFont(None, n) for n in (46, 28, 22))
    clock = pygame.time.Clock()
    rival = config is not None
    avail = set(config["unlocked"]) if rival else {p[0] for p in POOL}
    teams = [[], list(config["team2"]) if rival else []]
    agents = [SPECS.index("AlphaBeta:6"), SPECS.index(config["agent2"]) if rival else SPECS.index("MCTS:200")]
    first, active = 0, 0
    panel = lambda s: pygame.Rect(24 + s * 492, 60, 420, 150)
    abtn = lambda s: pygame.Rect(24 + s * 492 + 250, 68, 154, 36)
    slot = lambda s, k: pygame.Rect(24 + s * 492 + 16 + k * 198, 114, 190, 80)
    b_first, b_rand, b_start, b_back = (pygame.Rect(x, 222, w, 40) for x, w in ((24, 220), (256, 220), (488, 220), (720, 216)))
    pool = [pygame.Rect(24 + (i % 4) * 228, 282 + (i // 4) * 122, 216, 112) for i in range(len(POOL))]
    audio.music("menu")

    def button(r, text, on=True, accent=TEAL):
        pygame.draw.rect(scr, PANEL if on else (24, 22, 34), r, border_radius=10)
        pygame.draw.rect(scr, accent if on else (58, 53, 80), r, 3, border_radius=10)
        t = f2.render(text, True, WHITE if on else DIM)
        scr.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    while True:
        used = set(teams[0]) if rival else {n for t in teams for n in t}
        ready = len(teams[0]) == 2 and len(teams[1]) == 2
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m: audio.toggle_mute()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = e.pos; hit = False
                for s in (0, 1):
                    locked = rival and s == 1
                    if abtn(s).collidepoint(pos):
                        if not locked: agents[s] = (agents[s] + 1) % len(SPECS); audio.sfx("move")
                        hit = True
                    for k in (0, 1):
                        if slot(s, k).collidepoint(pos):
                            if not locked and k < len(teams[s]): teams[s].pop(k); audio.sfx("move")
                            if not locked: active = s
                            hit = True
                    if not hit and panel(s).collidepoint(pos):
                        if not locked: active = s
                        hit = True
                if hit: continue
                if b_first.collidepoint(pos): first = (first + 1) % 3; audio.sfx("move")
                elif b_rand.collidepoint(pos):
                    audio.sfx("select")
                    if rival: teams[0] = []; active = 0
                    else:
                        a = random.sample(POOL, 4); teams = [[a[0][0], a[1][0]], [a[2][0], a[3][0]]]
                elif b_back.collidepoint(pos): return None
                elif b_start.collidepoint(pos) and ready:
                    audio.sfx("select")
                    f = random.randint(0, 1) if FIRST[first] == "Random" else int(FIRST[first][-1]) - 1
                    st = make_state(tuple(fighter(P[n]) for n in teams[0]), tuple(fighter(P[n]) for n in teams[1]), f)
                    return st, (SPECS[agents[0]], SPECS[agents[1]])
                for i, p in enumerate(POOL):
                    if pool[i].collidepoint(pos) and p[0] in avail and p[0] not in used and len(teams[active]) < 2:
                        teams[active].append(p[0]); audio.sfx("move")
                        if not rival and len(teams[active]) == 2 and len(teams[1 - active]) < 2: active = 1 - active
        for k in range(18): pygame.draw.rect(scr, (13 + k * 3, 11 + k * 2, 31 + k * 4), (0, k * 30, 960, 30))
        scr.blit(ft.render(config["title"] if rival else "Arena: Choose Your Match", True, GOLD), (24, 14))
        scr.blit(f2.render("Click an unlocked fighter to add it to your team" if rival else "Click a fighter to add it to the highlighted team", True, MUTED), (560 if not rival else 540, 28))
        for s in (0, 1):
            r = panel(s); locked = rival and s == 1
            pygame.draw.rect(scr, (20, 18, 31), r, border_radius=14)
            pygame.draw.rect(scr, GOLD if active == s else (58, 53, 80), r, 3, border_radius=14)
            scr.blit(f1.render(("Rival" if locked else f"Team {s + 1}") if rival else f"Team {s + 1}", True, WHITE), (r.x + 16, r.y + 14))
            button(abtn(s), label(SPECS[agents[s]]), not locked, TEAL)
            for k in (0, 1):
                sr = slot(s, k)
                pygame.draw.rect(scr, PANEL, sr, border_radius=10)
                if k < len(teams[s]):
                    p = P[teams[s][k]]
                    pygame.draw.rect(scr, COL[p[4]], (sr.x, sr.y, 8, sr.h), border_radius=4)
                    scr.blit(f1.render(p[0], True, WHITE), (sr.x + 18, sr.y + 10))
                    scr.blit(f2.render(f"HP {p[1]}  ATK {p[2]}  DEF {p[3]}", True, MUTED), (sr.x + 18, sr.y + 46))
                else:
                    scr.blit(f2.render("Empty slot", True, DIM), (sr.x + 18, sr.y + 30))
        scr.blit(f1.render("VS", True, GOLD), (468, 120))
        button(b_first, f"First move: {FIRST[first]}"); button(b_rand, "Clear my team" if rival else "Random teams")
        button(b_start, "Start battle", ready, GOLD); button(b_back, "Back (ESC)", True, (138, 134, 153))
        mx, my = pygame.mouse.get_pos()
        for i, p in enumerate(POOL):
            r = pool[i]; locked_f = p[0] not in avail; taken = p[0] in used
            off = locked_f or taken
            pygame.draw.rect(scr, (24, 22, 34) if off else (44, 40, 66) if r.collidepoint(mx, my) else PANEL, r, border_radius=12)
            pygame.draw.rect(scr, (58, 53, 80) if off else COL[p[4]], (r.x, r.y, 10, r.h), border_radius=5)
            c1, c2 = (DIM, DIM) if off else (WHITE, MUTED)
            scr.blit(f1.render(p[0], True, c1), (r.x + 22, r.y + 14))
            scr.blit(f2.render("Locked: beat a rival" if locked_f else p[4], True, c2), (r.x + 22, r.y + 48))
            scr.blit(f2.render(f"HP {p[1]}  ATK {p[2]}  DEF {p[3]}", True, c2), (r.x + 22, r.y + 78))
        pygame.display.flip(); clock.tick(60)
