"""Generates all sound effects and music loops as WAV files (pure Python, no assets needed)."""
import math, random, struct, wave, pathlib

SR = 22050
DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "sounds"


def write(name, samples):
    DIR.mkdir(parents=True, exist_ok=True)
    peak = max(1e-9, max(abs(x) for x in samples))
    scale = 0.9 * 32767 / max(peak, 1.0) if peak > 1.0 else 32767 * 0.9
    with wave.open(str(DIR / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 32767 * 0.9)) for x in samples))


def osc(kind, ph):
    ph %= 1.0
    if kind == "square": return 1.0 if ph < 0.5 else -1.0
    if kind == "pulse": return 1.0 if ph < 0.25 else -1.0
    if kind == "tri": return 4 * abs(ph - 0.5) - 1
    if kind == "saw": return 2 * ph - 1
    return math.sin(2 * math.pi * ph)


def add_note(buf, t0, freq, dur, vol, kind="square", decay=6.0, f_end=None):
    start = int(t0 * SR); n = int(dur * SR)
    ph = 0.0
    for i in range(n):
        if start + i >= len(buf): break
        t = i / SR
        f = freq if f_end is None else freq + (f_end - freq) * (i / n)
        ph += f / SR
        env = min(1.0, t / 0.004) * math.exp(-decay * t / max(dur, 1e-3))
        buf[start + i] += osc(kind, ph) * vol * env


def add_noise(buf, t0, dur, vol, decay=8.0, rn=random.Random(1)):
    start = int(t0 * SR); n = int(dur * SR)
    for i in range(n):
        if start + i >= len(buf): break
        buf[start + i] += (rn.random() * 2 - 1) * vol * math.exp(-decay * i / n)


def midi(n): return 440.0 * 2 ** ((n - 69) / 12)


def sfx():
    out = {}
    b = [0.0] * int(0.2 * SR); add_noise(b, 0, 0.18, 0.7); add_note(b, 0, 140, 0.15, 0.6, "sine", 10); out["hit"] = b
    b = [0.0] * int(0.35 * SR); add_noise(b, 0, 0.2, 0.7); add_note(b, 0, 120, 0.2, 0.6, "sine", 10); add_note(b, 0.02, 700, 0.25, 0.35, "square", 7, 1400); out["crit"] = b
    b = [0.0] * int(0.6 * SR); add_note(b, 0, 420, 0.55, 0.45, "square", 4, 70); out["faint"] = b
    b = [0.0] * int(0.3 * SR); add_noise(b, 0, 0.25, 0.4, 3); add_note(b, 0, 300, 0.25, 0.25, "tri", 3, 900); out["switch"] = b
    b = [0.0] * int(0.12 * SR); add_note(b, 0, 660, 0.1, 0.4, "square", 7); out["select"] = b
    b = [0.0] * int(0.07 * SR); add_note(b, 0, 440, 0.05, 0.3, "square", 8); out["move"] = b
    b = [0.0] * int(0.9 * SR)
    for i, n in enumerate((72, 76, 79, 84)): add_note(b, i * 0.14, midi(n), 0.3, 0.4, "tri", 3)
    out["win"] = b
    b = [0.0] * int(1.0 * SR)
    for i, n in enumerate((67, 64, 60, 57)): add_note(b, i * 0.2, midi(n), 0.35, 0.4, "tri", 3)
    out["lose"] = b
    b = [0.0] * int(1.1 * SR)
    for i, n in enumerate((76, 79, 83, 88, 91)): add_note(b, i * 0.09, midi(n), 0.35, 0.3, "tri", 3); add_note(b, i * 0.09 + 0.12, midi(n), 0.3, 0.12, "tri", 4)
    out["unlock"] = b
    for k, v in out.items(): write(k, v)


def track(name, bpm, chords, pattern, melody_kind="square", drums=False, bars=8, mel_vol=0.16, bass_vol=0.3):
    beat = 60.0 / bpm; total = bars * 4 * beat
    buf = [0.0] * int(total * SR)
    for bar in range(bars):
        root, ivs = chords[bar % len(chords)]
        t0 = bar * 4 * beat
        add_note(buf, t0, midi(root - 12), 2 * beat * 0.95, bass_vol, "tri", 2)
        add_note(buf, t0 + 2 * beat, midi(root - 12 + (7 if bar % 2 else 0)), 2 * beat * 0.95, bass_vol, "tri", 2)
        for k, step in enumerate(pattern):
            if step is None: continue
            idx, octv = step
            note = root + ivs[idx % len(ivs)] + 12 * octv
            add_note(buf, t0 + k * beat / 2, midi(note), beat / 2 * 0.9, mel_vol, melody_kind, 5)
        if drums:
            for q in range(4):
                tq = t0 + q * beat
                if q % 2 == 0: add_note(buf, tq, 120, 0.12, 0.45, "sine", 9, 45)
                else: add_noise(buf, tq, 0.1, 0.22, 10)
                add_noise(buf, tq + beat / 2, 0.04, 0.07, 14)
    write(name, buf)


MAJ, MIN = [0, 4, 7, 12], [0, 3, 7, 12]


def music():
    track("music_menu", 84, [(60, MAJ), (65, MAJ), (67, MAJ), (57, MIN)], [(0, 1), None, (1, 1), None, (2, 1), None, (1, 1), None], "tri", mel_vol=0.22)
    track("music_village", 112, [(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ), (57, MIN), (65, MAJ), (67, MAJ), (60, MAJ)],
          [(0, 1), (1, 1), (2, 1), (1, 1), (0, 1), (1, 1), (3, 1), None])
    track("music_forest", 78, [(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], [(0, 1), None, (1, 1), None, (2, 1), None, (1, 1), (0, 1)], "pulse", mel_vol=0.15)
    track("music_arena", 128, [(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], [(0, 1), (2, 1), (1, 1), (2, 1), (3, 1), (2, 1), (1, 1), (0, 1)], "square", drums=True, mel_vol=0.14)
    track("music_battle", 150, [(64, MIN), (60, MAJ), (62, MAJ), (59, MIN)], [(0, 1), (1, 1), (2, 1), (3, 1), (2, 1), (1, 1), (2, 1), (1, 1)], "saw", drums=True, mel_vol=0.1)


def ensure():
    need = ["hit", "crit", "faint", "switch", "select", "move", "win", "lose", "unlock",
            "music_menu", "music_village", "music_forest", "music_arena", "music_battle"]
    if all((DIR / f"{n}.wav").exists() for n in need): return
    sfx(); music()


if __name__ == "__main__":
    sfx(); music(); print("sounds written to", DIR)
