"""Help screens: controls, elements and damage, fighters, agents."""
import math, pygame, sys
from ai.teams import POOL
from core import audio

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
WHITE, MUTED, GOLD, TEAL, PANEL = (244, 239, 230), (169, 165, 184), (242, 184, 75), (94, 194, 183), (32, 29, 48)
PAGES = ["Controls", "Elements and damage", "Fighters", "The AI agents"]


def arrow(scr, a, b, col=WHITE):
    dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
    p1, p2 = (a[0] + ux * 52, a[1] + uy * 52), (b[0] - ux * 52, b[1] - uy * 52)
    pygame.draw.line(scr, col, p1, p2, 4)
    px, py = -uy, ux
    pygame.draw.polygon(scr, col, [p2, (p2[0] - ux * 16 + px * 8, p2[1] - uy * 16 + py * 8), (p2[0] - ux * 16 - px * 8, p2[1] - uy * 16 - py * 8)])


def show_help(start=0):
    scr = pygame.display.set_mode((960, 540))
    ft, f1, f2 = (pygame.font.SysFont(None, n) for n in (46, 28, 22))
    clock = pygame.time.Clock()
    page = start
    audio.music("menu")
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_m: audio.toggle_mute()
                if e.key in (pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE): page = (page + 1) % len(PAGES); audio.sfx("move")
                if e.key == pygame.K_LEFT: page = (page - 1) % len(PAGES); audio.sfx("move")
        for k in range(18): pygame.draw.rect(scr, (13 + k * 3, 11 + k * 2, 31 + k * 4), (0, k * 30, 960, 30))
        scr.blit(ft.render(f"Help: {PAGES[page]}", True, GOLD), (28, 18))
        scr.blit(f2.render(f"Page {page + 1}/{len(PAGES)}   Left/Right: change page   ESC: close", True, MUTED), (28, 506))
        if page == 0:
            rows = [("Arrow keys", "Move around the map"), ("Enter / Space", "Talk to a villager or read a sign, then continue"),
                    ("ESC", "Pause menu on the map, or go back on other screens"), ("M", "Mute or unmute sound"),
                    ("Gold emblem", "Step on it in the arena to set up a match"), ("Forest rival", "Touch the rival to challenge them. Win to unlock fighters"),
                    ("Menu: AI Battle", "Set up any match between two agents"), ("Menu: Tournament", "Compare the algorithms on fair, mirrored matches")]
            for i, (k, v) in enumerate(rows):
                y = 90 + i * 50
                pygame.draw.rect(scr, PANEL, (28, y, 904, 42), border_radius=10)
                scr.blit(f1.render(k, True, TEAL), (44, y + 10)); scr.blit(f1.render(v, True, WHITE), (290, y + 10))
        elif page == 1:
            pos = {"Fire": (230, 150), "Earth": (350, 270), "Lightning": (230, 390), "Water": (110, 270)}
            order = ["Fire", "Earth", "Lightning", "Water"]
            for i in range(4): arrow(scr, pos[order[i]], pos[order[(i + 1) % 4]])
            for el, p in pos.items():
                pygame.draw.circle(scr, COL[el], p, 46)
                t = f2.render(el, True, (20, 18, 31) if el == "Lightning" else WHITE); scr.blit(t, (p[0] - t.get_width() // 2, p[1] - 8))
            lines = [("Arrows point to the weaker element.", MUTED), ("Fire beats Earth, Earth beats Lightning,", WHITE),
                     ("Lightning beats Water, Water beats Fire.", WHITE), ("", WHITE),
                     ("Damage = max(1, Attack × multiplier − Defense)", GOLD), ("Strong 1.5×   Neutral 1.0×   Weak 0.75×", WHITE), ("", WHITE),
                     ("Each turn a team attacks or switches fighters.", WHITE), ("Switching uses the turn.", WHITE),
                     ("A fainted fighter is replaced by the bench fighter.", WHITE), ("A team loses when both fighters faint.", WHITE)]
            for i, (t, c) in enumerate(lines): scr.blit(f1.render(t, True, c), (470, 100 + i * 34))
        elif page == 2:
            for j, h in enumerate(("Fighter", "Element", "HP", "ATK", "DEF")): scr.blit(f1.render(h, True, MUTED), (60 + [0, 300, 470, 590, 710][j], 84))
            for i, p in enumerate(POOL):
                y = 118 + i * 46
                pygame.draw.rect(scr, PANEL, (28, y, 904, 40), border_radius=10)
                pygame.draw.rect(scr, COL[p[4]], (28, y, 10, 40), border_radius=5)
                for j, v in enumerate((p[0], p[4], p[1], p[2], p[3])): scr.blit(f1.render(str(v), True, WHITE), (60 + [0, 300, 470, 590, 710][j], y + 9))
        else:
            rows = [("Alpha-Beta", "Searches Attack/Switch sequences 6 plies ahead and skips branches that cannot change the choice."),
                    ("Alpha-Beta+", "Same search, plus a smarter score (matchups, fighters alive) and best-move-first ordering."),
                    ("MCTS", "Plays many simulated battles from the current state and picks the most visited move."),
                    ("Greedy", "Attacks unless a bench switch is clearly better. No search at all."),
                    ("Random", "Picks any legal action. The baseline everything is compared with."),
                    ("A*", "Moves the forest rival along the shortest path around obstacles.")]
            for i, (k, v) in enumerate(rows):
                y = 84 + i * 68
                pygame.draw.rect(scr, PANEL, (28, y, 904, 60), border_radius=10)
                scr.blit(f1.render(k, True, TEAL), (44, y + 8))
                scr.blit(f2.render(v, True, WHITE), (44, y + 34))
        pygame.display.flip(); clock.tick(30)
