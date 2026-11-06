import pygame, sys, subprocess
from battle_ui import run

ITEMS = ["1  AI Battle (AlphaBeta vs MCTS)", "2  Tournament (close the chart to return)", "3  Quit"]

def main():
    pygame.init()
    screen = pygame.display.set_mode((760, 460))
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    run()
                    screen = pygame.display.set_mode((760, 460))
                elif e.key == pygame.K_2:
                    subprocess.run([sys.executable, "tournament.py"])
                elif e.key == pygame.K_3:
                    pygame.quit(); sys.exit()
        screen.fill((25, 25, 35))
        screen.blit(font.render("ARCANUM WARS", True, (255, 255, 0)), (280, 60))
        for i, t in enumerate(ITEMS):
            screen.blit(font.render(t, True, (255, 255, 255)), (120, 160 + i * 60))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()