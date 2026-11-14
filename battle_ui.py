import pygame, sys, math, random
from battle import apply, winner, mult, actions, analyze
from mcts import mcts_info
from teams import new_state, nm

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
SKIN, DARK, STEEL = (242, 201, 160), (58, 53, 80), (217, 221, 232)
WOOD, GOLD = (110, 80, 50), (242, 184, 75)
LABEL = {"AlphaBeta": "Alpha-Beta", "MCTS": "MCTS", "Random": "Random"}
ACT = {"A": "Attack", "S": "Switch"}

def think(name, s):
    if name == "AlphaBeta":
        a, sc, nodes, pruned = analyze(s)
        return a, {"kind": "ab", "scores": sc, "nodes": nodes, "pruned": pruned}
    if name == "MCTS":
        a, st = mcts_info(s, 200)
        return a, {"kind": "mcts", "stats": st}
    return random.choice(actions(s)), {"kind": "rand"}

def think_panel(scr, f2, th):
    r = pygame.Rect(600, 430, 336, 90)
    pygame.draw.rect(scr, (20, 18, 31), r, border_radius=14)
    if not th:
        scr.blit(f2.render("AI thinking appears here", True, (169, 165, 184)), (r.x + 16, r.y + 34)); return
    side, name, info, chosen = th
    scr.blit(f2.render(f"Team {side + 1} · {LABEL[name]} thinking", True, (242, 184, 75)), (r.x + 14, r.y + 6))
    if info["kind"] == "rand":
        scr.blit(f2.render("Picks any legal action at random", True, (244, 239, 230)), (r.x + 14, r.y + 40)); return
    vals = info["scores"] if info["kind"] == "ab" else {a: v[0] for a, v in info["stats"].items()}
    lo, hi, tot = min(vals.values()), max(vals.values()), max(1, sum(vals.values()))
    for i, a in enumerate(sorted(vals)):
        y = r.y + 28 + i * 20
        col = (242, 184, 75) if a == chosen else (169, 165, 184)
        frac = (vals[a] - lo) / (hi - lo) if info["kind"] == "ab" and hi > lo else (1.0 if info["kind"] == "ab" else vals[a] / tot)
        pygame.draw.rect(scr, (58, 53, 80), (r.x + 80, y + 3, 130, 12), border_radius=6)
        pygame.draw.rect(scr, col, (r.x + 80, y + 3, max(6, 130 * frac), 12), border_radius=6)
        txt = f"{vals[a]:+d}" if info["kind"] == "ab" else f"{vals[a]} ({100 * vals[a] // tot}%)"
        scr.blit(f2.render(ACT[a], True, col), (r.x + 14, y)); scr.blit(f2.render(txt, True, col), (r.x + 218, y))
    foot = f"{info['nodes']} nodes · {info['pruned']} pruned" if info["kind"] == "ab" else "200 simulations"
    scr.blit(f2.render(foot, True, (244, 239, 230)), (r.x + 14, r.y + 68))

def sprite(scr, name, el, cx, by, s, flip):
    c = COL[el]; d = tuple(int(v * 0.6) for v in c); l = tuple(min(255, int(v * 1.25)) for v in c)
    def r(x, y, w, h, col):
        px = cx + ((-x - w) if flip else x) * s
        pygame.draw.rect(scr, col, (px, by + y * s, w * s, h * s))
    pygame.draw.ellipse(scr, (30, 60, 30), (cx - 10 * s, by - 1.5 * s, 20 * s, 3 * s))
    if name == "Earth Golem":
        r(-9, -8, 7, 8, d); r(2, -8, 7, 8, d); r(-14, -24, 28, 18, c); r(-14, -24, 28, 4, l)
        r(-20, -22, 6, 18, d); r(14, -22, 6, 18, d); r(-6, -34, 12, 10, c); r(-4, -31, 3, 3, GOLD); r(1, -31, 3, 3, GOLD)
        r(-9, -18, 4, 4, d); r(3, -15, 5, 4, d); return
    dark = (40, 36, 60)
    r(-5, -6, 4, 6, DARK); r(1, -6, 4, 6, DARK)
    robe = name in ("Water Mage", "Stone Monk")
    body = dark if name == "Storm Rogue" else c
    if robe: r(-8, -16, 16, 13, body); r(-8, -6, 16, 3, d)
    else: r(-7, -16, 14, 10, body); r(-7, -9, 14, 2, d)
    r(-10, -15, 3, 8, body); r(7, -15, 3, 8, body)
    r(-5, -24, 10, 8, SKIN); r(-3, -21, 2, 2, (34, 34, 34)); r(1, -21, 2, 2, (34, 34, 34))
    if name == "Fire Knight":
        r(-5, -26, 10, 4, (190, 195, 210)); r(-5, -22, 10, 2, DARK); r(-1, -32, 2, 7, GOLD); r(10, -26, 2, 18, STEEL); r(8, -10, 6, 2, GOLD)
    elif name == "Flame Archer":
        r(-6, -27, 12, 6, d); r(-6, -22, 3, 6, d); r(9, -26, 3, 4, WOOD); r(11, -22, 2, 12, WOOD); r(9, -10, 3, 4, WOOD); r(13, -24, 1, 16, STEEL)
    elif name == "Water Mage":
        r(-7, -27, 14, 3, d); r(-4, -34, 8, 8, d); r(10, -28, 2, 26, WOOD); r(8, -32, 6, 5, (142, 202, 230))
    elif name == "Tide Guard":
        r(-6, -27, 12, 6, STEEL); r(-6, -22, 12, 2, DARK); r(-9, -16, 18, 2, l); r(9, -22, 8, 16, (60, 110, 200)); r(11, -18, 4, 8, STEEL)
    elif name == "Stone Monk":
        r(-5, -26, 10, 2, SKIN); r(-8, -9, 16, 2, GOLD); r(10, -26, 2, 24, WOOD); r(8, -26, 6, 3, GOLD)
    elif name == "Storm Rogue":
        r(-6, -27, 12, 5, dark); r(-5, -21, 10, 3, dark); r(-5, -17, 10, 3, c); r(10, -14, 2, 9, STEEL); r(9, -6, 4, 2, GOLD)
    else:
        r(-5, -28, 3, 5, c); r(-1, -31, 3, 8, c); r(3, -28, 3, 5, c); r(10, -28, 2, 24, STEEL); r(8, -14, 6, 2, c)

def draw_fighter(scr, name, el, cx, by, s, flip, alpha=255, dx=0, dy=0):
    surf = pygame.Surface((260, 260), pygame.SRCALPHA)
    sprite(surf, name, el, 130, 230, s, flip)
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
    scr.blit(f1.render(nm(teams[side][i]), True, (244, 239, 230)), (x + 16, y + 32))
    pygame.draw.circle(scr, COL[el], (x + 280, y + 42), 12)
    frac = max(0, disp[side][i] / maxhp[side][i])
    pygame.draw.rect(scr, (58, 53, 80), (x + 16, y + 62, 278, 14), border_radius=7)
    if frac > 0: pygame.draw.rect(scr, bar_color(frac), (x + 16, y + 62, 278 * frac, 14), border_radius=7)
    scr.blit(f2.render(f"HP {max(0, round(disp[side][i]))}/{maxhp[side][i]}  ATK {atk}  DEF {df}", True, (244, 239, 230)), (x + 16, y + 82))
    b = 1 - i
    scr.blit(f2.render(f"Bench: {nm(teams[side][b])} {teams[side][b][0]}/{maxhp[side][b]}", True, (169, 165, 184)), (x + 16, y + 100))

def run(n1="AlphaBeta", n2="MCTS", state=None):
    pygame.init()
    scr = pygame.display.set_mode((960, 540))
    f1, f2, f3, f4 = (pygame.font.SysFont(None, n) for n in (30, 22, 56, 40))
    clock = pygame.time.Clock()
    names = (n1, n2) if state or random.random() < 0.5 else (n2, n1)
    s = state or new_state()
    maxhp = [[f[0] for f in t] for t in s[0]]
    disp = [[float(f[0]) for f in t] for t in s[0]]
    vis = [{"idx": 0, "st": "idle", "t0": 0, "to": 0, "kind": ""} for _ in range(2)]
    log, floats = [f"Battle start! Team {s[2] + 1} moves first."], []
    thought = None
    parts = []
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
                a, info = think(names[s[2]], s)
                thought = (s[2], names[s[2]], info, a)
                pending, applied, phase, pt = (a, s, apply(s, a)), False, "anim", now
            elif phase == "anim":
                el = now - pt
                if not applied and el > 250:
                    a, old, new = pending; t, o = old[2], 1 - old[2]
                    if a == "A":
                        ai = old[1][o]; dmg = old[0][o][ai][0] - new[0][o][ai][0]
                        m = mult(old[0][t][old[1][t]][3], old[0][o][ai][3])
                        tag = " Super effective!" if m > 1 else " Not very effective." if m < 1 else ""
                        log.append(f"Team {t + 1}'s {nm(old[0][t][old[1][t]])} attacks: -{dmg}.{tag}")
                        if new[0][o][ai][0] == 0: log.append(f"{nm(old[0][o][ai])} fainted!")
                        floats.append([250 if o == 0 else 700, 290 if o == 0 else 205, f"-{dmg}", (242, 184, 75) if m > 1 else (255, 255, 255), now])
                        hit_t, hit_side = now, o
                        cx_, cy_ = (250, 300) if o == 0 else (700, 230)
                        for _ in range(18):
                            ang = random.uniform(0, 6.283); sp = random.uniform(2, 7)
                            parts.append([cx_, cy_, math.cos(ang) * sp, math.sin(ang) * sp - 2, now, COL[old[0][t][old[1][t]][3]]])
                    else:
                        log.append(f"Team {t + 1} switches to {nm(new[0][t][new[1][t]])}.")
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
            fi = s[0][side][v["idx"]]
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
            draw_fighter(scr, nm(fi), fi[3], bx, by, sc, flip, alpha, dx, dy)
        if now - hit_t < 300:
            pygame.draw.circle(scr, (255, 255, 255), (250 if hit_side == 0 else 700, 300 if hit_side == 0 else 220), int((now - hit_t) / 5), 4)
        for p in parts[:]:
            age = now - p[4]
            if age > 600: parts.remove(p); continue
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.25
            pygame.draw.circle(scr, p[5], (int(p[0]), int(p[1])), max(1, int(5 * (1 - age / 600))))
        for f in floats[:]:
            age = now - f[4]
            if age > 900: floats.remove(f); continue
            scr.blit(f4.render(f[2], True, f[3]), (f[0] - 30, f[1] - age / 10))
        panel(scr, (f1, f2), s, disp, maxhp, 0, LABEL[names[0]], 24, 24, vis[0]["idx"])
        panel(scr, (f1, f2), s, disp, maxhp, 1, LABEL[names[1]], 626, 24, vis[1]["idx"])
        pygame.draw.rect(scr, (20, 18, 31), (24, 430, 560, 90), border_radius=14)
        for i, line in enumerate(log[-3:]): scr.blit(f2.render(line, True, (244, 239, 230) if i == len(log[-3:]) - 1 else (169, 165, 184)), (40, 442 + i * 26))
        think_panel(scr, f2, thought)
        if w is not None and settled:
            pygame.draw.rect(scr, (20, 18, 31), (0, 190, 960, 100))
            t = f3.render(f"Team {w + 1} ({LABEL[names[w]]}) wins!", True, (242, 184, 75))
            scr.blit(t, (480 - t.get_width() // 2, 205))
            scr.blit(f2.render("Press ESC to return", True, (169, 165, 184)), (480 - 80, 262))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run()