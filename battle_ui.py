import pygame, sys
from battle import apply, winner, best
from mcts import mcts
from tournament import START

COL = {"Fire": (230, 80, 40), "Water": (60, 140, 255), "Earth": (140, 100, 50), "Lightning": (240, 210, 50)}
AI = {"AlphaBeta": lambda s: best(s, 6, True), "MCTS": lambda s: mcts(s, 200)}

def draw(screen, font, s, log):
    screen.fill((25, 25, 35))
    teams, act, t = s
    for side in (0, 1):
        x = 40 + side * 400
        screen.blit(font.render(f"Team {side + 1}" + ("  <" if t == side else ""), True, (255, 255, 255)), (x, 20))
        for i, (hp, atk, df, el) in enumerate(teams[side]):
            y = 70 + i * 110
            pygame.draw.rect(screen, COL[el], (x, y, 280, 90), 0 if act[side] == i else 3)
            screen.blit(font.render(el, True, (255, 255, 255)), (x + 10, y + 12))
            screen.blit(font.render(f"HP {hp}  ATK {atk}  DEF {df}", True, (255, 255, 255)), (x + 10, y + 50))
    for i, line in enumerate(log[-4:]):
        screen.blit(font.render(line, True, (200, 200, 200)), (40, 320 + i * 28))

def run(n1="AlphaBeta", n2="MCTS"):
    pygame.init()
    screen = pygame.display.set_mode((760, 460))
    font = pygame.font.SysFont(None, 28)
    clock = pygame.time.Clock()
    s, log, last, turns = START, [], 0, 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        now = pygame.time.get_ticks()
        w = winner(s)
        if w is None and turns < 60 and now - last > 700:
            a = AI[(n1, n2)[s[2]]](s)
            log.append(f"Team {s[2] + 1}: {'Attack' if a == 'A' else 'Switch'}")
            s = apply(s, a)
            turns += 1
            last = now
        draw(screen, font, s, log)
        if w is not None:
            screen.blit(font.render(f"Team {w + 1} wins!", True, (255, 255, 0)), (300, 420))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    run()