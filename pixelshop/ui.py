"""Shared Item Shop UI widgets: HUD, title card, wallet, dialog, stamps, coin streams."""
import math

import numpy as np

from . import sprites as S
from .gfx import back_out, ease_io, seg, text_w, wrap

SERIES = "ITEM SHOP"


def fmt_money(v):
    a = abs(v)
    if a >= 1e9:
        x = v / 1e9
        return f"${x:,.0f}B" if a >= 1e10 else f"${x:,.1f}B"
    if a >= 1e6:
        return f"${v / 1e6:,.1f}M"
    return f"${v:,.0f}"


def hud(cv, t, ep="001"):
    cv.blit(S.COIN[int(t * 6) % 3 if int(t * 6) % 6 < 3 else 0], 8, 5)
    cv.text(20, 6, SERIES, "gold")
    cv.text(cv.w - 8, 6, f"NO.{ep}", "gray", align="right")


def title(cv, lines, y=18, h=None, scale=2, fill="navy", color="white", accent=None):
    lh = 11 * scale
    h = h or (len(lines) * lh + 16)
    cv.window(8, y, cv.w - 16, h, fill=fill)
    for i, ln in enumerate(lines):
        c = accent.get(i, color) if accent else color
        cv.text(cv.w // 2, y + 10 + i * lh, ln, c, scale=scale, align="center")
    return y + h


def dialog(cv, text, t, t0, y=334, h=50, cps=30, color="white", fill="navy_d", speaker=None, scale=1):
    """Typewriter dialog box. Returns number of chars shown."""
    cv.window(8, y, cv.w - 16, h, fill=fill)
    if t < t0:
        return 0
    n = int((t - t0) * cps)
    max_chars = (cv.w - 16 - 14) // (6 * scale)
    lines = wrap(text, max_chars)
    shown, yy = n, y + 8
    if speaker:
        cv.text(16, yy, speaker, "gold")
        yy += 11
    for ln in lines:
        if shown <= 0:
            break
        cv.text(16, yy, ln[:shown], color, scale=scale)
        shown -= len(ln) + 1
        yy += 11 * scale
    if n >= len(text) and int(t * 3) % 2 == 0:  # "more" arrow
        cv.text(cv.w - 20, y + h - 12, ">", "gold", shadow=None)
    return n


def type_times(text, t0, cps=30, every=2):
    return [t0 + i / cps for i in range(0, len(text), every) if text[i] != " "]


def wallet(cv, y, name, sub, value, frac, h=46, warn=False):
    cv.window(8, y, cv.w - 16, h, fill="navy_d", border="gold" if not warn else "red")
    cv.blit(S.MONEYBAG, 16, y + 8)
    cv.text(36, y + 7, name, "white")
    if sub:
        cv.text(36, y + 17, sub, "gray")
    cv.text(cv.w - 16, y + 9, fmt_money(value), "red" if warn else "gold", scale=2, align="right")
    cv.bar(36, y + h - 15, cv.w - 52, 8, frac, fg="red" if warn else "gold",
           hi="white" if warn else "gold_l")


def stamp(cv, text, t, t0, color="red", scale=4, y=None, dur=None, outline="ink"):
    """Pop-in stamp text with a white flash frame."""
    if t < t0 or (dur is not None and t > t0 + dur):
        return
    p = seg(t, t0, t0 + 0.18)
    s = max(1, int(round(scale + (1 - back_out(p)) * 2)))
    y = cv.h // 2 - 20 if y is None else y
    w = text_w(text, s)
    x = cv.w // 2 - w // 2
    pad = 6
    cv.rect(x - pad - 2, y - pad - 2, w + 2 * pad + 4, 7 * s + 2 * pad + 4, "ink")
    cv.rect(x - pad, y - pad, w + 2 * pad, 7 * s + 2 * pad, "white" if t - t0 < 0.06 else color)
    cv.rect(x - pad + 2, y - pad + 2, w + 2 * pad - 4, 7 * s + 2 * pad - 4, "ink")
    cv.text(x, y, text, color if t - t0 >= 0.06 else "white", scale=s, shadow=None)


def coin_stream(cv, t, t0, t1, src, dst, rate=14, flight=0.55, arc=40, seed=1):
    """Coins launched from src to dst between t0 and t1. Returns list of arrival times."""
    n = int((t1 - t0) * rate)
    rng = np.random.default_rng(seed)
    jit = rng.uniform(-6, 6, (n, 2))
    arcs = rng.uniform(0.6, 1.2, n)
    for k in range(n):
        ts = t0 + k / rate
        p = (t - ts) / flight
        if 0 <= p <= 1:
            e = ease_io(p)
            x = src[0] + (dst[0] - src[0]) * e + jit[k, 0] * (1 - p)
            y = src[1] + (dst[1] - src[1]) * e - math.sin(math.pi * p) * arc * arcs[k] + jit[k, 1] * (1 - p)
            cv.blit(S.COIN[int((t * 12 + k) % 3)], x - 4, y - 4)
    return [t0 + k / rate + flight for k in range(n)]


def shake(cv, t, windows, amp=3):
    cv.ox = cv.oy = 0
    for t0, t1 in windows:
        if t0 <= t <= t1:
            k = 1 - (t - t0) / (t1 - t0)
            cv.ox = int(round(math.sin(t * 91) * amp * k))
            cv.oy = int(round(math.cos(t * 77) * amp * k))


def sources(cv, lines, y=392):
    for i, ln in enumerate(lines):
        cv.text(cv.w // 2, y + i * 10, ln, "gray", align="center")


def loop_wipe(cv, t, t0, t1, draw_hook):
    """Pixel wipe back into the hook frame so the reel loops cleanly."""
    if t < t0:
        return
    p = seg(t, t0, t1)
    from .gfx import Canvas
    hook = Canvas(cv.w, cv.h)
    draw_hook(hook)
    rows = int(cv.h * ease_io(p))
    if rows > 0:
        cv.a[:rows] = hook.a[:rows]
    edge = min(cv.h - 1, rows)
    cv.rect(0, edge - 1, cv.w, 2, "gold")
