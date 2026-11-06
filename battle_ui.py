import pygame, sys, math, random
from battle import apply, winner, best, mult
from mcts import mcts
from tournament import START

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
NAME = {"Fire": "Fire Knight", "Water": "Water Mage", "Earth": "Earth Golem", "Lightning": "Storm Rogue"}
AI = {"AlphaBeta": lambda s: best(s, 6, True), "MCTS": lambda s: mcts(s, 200)}
SKIN, DARK, STEEL = (242, 201, 160), (58, 53, 80), (217, 221, 232)

def sprite(scr, el, cx, by, s, flip):
    c = COL[el]; d = tuple(int(v * 0.6) for v in c)
    def r(x, y, w, h, col):
        px = cx + ((-x - w) if flip else x) * s
        pygame.draw.rect(scr, col, (px, by + y * s, w * s, h * s))
    pygame.draw.ellipse(scr, (30, 60, 30), (cx - 8 * s, by - 1.5 * s, 16 * s, 3 * s))
    r(-5, -6, 4, 6, DARK); r(1, -6, 4, 6, DARK)
    r(-7, -16, 14, 10, c); r(-7, -9, 14, 2, d); r(-10, -15, 3, 8, c); r(7, -15, 3, 8, c)
    r(-5, -24, 10, 8, SKIN); r(-3, -21, 2, 2, (34, 34, 34)); r(1, -21, 2, 2, (34, 34, 34))
    if el == "Fire": r(-5, -26, 10, 4, (190, 195, 210)); r(-1, -31, 2, 6, (242, 184, 75)); r(10, -24, 2, 16, STEEL)
    elif el == "Water": r(-6, -27, 12, 5, c); r(10, -26, 2, 24, (110, 80, 50)); r(9, -29, 4, 4, (142, 202, 230))
    elif el == "Earth": r(-11, -17, 5, 5, d); r(6, -17, 5, 5, d); r(-3, -26, 6, 3, d)
    else: r(-5, -28, 3, 4, COL[el]); r(-1, -30, 3, 6, COL[el]); r(3, -28, 3, 4, COL[el]); r(10, -14, 2, 8, STEEL)

def draw_fighter(scr, el, cx, by, s, flip, alpha=255, dx=0, dy=0):
    surf = pygame.Surface((260, 260), pygame.SRCALPHA)
    sprite(surf, el, 130, 230, s, flip)
    surf.set_alpha(max(0, min(255, int(alpha))))
    scr.blit(surf, (cx - 130 + dx, by - 230 + dy))

def bar_color(f): return (94, 194, 183) if f > .5 else (242, 184, 75) if f > .25 else (230, 59, 46)

def panel(scr, fonts, s, disp, maxhp, side, label, x, y, i):
    f1, f2 = fonts
    teams, act, turn = s
    hp, atk, df, el = teams[side][i]
    pygame.draw.rect(scr, (20, 18, 31), (x, y, 310, 120), border_radius=14)
    if turn == side: pygame.draw.rect(scr, (242, 184, 75), (x, y, 310, 120), 3, border_radius=14)
    scr.blit(f2.render(f"Team {side + 1} · {label}", True, (169, 165, 184)), (x + 16, y + 10))
    scr.blit(f1.render(NAME[el], True, (244, 239, 230)), (x + 16, y + 32))
    pygame.draw.circle(scr, COL[el], (x + 280, y + 42), 12)
    frac = max(0, disp[side][i] / maxhp[side][i])
    pygame.draw.rect(scr, (58, 53, 80), (x + 16, y + 62, 278, 14), border_radius=7)
    if frac > 0: pygame.draw.rect(scr, bar_color(frac), (x + 16, y + 62, 278 * frac, 14), border_radius=7)
    scr.blit(f2.render(f"HP {max(0, round(disp[side][i]))}/{maxhp[side][i]}  ATK {atk}  DEF {df}", True, (244, 239, 230)), (x + 16, y + 82))
    b = 1 - i; bh, _, _, bel = teams[side][b]
    scr.blit(f2.render(f"Bench: {NAME[bel]} {bh}/{maxhp[side][b]}", True, (169, 165, 184)), (x + 16, y + 100))

def run(n1="AlphaBeta", n2="MCTS"):
    pygame.init()
    scr = pygame.display.set_mode((960, 540))
    f1, f2, f3, f4 = (pygame.font.SysFont(None, n) for n in (30, 22, 56, 40))
    clock = pygame.time.Clock()
    names = (n1, n2)
    s = START
    maxhp = [[f[0] for f in t] for t in START[0]]
    disp = [[float(f[0]) for f in t] for t in START[0]]
    vis = [{"idx": 0, "st": "idle", "t0": 0, "to": 0, "kind": ""} for _ in range(2)]
    log, floats = ["Battle start!"], []
    phase, pt, pending, applied, hit_t, hit_side, turns = "wait", 0, None, False, -9999, 0, 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        now = pygame.time.get_ticks()
        w = winner(s)
        settled = all(v["st"] in ("idle", "gone") for v in vis)
        if w is None and turns < 60:
            if phase == "wait" and now - pt > 700:
                a = AI[names[s[2]]](s)
                pending, applied, phase, pt = (a, s, apply(s, a)), False, "anim", now
            elif phase == "anim":
                el = now - pt
                if not applied and el > 250:
                    a, old, new = pending; t, o = old[2], 1 - old[2]
                    if a == "A":
                        ai = old[1][o]; dmg = old[0][o][ai][0] - new[0][o][ai][0]
                        m = mult(old[0][t][old[1][t]][3], old[0][o][ai][3])
                        tag = " Super effective!" if m > 1 else " Not very effective." if m < 1 else ""
                        log.append(f"Team {t + 1}'s {NAME[old[0][t][old[1][t]][3]]} attacks: -{dmg}.{tag}")
                        if new[0][o][ai][0] == 0: log.append(f"{NAME[old[0][o][ai][3]]} fainted!")
                        floats.append([250 if o == 0 else 700, 290 if o == 0 else 205, f"-{dmg}", (242, 184, 75) if m > 1 else (255, 255, 255), now])
                        hit_t, hit_side = now, o
                    else:
                        log.append(f"Team {t + 1} switches to {NAME[new[0][t][new[1][t]][3]]}.")
                    for side in (0, 1):
                        oi, ni = old[1][side], new[1][side]
                        fainted = new[0][side][oi][0] == 0 and old[0][side][oi][0] > 0
                        if ni != oi:
                            vis[side].update(st="out", kind="faint" if fainted else "switch", t0=now + 400 if fainted else now, to=ni)
                        elif fainted:
                            vis[side].update(st="out", kind="faint", t0=now + 400, to=None)
                    s, applied = new, True
                if el > 700 and applied and settled: phase, pt, turns = "wait", now, turns + 1
        for v in vis:
            if v["st"] == "out" and now - v["t0"] >= (600 if v["kind"] == "faint" else 350):
                if v["to"] is None: v["st"] = "gone"
                else: v.update(st="in", t0=now, idx=v["to"])
            elif v["st"] == "in" and now - v["t0"] >= 450: v["st"] = "idle"
        for side in (0, 1):
            for i in (0, 1):
                tgt = s[0][side][i][0]
                disp[side][i] += (tgt - disp[side][i]) * 0.15
                if abs(tgt - disp[side][i]) < .5: disp[side][i] = tgt
        for k in range(12): pygame.draw.rect(scr, (140 + k * 7, 203 + k * 3, 238 - k * 2), (0, k * 21, 960, 22))
        pygame.draw.polygon(scr, (127, 181, 154), [(0, 250), (180, 170), (360, 250)])
        pygame.draw.polygon(scr, (106, 168, 138), [(280, 250), (520, 150), (760, 250)])
        pygame.draw.rect(scr, (109, 187, 90), (0, 250, 960, 290))
        pygame.draw.ellipse(scr, (76, 157, 74), (60, 385, 380, 50)); pygame.draw.ellipse(scr, (76, 157, 74), (580, 305, 240, 40))
        for side, (bx, by, sc, flip) in enumerate(((250, 410, 5, False), (700, 330, 4.4, True))):
            v = vis[side]
            if v["st"] == "gone": continue
            el = s[0][side][v["idx"]][3]
            dx = dy = 0; alpha = 255
            if v["st"] == "in":
                p = min(1, (now - v["t0"]) / 450)
                dx, alpha = (-1 if side == 0 else 1) * 160 * (1 - p), 255 * p
            elif v["st"] == "out" and now >= v["t0"]:
                p = min(1, (now - v["t0"]) / (600 if v["kind"] == "faint" else 350))
                alpha = 255 * (1 - p)
                if v["kind"] == "faint": dy = 45 * p
                else: dx = (-1 if side == 0 else 1) * 140 * p
            elif phase == "anim" and pending and pending[1][2] == side and pending[0] == "A":
                dx = math.sin(math.pi * min(1, (now - pt) / 500)) * 70 * (1 if side == 0 else -1)
            if now - hit_t < 250 and hit_side == side and v["st"] != "in": dx += random.randint(-5, 5)
            draw_fighter(scr, el, bx, by, sc, flip, alpha, dx, dy)
        if now - hit_t < 300:
            pygame.draw.circle(scr, (255, 255, 255), (250 if hit_side == 0 else 700, 300 if hit_side == 0 else 220), int((now - hit_t) / 5), 4)
        for f in floats[:]:
            age = now - f[4]
            if age > 900: floats.remove(f); continue
            scr.blit(f4.render(f[2], True, f[3]), (f[0] - 30, f[1] - age / 10))
        panel(scr, (f1, f2), s, disp, maxhp, 0, names[0], 24, 24, vis[0]["idx"])
        panel(scr, (f1, f2), s, disp, maxhp, 1, names[1], 626, 24, vis[1]["idx"])
        pygame.draw.rect(scr, (20, 18, 31), (24, 430, 912, 90), border_radius=14)
        for i, line in enumerate(log[-3:]): scr.blit(f1.render(line, True, (244, 239, 230) if i == len(log[-3:]) - 1 else (169, 165, 184)), (44, 444 + i * 26))
        if w is not None and settled:
            pygame.draw.rect(scr, (20, 18, 31), (0, 190, 960, 100))
            scr.blit(f3.render(f"Team {w + 1} wins!", True, (242, 184, 75)), (480 - 130, 205))
            scr.blit(f2.render("Press ESC to return", True, (169, 165, 184)), (480 - 80, 262))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run()