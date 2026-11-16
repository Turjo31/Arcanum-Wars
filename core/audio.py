"""Sound effects and music. Safe to call even when no audio device exists."""
import pygame
from core import synth

_state = {"ok": None, "muted": False, "music": None, "sounds": {}}


def init():
    if _state["ok"] is not None: return _state["ok"]
    try:
        synth.ensure()
        pygame.mixer.init(synth.SR, -16, 1, 512)
        _state["ok"] = True
    except Exception:
        _state["ok"] = False
    return _state["ok"]


def sfx(name, vol=0.6):
    if not init() or _state["muted"]: return
    try:
        snd = _state["sounds"].get(name)
        if snd is None:
            snd = _state["sounds"][name] = pygame.mixer.Sound(str(synth.DIR / f"{name}.wav"))
        snd.set_volume(vol); snd.play()
    except Exception:
        pass


def music(name):
    if not init() or _state["music"] == name: return
    _state["music"] = name
    try:
        pygame.mixer.music.load(str(synth.DIR / f"music_{name}.wav"))
        pygame.mixer.music.set_volume(0.0 if _state["muted"] else 0.3)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


def toggle_mute():
    _state["muted"] = not _state["muted"]
    if init():
        try: pygame.mixer.music.set_volume(0.0 if _state["muted"] else 0.3)
        except Exception: pass
    return _state["muted"]


def is_muted(): return _state["muted"]
