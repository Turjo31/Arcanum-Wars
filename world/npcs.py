"""Villagers, signs and the dialogue box."""
import pygame
from ai.teams import RIVALS
from ai.agents import label

VW, VH = 960, 520

NPCS = [
    dict(name="Trainer Mira", pos=(21, 13), body=(94, 194, 183), hair=(58, 42, 26), lines=[
        "Welcome, traveler! In the arena, two AI agents battle for you.",
        "Alpha-Beta looks 6 moves ahead and skips branches that cannot change its decision.",
        "MCTS plays hundreds of random games and picks the move that wins most often.",
        "Try both in the arena and watch the thinking panel."]),
    dict(name="Elder Odo", pos=(14, 11), body=(150, 120, 200), hair=(220, 220, 230), lines=[
        "Fire beats Earth, Earth beats Lightning, Lightning beats Water, and Water beats Fire.",
        "A strong matchup deals 1.5 times damage. A weak one only 0.75 times.",
        "Defense is subtracted from every hit, so tanks like Earth Golem take very little.",
        "Switching costs a turn, so only switch when the matchup is bad."]),
    dict(name="Recruiter Finn", pos=(24, 13), body=(242, 184, 75), hair=(122, 59, 46), lines=[
        "Tide Guard has 120 HP and 8 defense. Hard to hurt, but slow to win.",
        "Flame Archer hits hard with 28 attack, but has only 80 HP.",
        "Earth Golem has 130 HP and 10 defense. A real tank.",
        "Beat the rivals in the forest and I will let you recruit fighters you have not met yet."]),
    dict(name="Villager Lena", pos=(28, 11), body=(244, 166, 200), hair=(58, 42, 26), lines=[
        "The forest rivals chase you with A*, a shortest-path algorithm.",
        "They are slower than you, so use the bridges and outrun them if you are not ready.",
        "Beat the arena for practice, then come back and try another team."]),
]
ARENA_NPCS = [
    dict(name="Arena Master", pos=(11, 12), body=(230, 90, 46), hair=(20, 18, 31), lines=[
        "Step on the gold emblem to set up a match between any two agents.",
        "You can pick the fighters, the algorithm for each side, and who moves first.",
        "Pair a deep Alpha-Beta against a small MCTS to see how search depth changes the fight."]),
]


def board_lines(sv):
    tier = sv["tier"]
    nxt = f"Next rival: {RIVALS[tier][0]} ({label(RIVALS[tier][2])})." if tier < len(RIVALS) else "You are the champion of the forest!"
    return [f"Rivals defeated: {tier} of {len(RIVALS)}.", f"Fighters unlocked: {len(sv['unlocked'])} of 8.", nxt,
            "Beating a rival unlocks a new fighter for the next fights."]


SIGNS = {"village": [dict(name="Notice Board", pos=(36, 10), lines=board_lines, sign=True)]}


def wrap(font, text, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.size(t)[0] <= width: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]


def dialogue(screen, f1, f2, obj, lines, i):
    r = pygame.Rect(30, VH - 150, 900, 142)
    pygame.draw.rect(screen, (20, 18, 31), r, border_radius=16)
    pygame.draw.rect(screen, (242, 184, 75), r, 3, border_radius=16)
    screen.blit(f1.render(obj["name"], True, (242, 184, 75)), (r.x + 22, r.y + 14))
    for k, line in enumerate(wrap(f2, lines[i], 850)[:3]):
        screen.blit(f2.render(line, True, (244, 239, 230)), (r.x + 22, r.y + 52 + k * 26))
    tip = f"Enter: next ({i + 1}/{len(lines)})" if i + 1 < len(lines) else "Enter: close"
    screen.blit(f2.render(tip, True, (169, 165, 184)), (r.right - 22 - f2.size(tip)[0], r.bottom - 30))


def message_panel(screen, f1, f2, title, lines, sub="Press Enter to continue"):
    """Blocking centered panel. Returns when Enter/Space/ESC is pressed."""
    import sys
    base = screen.copy(); clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE): return
        screen.blit(base, (0, 0))
        r = pygame.Rect(130, 120, 700, 60 + 34 * len(lines) + 60)
        pygame.draw.rect(screen, (20, 18, 31), r, border_radius=16)
        pygame.draw.rect(screen, (242, 184, 75), r, 3, border_radius=16)
        t = pygame.font.SysFont(None, 46).render(title, True, (242, 184, 75)); screen.blit(t, (480 - t.get_width() // 2, r.y + 16))
        for k, line in enumerate(lines): screen.blit(f1.render(line, True, (244, 239, 230)), (r.x + 30, r.y + 70 + k * 34))
        screen.blit(f2.render(sub, True, (169, 165, 184)), (r.right - 30 - f2.size(sub)[0], r.bottom - 32))
        pygame.display.flip(); clock.tick(30)
