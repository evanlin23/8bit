"""Pacing lint: flag dead air (no visual change and no sound event) and silent stretches."""
import numpy as np

from . import audio
from .gfx import Canvas

FPS = 30


class _RecTrack(audio.Track):
    def __init__(self, seconds):
        super().__init__(seconds)
        self.times = []

    def add(self, t, sig, gain=1.0):
        if gain > 0.02:
            self.times.append(t)
        super().add(t, sig, gain)


def lint(reel, gap_max=0.7, step=0.1, vis_px=450, silence_rms=0.02):
    # visual events: compare frames `step` seconds apart (idle sparkles change only a few pixels)
    cv = Canvas()
    vis = []
    prev = None
    n = int(round(reel.seconds / step))
    for i in range(n + 1):
        t = min(i * step, reel.seconds - 1e-3)
        reel.draw(cv, t)
        cur = cv.a.copy()
        if prev is not None and np.any(cur != prev, axis=2).sum() > vis_px:
            vis.append(t)
        prev = cur
    tr = _RecTrack(reel.seconds)
    reel.sfx(tr)
    events = sorted(set([0.0, reel.seconds] + vis + [round(x, 3) for x in tr.times]))
    gaps = [(a, b) for a, b in zip(events, events[1:]) if b - a > gap_max]

    # silence in the final mix
    music = reel.music()
    m = np.zeros(int(reel.seconds * audio.SR))
    m[: min(len(m), len(music))] = music[: len(m)] * reel.music_gain
    s = tr.buf[: len(m)]
    mix = m + np.pad(s, (0, len(m) - len(s)))
    w = int(0.25 * audio.SR)
    peak = np.percentile(np.abs(mix), 99.7) or 1
    silent = [i * 0.25 for i in range(len(mix) // w)
              if np.sqrt(np.mean((mix[i * w:(i + 1) * w] / peak) ** 2)) < silence_rms]
    a0, a1 = Canvas(), Canvas()
    reel.draw(a0, 0.0)
    reel.draw(a1, reel.seconds - 1.0 / FPS)
    loop_px = int(np.any(a0.a != a1.a, axis=2).sum())
    return dict(gaps=gaps, silent=silent, n_visual=len(vis), n_sfx=len(tr.times), loop_px=loop_px)


def report(name, r):
    ok = not r["gaps"] and not r["silent"] and r["loop_px"] <= 400
    print(f"[{'OK ' if ok else 'FAIL'}] {name}: {r['n_visual']} visual beats, {r['n_sfx']} sound events, "
          f"loop seam {r['loop_px']} px changed")
    for a, b in r["gaps"]:
        print(f"    dead air {a:.2f}-{b:.2f}s ({b - a:.2f}s)")
    if r["silent"]:
        print(f"    silent windows at: {', '.join(f'{t:.2f}' for t in r['silent'])}")
    return ok
