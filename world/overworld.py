"""Overworld: three maps, villagers, the A* rival, unlocks, pause menu and animated water."""
import pygame, heapq, sys, math
from ai.teams import RIVALS
from ai.agents import label
from ui.battle_ui import run
from ui.select_ui import select_match
from ui.help_ui import show_help
from core import audio, save
from world import maps as M
from world.maps import T, BLOCK, person
from world.npcs import NPCS, ARENA_NPCS, SIGNS, VW, VH, dialogue, message_panel


def astar(start, goal, m):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    W, H, blocked = len(m["g"][0]), len(m["g"]), m["blocked"]
    pq, came, g = [(h(start), start)], {start: None}, {start: 0}
    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal: break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in blocked and g[cur] + 1 < g.get(n, 1e9):
                g[n] = g[cur] + 1; came[n] = cur; heapq.heappush(pq, (g[n] + h(n), n))
    path, p = [], goal
    while p in came and p is not None:
        path.append(p); p = came[p]
    return path[::-1]


def fade(screen):
    cover = pygame.Surface((VW, VH))
    for a in range(0, 255, 40):
        cover.set_alpha(a); screen.blit(cover, (0, 0)); pygame.display.flip(); pygame.time.delay(15)


def pause_menu(screen, f1, f2):
    """Returns 'resume' or 'quit'."""
    base = screen.copy(); clock = pygame.time.Clock(); sel = 0
    items = ["Resume", "Help", "Quit to menu"]
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "resume"
                if e.key in (pygame.K_UP, pygame.K_w): sel = (sel - 1) % 3; audio.sfx("move")
                if e.key in (pygame.K_DOWN, pygame.K_s): sel = (sel + 1) % 3; audio.sfx("move")
                if e.key == pygame.K_m: audio.toggle_mute()
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    audio.sfx("select")
                    if sel == 0: return "resume"
                    if sel == 1:
                        show_help(); screen = pygame.display.set_mode((VW, VH)); base = screen.copy()
                    if sel == 2: return "quit"
        screen.blit(base, (0, 0))
        dim = pygame.Surface((VW, VH)); dim.set_alpha(150); screen.blit(dim, (0, 0))
        r = pygame.Rect(300, 130, 360, 250)
        pygame.draw.rect(screen, (20, 18, 31), r, border_radius=16); pygame.draw.rect(screen, (242, 184, 75), r, 3, border_radius=16)
        t = pygame.font.SysFont(None, 46).render("Paused", True, (242, 184, 75)); screen.blit(t, (480 - t.get_width() // 2, r.y + 16))
        for i, it in enumerate(items):
            b = pygame.Rect(r.x + 40, r.y + 78 + i * 56, 280, 44)
            pygame.draw.rect(screen, (32, 29, 48), b, border_radius=10)
            pygame.draw.rect(screen, (242, 184, 75) if i == sel else (94, 194, 183), b, 3, border_radius=10)
            f = f1.render(it, True, (244, 239, 230)); screen.blit(f, (b.centerx - f.get_width() // 2, b.centery - f.get_height() // 2))
        pygame.display.flip(); clock.tick(30)


def rival_fight(screen, sv, f1, f2):
    """Team pick + battle against the current rival. Updates and saves progress."""
    name, team, agent, reward = RIVALS[sv["tier"]]
    res = select_match(dict(title=f"Rival: {name} ({label(agent)})", unlocked=sv["unlocked"], team2=team, agent2=agent))
    screen = pygame.display.set_mode((VW, VH))
    if res is None: return screen
    result = run(res[1][0], res[1][1], res[0])
    screen = pygame.display.set_mode((VW, VH))
    sv["battles"] += 1
    if result and result["winner"] == 0:
        sv["wins"] += 1; sv["tier"] += 1
        lines = [f"You defeated {name}!"]
        if reward and reward not in sv["unlocked"]:
            sv["unlocked"].append(reward); lines.append(f"New fighter unlocked: {reward}")
        elif reward is None: lines.append("You are the champion of the forest!")
        save.save(sv); audio.sfx("unlock")
        message_panel(screen, f1, f2, "Victory!", lines)
    elif result:
        save.save(sv); audio.sfx("lose")
        message_panel(screen, f1, f2, "Defeat" if result["winner"] == 1 else "Draw", [f"{name} was too strong this time.", "Pick a different team or try again."])
    return screen


def adventure():
    screen = pygame.display.set_mode((VW, VH))
    f1, f2, f3 = (pygame.font.SysFont(None, n) for n in (30, 22, 34))
    sv = save.load()
    maps = {"village": M.village(), "forest": M.forest(), "arena": M.arena()}
    maps["village"]["objs"] = NPCS + SIGNS["village"]
    maps["arena"]["objs"] = ARENA_NPCS
    for m in maps.values():
        m.setdefault("objs", [])
        m["surf"] = M.render(m)
        m["blocked"] = {(x, y) for y, row in enumerate(m["g"]) for x, c in enumerate(row) if c in BLOCK}
        m["blocked"] |= {o["pos"] for o in m["objs"]}
        m["water"] = [(x, y) for y, row in enumerate(m["g"]) for x, c in enumerate(row) if c == "~"]
    key = "village"; m = maps[key]
    rival_on = lambda: sv["tier"] < len(RIVALS)
    player, npc, t_move, t_npc, steps, chasing = list(m["spawn"]), m["npc"], 0, 0, 0, False
    talk = None
    clock = pygame.time.Clock()
    near_obj = lambda: next((o for o in m["objs"] if abs(o["pos"][0] - player[0]) + abs(o["pos"][1] - player[1]) <= 1), None)
    while True:
        audio.music(key)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m: audio.toggle_mute()
                elif e.key == pygame.K_ESCAPE:
                    if talk: talk = None
                    elif pause_menu(screen, f1, f2) == "quit": save.save(sv); return
                    screen = pygame.display.set_mode((VW, VH))
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if talk:
                        talk[2] += 1
                        if talk[2] >= len(talk[1]): talk = None
                    else:
                        o = near_obj()
                        if o:
                            audio.sfx("select")
                            lines = o["lines"](sv) if callable(o["lines"]) else o["lines"]
                            talk = [o, lines, 0]
        now = pygame.time.get_ticks()
        k = pygame.key.get_pressed()
        dx, dy = k[pygame.K_RIGHT] - k[pygame.K_LEFT], k[pygame.K_DOWN] - k[pygame.K_UP]
        if dx: dy = 0
        if not talk and (dx or dy) and now - t_move > 120:
            n = (player[0] + dx, player[1] + dy)
            if 0 <= n[0] < len(m["g"][0]) and 0 <= n[1] < len(m["g"]) and n not in m["blocked"]:
                player = list(n); steps += 1
                for (rx, ry, rw, rh), to, sp in m["exits"]:
                    if rx <= n[0] < rx + rw and ry <= n[1] < ry + rh:
                        fade(screen); key = to; m = maps[key]; player, chasing = list(sp), False
                        npc = m["npc"] if (key != "forest" or rival_on()) else None
                        break
                else:
                    if m["g"][n[1]][n[0]] == "E":
                        res = select_match()
                        if res: run(res[1][0], res[1][1], res[0])
                        screen = pygame.display.set_mode((VW, VH)); player = [11, 10]
            t_move = now
        if npc and not talk and now - t_npc > 280:
            path = astar(npc, tuple(player), m)
            chasing = 1 < len(path) <= 24
            if chasing: npc = path[1]
            t_npc = now
        if npc and abs(player[0] - npc[0]) + abs(player[1] - npc[1]) <= 1:
            screen = rival_fight(screen, sv, f1, f2)
            player, chasing = list(m["spawn"]), False
            npc = m["npc"] if rival_on() else None
        mw, mh = len(m["g"][0]) * T, len(m["g"]) * T
        cx = max(0, min(player[0] * T + 20 - VW // 2, mw - VW)); cy = max(0, min(player[1] * T + 20 - VH // 2, mh - VH))
        screen.blit(m["surf"], (-cx, -cy))
        for (wx, wy) in m["water"]:
            sx, sy = wx * T - cx, wy * T - cy
            if -T < sx < VW and -T < sy < VH:
                o = int(6 * math.sin(now / 450 + wx * 0.9 + wy * 0.5))
                pygame.draw.rect(screen, (120, 175, 235), (sx + 8 + o, sy + 10, 14, 3)); pygame.draw.rect(screen, (100, 155, 225), (sx + 16 - o, sy + 26, 14, 3))
        for o in m["objs"]:
            if not o.get("sign"): person(screen, o["pos"][0] * T - cx, o["pos"][1] * T - cy - 4, o["body"], o["hair"], 0)
        if npc:
            person(screen, npc[0] * T - cx, npc[1] * T - cy - 4, (230, 70, 50), (20, 18, 31), (now // 160) % 2 * 2)
            tag = f2.render(RIVALS[sv["tier"]][0], True, (244, 239, 230))
            screen.blit(tag, (npc[0] * T - cx + 20 - tag.get_width() // 2, npc[1] * T - cy - 34))
            if chasing:
                pygame.draw.circle(screen, (242, 184, 75), (npc[0] * T - cx + 20, npc[1] * T - cy - 48), 13)
                screen.blit(f3.render("!", True, (20, 18, 31)), (npc[0] * T - cx + 16, npc[1] * T - cy - 59))
        person(screen, player[0] * T - cx, player[1] * T - cy - 4, (60, 140, 255), (58, 42, 26), steps % 2 * 2)
        pygame.draw.rect(screen, (20, 18, 31), (12, 12, 170, 40), border_radius=10)
        screen.blit(f1.render(m["name"], True, (242, 184, 75)), (26, 22))
        hint = {"village": "Head east to leave the village",
                "forest": f"Rival: {RIVALS[sv['tier']][0]}. Cross the bridges" if rival_on() else "The forest is quiet. The arena is east",
                "arena": "Step on the gold emblem to set up a match"}[key]
        pygame.draw.rect(screen, (20, 18, 31), (12, VH - 40, 600, 30), border_radius=8)
        screen.blit(f2.render(f"Arrows: move  ·  ESC: pause  ·  {hint}", True, (244, 239, 230)), (22, VH - 33))
        near = near_obj()
        if near and not talk:
            px, py = near["pos"][0] * T - cx + 20, near["pos"][1] * T - cy - 16
            pygame.draw.rect(screen, (20, 18, 31), (px - 34, py - 12, 68, 24), border_radius=8)
            screen.blit(f2.render("Enter", True, (242, 184, 75)), (px - 20, py - 8))
        if talk: dialogue(screen, f1, f2, talk[0], talk[1], talk[2])
        pygame.display.flip()
        clock.tick(60)
