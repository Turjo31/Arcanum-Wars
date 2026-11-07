import pygame, sys, subprocess
from battle_ui import run
from overworld import adventure

ITEMS = ["1   Adventure Mode", "2   AI Battle Mode", "3   Tournament Mode", "4   Quit"]

def main():
    pygame.init()
    size = (960, 540)
    screen = pygame.display.set_mode(size)
    title, font, small = (pygame.font.SysFont(None, n) for n in (72, 38, 24))
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: adventure()
                elif e.key == pygame.K_2: run()
                elif e.key == pygame.K_3: subprocess.run([sys.executable, "tournament.py"])
                elif e.key == pygame.K_4: pygame.quit(); sys.exit()
                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3): screen = pygame.display.set_mode(size)
        for k in range(18): pygame.draw.rect(screen, (13 + k * 3, 11 + k * 2, 31 + k * 5), (0, k * 30, 960, 30))
        t = title.render("ARCANUM WARS", True, (242, 184, 75))
        screen.blit(t, (480 - t.get_width() // 2, 70))
        s = small.render("AI battles in a fantasy world", True, (169, 165, 184))
        screen.blit(s, (480 - s.get_width() // 2, 135))
        for i, txt in enumerate(ITEMS):
            r = pygame.Rect(280, 200 + i * 70, 400, 54)
            pygame.draw.rect(screen, (32, 29, 48), r, border_radius=12)
            pygame.draw.rect(screen, (242, 184, 75) if i == 0 else (94, 194, 183), r, 3, border_radius=12)
            f = font.render(txt, True, (244, 239, 230))
            screen.blit(f, (r.centerx - f.get_width() // 2, r.centery - f.get_height() // 2))
        h = small.render("Press 1-4 to choose  ·  ESC returns to menu", True, (169, 165, 184))
        screen.blit(h, (480 - h.get_width() // 2, 500))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()