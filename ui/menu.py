"""Main menu."""
import pygame, sys
from ui.battle_ui import run
from ui.select_ui import select_match
from ui.tournament_ui import tournament
from ui.help_ui import show_help
from world.overworld import adventure
from core import audio

ITEMS = ["Adventure Mode", "AI Battle Mode", "Tournament Mode", "Help", "Quit"]


def main():
    pygame.init()
    size = (960, 540)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Arcanum Wars")
    title, font, small = (pygame.font.SysFont(None, n) for n in (80, 38, 24))
    clock = pygame.time.Clock()
    sel = 0

    def choose(i):
        nonlocal screen
        audio.sfx("select")
        if i == 0: adventure()
        elif i == 1:
            res = select_match()
            if res: run(res[1][0], res[1][1], res[0])
        elif i == 2: tournament()
        elif i == 3: show_help()
        elif i == 4: pygame.quit(); sys.exit()
        screen = pygame.display.set_mode(size)

    while True:
        audio.music("menu")
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w): sel = (sel - 1) % len(ITEMS); audio.sfx("move")
                elif e.key in (pygame.K_DOWN, pygame.K_s): sel = (sel + 1) % len(ITEMS); audio.sfx("move")
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE): choose(sel)
                elif e.key == pygame.K_m: audio.toggle_mute()
                elif pygame.K_1 <= e.key <= pygame.K_5: sel = e.key - pygame.K_1; choose(sel)
        for k in range(18): pygame.draw.rect(screen, (13 + k * 3, 11 + k * 2, 31 + k * 5), (0, k * 30, 960, 30))
        t = title.render("ARCANUM WARS", True, (242, 184, 75))
        screen.blit(t, (480 - t.get_width() // 2, 50))
        s = small.render("AI battles in a fantasy world", True, (169, 165, 184))
        screen.blit(s, (480 - s.get_width() // 2, 120))
        for i, txt in enumerate(ITEMS):
            r = pygame.Rect(280, 170 + i * 64, 400, 52)
            pygame.draw.rect(screen, (32, 29, 48), r, border_radius=12)
            pygame.draw.rect(screen, (242, 184, 75) if i == sel else (94, 194, 183), r, 4 if i == sel else 3, border_radius=12)
            f = font.render(f"{i + 1}   {txt}", True, (244, 239, 230))
            screen.blit(f, (r.centerx - f.get_width() // 2, r.centery - f.get_height() // 2))
        h = small.render("Up/Down + Enter, or press 1-5  ·  M: mute sound", True, (169, 165, 184))
        screen.blit(h, (480 - h.get_width() // 2, 506))
        pygame.display.flip()
        clock.tick(30)
