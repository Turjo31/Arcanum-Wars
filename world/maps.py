"""Tile maps (village, forest, arena) and their rendering."""
import pygame, random

T = 40
BLOCK = set("TR~MOCXWHN")
BASE = {"village": (88, 162, 76), "forest": (43, 96, 52), "arena": (216, 192, 138)}


def mk(w, h, ch): return [[ch] * w for _ in range(h)]


def fill(g, x, y, w, h, ch):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= yy < len(g) and 0 <= xx < len(g[0]): g[yy][xx] = ch


def carve(g, pts, width=3):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if y1 == y2: fill(g, min(x1, x2), y1 - width // 2, abs(x2 - x1) + 1, width, "P")
        else: fill(g, x1 - width // 2, min(y1, y2), width, abs(y2 - y1) + 1, "P")


def scatter(g, ch, p, rn, only="."):
    for y in range(len(g)):
        for x in range(len(g[0])):
            if g[y][x] in only and rn.random() < p: g[y][x] = ch


def village():
    rn = random.Random(11); g = mk(40, 24, ".")
    fill(g, 0, 0, 40, 2, "T"); fill(g, 0, 22, 40, 2, "T"); fill(g, 0, 0, 1, 24, "T"); fill(g, 39, 0, 1, 24, "T")
    scatter(g, "T", 0.05, rn)
    carve(g, [(1, 12), (38, 12)]); carve(g, [(19, 2), (19, 21)]); fill(g, 16, 9, 8, 7, "P"); fill(g, 39, 11, 1, 3, "P")
    houses = [(4, 3, 4, 3, (181, 72, 47)), (10, 3, 5, 3, (60, 111, 181)), (25, 3, 5, 3, (122, 74, 181)), (32, 3, 4, 3, (181, 72, 47)),
              (4, 16, 4, 3, (60, 111, 181)), (10, 16, 5, 3, (181, 72, 47)), (26, 16, 4, 3, (122, 74, 181)), (32, 16, 5, 3, (60, 111, 181))]
    for hx, hy, hw, hh, _ in houses:
        fill(g, hx, hy, hw, hh, "H"); dx = hx + hw // 2
        if hy < 12: carve(g, [(dx, hy + hh), (dx, 10)], 1)
        else: carve(g, [(dx, 14), (dx, hy - 1)], 1)
    for x in (17, 18, 21, 22): g[9][x] = "M"
    g[12][19] = "O"; fill(g, 22, 18, 4, 4, "~"); g[10][36] = "N"
    scatter(g, "F", 0.07, rn)
    return dict(name="Village", theme="village", g=g, houses=houses, exits=[((39, 11, 1, 3), "forest", (1, 14))], spawn=(3, 12), npc=None)


def forest():
    rn = random.Random(21); g = mk(50, 30, ".")
    scatter(g, "T", 0.5, rn)
    fill(g, 0, 0, 50, 1, "T"); fill(g, 0, 29, 50, 1, "T"); fill(g, 0, 0, 1, 30, "T"); fill(g, 49, 0, 1, 30, "T")
    fill(g, 24, 0, 2, 30, "~"); fill(g, 36, 5, 5, 3, "~")
    carve(g, [(0, 14), (10, 14), (10, 8), (20, 8), (20, 14), (34, 14), (34, 22), (42, 22), (42, 14), (49, 14)])
    carve(g, [(10, 14), (10, 24), (34, 24), (34, 22)]); carve(g, [(20, 8), (20, 3), (30, 3)]); carve(g, [(42, 22), (42, 27), (46, 27)])
    fill(g, 27, 10, 9, 3, ".")
    for by in (2, 13, 23): fill(g, 24, by, 2, 3, "B")

    def ok():
        q, seen = [(1, 14)], {(1, 14)}
        for x, y in q:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and 0 <= n[0] < 50 and 0 <= n[1] < 30 and g[n[1]][n[0]] not in BLOCK: seen.add(n); q.append(n)
        return (48, 14) in seen

    for y in range(30):
        for x in range(5, 45):
            if g[y][x] == "P" and rn.random() < 0.12:
                g[y][x] = "R"
                if not ok(): g[y][x] = "P"
    return dict(name="Forest", theme="forest", g=g, houses=[], exits=[((0, 13, 1, 3), "village", (38, 12)), ((49, 13, 1, 3), "arena", (1, 10))], spawn=(1, 14), npc=(34, 14))


def arena():
    g = mk(30, 20, "S")
    fill(g, 0, 0, 30, 3, "X"); fill(g, 0, 17, 30, 3, "X"); fill(g, 0, 3, 30, 1, "W"); fill(g, 0, 16, 30, 1, "W")
    fill(g, 0, 3, 1, 14, "W"); fill(g, 29, 3, 1, 14, "W"); fill(g, 0, 9, 1, 2, "S"); fill(g, 13, 9, 2, 2, "E")
    for x, y in ((8, 6), (21, 6), (8, 13), (21, 13)): g[y][x] = "C"
    return dict(name="Arena", theme="arena", g=g, houses=[], exits=[((0, 9, 1, 2), "forest", (47, 14))], spawn=(1, 10), npc=None)


def R(s, c, x, y, w, h): pygame.draw.rect(s, c, (int(x), int(y), int(w), int(h)))


def draw_tile(s, ch, x, y, rn, theme):
    px, py = x * T, y * T
    base = {"P": (170, 135, 90) if theme == "forest" else (207, 168, 110), "B": (150, 110, 70), "~": (60, 120, 200), "X": (59, 53, 88),
            "W": (138, 134, 153), "S": (216, 192, 138) if (x + y) % 2 else (222, 198, 146), "E": (226, 196, 120)}.get(ch, BASE[theme])
    R(s, base, px, py, T, T)
    dark = tuple(max(0, v - 12) for v in base)
    if ch in ".TRFMONHP":
        for _ in range(3): R(s, dark, px + rn.randint(0, 34), py + rn.randint(0, 36), 5, 3)
    if ch == "B":
        for k in range(0, T, 10): R(s, (110, 76, 44), px, py + k, T, 2)
    if ch == "F":
        for _ in range(3): pygame.draw.circle(s, rn.choice([(244, 166, 200), (242, 216, 75), (255, 255, 255)]), (px + rn.randint(5, 35), py + rn.randint(5, 35)), 3)
    if ch == "T":
        d, m, l = ((22, 70, 34), (32, 100, 46), (46, 130, 60)) if theme == "forest" else ((30, 90, 44), (42, 122, 58), (60, 154, 74))
        R(s, (107, 74, 43), px + 16, py + 26, 8, 14); R(s, d, px + 2, py + 12, 36, 18); R(s, m, px + 8, py + 2, 24, 16); R(s, l, px + 10, py + 8, 10, 8)
    if ch == "R":
        pygame.draw.ellipse(s, (138, 134, 153), (px + 5, py + 14, 30, 22)); pygame.draw.ellipse(s, (169, 165, 181), (px + 10, py + 17, 14, 8))
    if ch == "W":
        R(s, (169, 165, 181), px, py, T, 8); R(s, (112, 108, 128), px, py + 20, T, 2)
        for k in range(0, T, 20): R(s, (112, 108, 128), px + k, py + 20, 2, 20)
    if ch == "X":
        for dx in (10, 30): pygame.draw.circle(s, rn.choice([(230, 90, 46), (60, 140, 255), (140, 100, 50), (232, 197, 46), (244, 239, 230)]), (px + dx, py + rn.randint(10, 30)), 9)
    if ch == "M":
        R(s, (160, 110, 60), px + 2, py + 18, 36, 18); R(s, (200, 70, 60), px, py + 4, T, 14); R(s, (244, 239, 230), px, py + 4, 10, 14); R(s, (244, 239, 230), px + 20, py + 4, 10, 14)
    if ch == "O":
        pygame.draw.ellipse(s, (154, 150, 168), (px + 3, py + 10, 34, 26)); pygame.draw.ellipse(s, (58, 110, 165), (px + 9, py + 15, 22, 14)); R(s, (107, 74, 43), px + 4, py + 2, 4, 20); R(s, (107, 74, 43), px + 32, py + 2, 4, 20)
    if ch == "C":
        pygame.draw.ellipse(s, (0, 0, 0), (px + 6, py + 32, 28, 8)); R(s, (138, 134, 153), px + 10, py + 6, 20, 32); R(s, (169, 165, 181), px + 6, py, 28, 8)
    if ch == "N":
        R(s, (107, 74, 43), px + 6, py + 22, 5, 16); R(s, (107, 74, 43), px + 29, py + 22, 5, 16); R(s, (150, 104, 60), px + 2, py + 4, 36, 22)
        R(s, (244, 239, 230), px + 7, py + 9, 12, 8); R(s, (244, 239, 230), px + 22, py + 9, 11, 8)


def house(s, x, y, w, h, col):
    px, py, pw, ph = x * T, y * T, w * T, h * T
    R(s, (230, 211, 168), px, py + ph * 0.4, pw, ph * 0.6); R(s, (107, 74, 43), px + pw / 2 - 10, py + ph - 34, 20, 34)
    R(s, (142, 202, 230), px + 10, py + ph * 0.55, 14, 14); R(s, (142, 202, 230), px + pw - 24, py + ph * 0.55, 14, 14)
    pygame.draw.polygon(s, col, [(px - 8, py + ph * 0.45), (px + pw / 2, py - 8), (px + pw + 8, py + ph * 0.45)])
    R(s, (138, 134, 153), px + pw * 0.7, py + 4, 10, 20)


def render(m):
    g = m["g"]; s = pygame.Surface((len(g[0]) * T, len(g) * T)); rn = random.Random(5)
    for y, row in enumerate(g):
        for x, ch in enumerate(row): draw_tile(s, ch, x, y, rn, m["theme"])
    for hx, hy, hw, hh, col in m["houses"]: house(s, hx, hy, hw, hh, col)
    if m["theme"] == "arena":
        cx, cy = 14 * T, 10 * T
        pygame.draw.circle(s, (176, 104, 15), (cx, cy), 62, 6); pygame.draw.circle(s, (242, 184, 75), (cx, cy), 34, 4)
        pygame.draw.polygon(s, (242, 184, 75), [(cx, cy - 24), (cx + 8, cy - 8), (cx + 24, cy - 6), (cx + 12, cy + 6), (cx + 16, cy + 22), (cx, cy + 12), (cx - 16, cy + 22), (cx - 12, cy + 6), (cx - 24, cy - 6), (cx - 8, cy - 8)])
    return s


def person(s, px, py, body, hair, step):
    pygame.draw.ellipse(s, (30, 60, 30), (px + 8, py + 34, 24, 7))
    R(s, (58, 53, 80), px + 13, py + 26 - step, 6, 9); R(s, (58, 53, 80), px + 21, py + 26 + step, 6, 9)
    R(s, body, px + 11, py + 14, 18, 14); R(s, body, px + 7, py + 15, 5, 10); R(s, body, px + 28, py + 15, 5, 10)
    R(s, (242, 201, 160), px + 13, py + 3, 14, 12); R(s, hair, px + 13, py + 1, 14, 6)
    R(s, (34, 34, 34), px + 17, py + 8, 2, 2); R(s, (34, 34, 34), px + 22, py + 8, 2, 2)
