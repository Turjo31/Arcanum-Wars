"""In-game tournament screen: runs fair mirrored matches and fills a results table."""
import pygame, sys, itertools
from ai import battle
from ai.tournament import PLAYERS, UI_PLAYERS, match
from core import audio


def avg(l): return 1000 * sum(l) / max(1, len(l))


def tournament(games=20):
    scr = pygame.display.set_mode((960, 540))
    title, f1, f2 = (pygame.font.SysFont(None, n) for n in (46, 24, 20))
    clock = pygame.time.Clock()
    pairs = list(itertools.combinations(UI_PLAYERS, 2))
    rows, i = [], 0
    cols = (24, 290, 390, 520, 700)
    audio.music("arena")
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m: audio.toggle_mute()
        for k in range(18): pygame.draw.rect(scr, (13 + k * 3, 11 + k * 2, 31 + k * 4), (0, k * 30, 960, 30))
        scr.blit(title.render("Tournament", True, (242, 184, 75)), (24, 12))
        for x, h in zip(cols, ("Match-up", "W - L", "ms / move", "Nodes / pruned", "Win bar")):
            scr.blit(f2.render(h, True, (169, 165, 184)), (x, 62))
        for n, (a, b, r) in enumerate(rows):
            y = 88 + n * 39
            pygame.draw.rect(scr, (32, 29, 48), (14, y - 4, 932, 34), border_radius=8)
            scr.blit(f1.render(f"{a} vs {b}", True, (244, 239, 230)), (cols[0], y + 3))
            scr.blit(f1.render(f"{r['w1']} - {r['w2']}", True, (244, 239, 230)), (cols[1], y + 3))
            scr.blit(f2.render(f"{avg(r['t1']):.1f} vs {avg(r['t2']):.1f}", True, (244, 239, 230)), (cols[2], y + 5))
            scr.blit(f2.render(f"{r['nodes']} / {r['pruned']}", True, (244, 239, 230)), (cols[3], y + 5))
            bw, x = 220, cols[4]
            for cnt, col in ((r["w1"], (94, 194, 183)), (r["draw"], (138, 134, 153)), (r["w2"], (230, 90, 70))):
                w = bw * cnt / games
                if w: pygame.draw.rect(scr, col, (x, y + 2, w, 22)); x += w
        done = i >= len(pairs)
        msg = "Done. First move alternates each game. Teal = first algorithm, red = second. ESC to return." if done else f"Running {pairs[i][0]} vs {pairs[i][1]}...  ({i + 1}/{len(pairs)})"
        scr.blit(f2.render(msg, True, (242, 184, 75) if not done else (169, 165, 184)), (24, 508))
        pygame.display.flip()
        if not done:
            a, b = pairs[i]
            battle.STATS[:] = [0, 0]
            r = match(a, b, games)
            r["nodes"], r["pruned"] = battle.STATS
            rows.append((a, b, r)); i += 1
            audio.sfx("move")
        clock.tick(30)
