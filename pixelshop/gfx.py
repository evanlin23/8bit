"""Low-res pixel canvas, bitmap font, RPG-style windows and CRT post-processing.

Everything is drawn on a 270x480 virtual screen and upscaled 4x to 1080x1920,
so every element (text, sprites, particles) snaps to the same pixel grid.
"""
import numpy as np

VW, VH = 270, 480
SCALE = 4

# ---------------------------------------------------------------- palette
PAL = {
    "bg0": (24, 12, 40), "bg1": (40, 18, 66), "bg2": (58, 26, 88),
    "ink": (10, 6, 18), "white": (255, 244, 224), "cream": (240, 222, 190),
    "gold": (255, 204, 51), "gold_d": (214, 140, 28), "gold_l": (255, 236, 140),
    "red": (255, 77, 90), "red_d": (150, 24, 48), "green": (86, 224, 122),
    "green_d": (34, 120, 70), "cyan": (95, 211, 232), "blue": (52, 120, 230),
    "navy": (20, 26, 74), "navy_d": (12, 14, 44), "gray": (150, 150, 168),
    "gray_d": (82, 82, 104), "purple": (142, 91, 214), "orange": (255, 138, 36),
}


def C(c):
    return PAL[c] if isinstance(c, str) else c


# ---------------------------------------------------------------- font (5x7)
_FONT_SRC = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.",
    "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    ".": ".....|.....|.....|.....|.....|.##..|.##..",
    ",": ".....|.....|.....|.....|.##..|..#..|.#...",
    "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "$": "..#..|.####|#.#..|.###.|..#.#|####.|..#..",
    "%": "##..#|##..#|...#.|..#..|.#...|#..##|#..##",
    "'": "..#..|..#..|.#...|.....|.....|.....|.....",
    '"': ".#.#.|.#.#.|.....|.....|.....|.....|.....",
    "-": ".....|.....|.....|.###.|.....|.....|.....",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...",
    "=": ".....|.....|#####|.....|#####|.....|.....",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    ">": "#....|##...|###..|####.|###..|##...|#....",
    "<": "....#|...##|..###|.####|..###|...##|....#",
    "x": ".....|.....|#...#|.#.#.|..#..|.#.#.|#...#",
    "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#",
    "~": ".....|.....|.#...|#.#.#|...#.|.....|.....",
    " ": ".....|.....|.....|.....|.....|.....|.....",
}
FONT = {k: np.array([[c == "#" for c in row] for row in v.split("|")], dtype=bool)
        for k, v in _FONT_SRC.items()}
_GLYPH_CACHE = {}


def glyph(ch, s):
    key = (ch, s)
    if key not in _GLYPH_CACHE:
        g = FONT.get(ch, FONT.get(ch.upper(), FONT["?"]))
        _GLYPH_CACHE[key] = np.kron(g, np.ones((s, s), dtype=bool))
    return _GLYPH_CACHE[key]


def text_w(s, scale=1):
    return max(0, len(s) * 6 * scale - scale)


def wrap(s, max_chars):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w=VW, h=VH):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 3), dtype=np.uint8)
        self.ox = self.oy = 0  # camera shake offset

    # -- primitives
    def fill(self, c):
        self.a[:] = C(c)

    def rect(self, x, y, w, h, c):
        x, y = int(x) + self.ox, int(y) + self.oy
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + int(w), self.w), min(y + int(h), self.h)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = C(c)

    def mask(self, m, x, y, c):
        x, y = int(x) + self.ox, int(y) + self.oy
        h, w = m.shape
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = m[y0 - y:y1 - y, x0 - x:x1 - x]
        self.a[y0:y1, x0:x1][sub] = C(c)

    def blit(self, spr, x, y, scale=1, flip=False, tint=None):
        """spr: (h, w, 4) uint8 with alpha 0/255."""
        if scale != 1:
            spr = np.repeat(np.repeat(spr, scale, 0), scale, 1)
        if flip:
            spr = spr[:, ::-1]
        x, y = int(x) + self.ox, int(y) + self.oy
        h, w = spr.shape[:2]
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = spr[y0 - y:y1 - y, x0 - x:x1 - x]
        m = sub[..., 3] > 0
        rgb = sub[..., :3] if tint is None else np.broadcast_to(np.array(C(tint), np.uint8), sub[..., :3].shape)
        self.a[y0:y1, x0:x1][m] = rgb[m]

    def blit_ghost(self, spr, x, y, scale=1, phase=0):
        """Dithered (50%) blit for see-through sprites."""
        if scale != 1:
            spr = np.repeat(np.repeat(spr, scale, 0), scale, 1)
        spr = spr.copy()
        h, w = spr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        spr[((xx + yy + phase) % 2) == 1, 3] = 0
        lum = spr[..., :3].astype(int).mean(-1, keepdims=True)
        spr[..., :3] = np.clip(lum * 0.4 + np.array([150, 220, 240]) * 0.6, 0, 255).astype(np.uint8)
        self.blit(spr, x, y)

    def text(self, x, y, s, c="white", scale=1, shadow="ink", align="left"):
        s = str(s)
        if align == "center":
            x = x - text_w(s, scale) // 2
        elif align == "right":
            x = x - text_w(s, scale)
        cx = x
        for ch in s:
            g = glyph(ch, scale)
            if shadow:
                self.mask(g, cx + scale, y + scale, shadow)
            self.mask(g, cx, y, c)
            cx += 6 * scale
        return x

    def dither(self, x, y, w, h, c, phase=0):
        x, y = int(x) + self.ox, int(y) + self.oy
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        yy, xx = np.mgrid[y0:y1, x0:x1]
        m = ((xx + yy + phase) % 2) == 0
        self.a[y0:y1, x0:x1][m] = C(c)

    def window(self, x, y, w, h, fill="navy", border="white", glow=None):
        """Classic RPG text window: black edge, light border, black gap, fill."""
        self.rect(x, y, w, h, "ink")
        self.rect(x + 1, y + 1, w - 2, h - 2, border)
        self.rect(x + 2, y + 2, w - 4, h - 4, "ink")
        self.rect(x + 3, y + 3, w - 6, h - 6, fill)
        if glow:
            self.rect(x + 3, y + 3, w - 6, 1, glow)

    def bar(self, x, y, w, h, frac, fg="gold", bg="navy_d", hi="gold_l"):
        self.rect(x, y, w, h, "ink")
        self.rect(x + 1, y + 1, w - 2, h - 2, bg)
        fw = int(round((w - 2) * max(0.0, min(1.0, frac))))
        if fw > 0:
            self.rect(x + 1, y + 1, fw, h - 2, fg)
            self.rect(x + 1, y + 1, fw, 1, hi)


# ---------------------------------------------------------------- background
def background(cv, t, seed=0):
    """Deep plum gradient with dithered bands and twinkling gold sparkles."""
    a = cv.a
    ys = np.linspace(0, 1, cv.h)[:, None]
    c0, c1 = np.array(PAL["bg0"], float), np.array(PAL["bg1"], float)
    grad = (c0 * (1 - ys) + c1 * ys)
    a[:] = grad[:, None, :].astype(np.uint8)
    # dithered band transitions (pixel-art gradient look)
    for i, yb in enumerate(range(60, cv.h, 60)):
        cv.dither(0, yb, cv.w, 2, "bg2" if i % 2 else "bg1", phase=i)
    rng = np.random.default_rng(seed)
    n = 46
    xs, ys_, ph = rng.integers(0, cv.w, n), rng.integers(0, cv.h, n), rng.random(n) * 6.28
    for x, y, p in zip(xs, ys_, ph):
        v = np.sin(t * 2.0944 + p)  # 4 cycles per 12s loop
        if v > 0.55:
            cv.rect(x, y, 1, 1, "gold_l")
            if v > 0.9:
                cv.rect(x - 1, y, 3, 1, "gold")
                cv.rect(x, y - 1, 1, 3, "gold")
        elif v > 0.1:
            cv.rect(x, y, 1, 1, "purple")


# ---------------------------------------------------------------- output
_VIGNETTE = None


def to_output(cv):
    """Upscale 4x (nearest) and add scanlines + vignette for a CRT feel."""
    global _VIGNETTE
    big = np.repeat(np.repeat(cv.a, SCALE, 0), SCALE, 1).astype(np.float32)
    H, W = big.shape[:2]
    if _VIGNETTE is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        vig = 1.0 - 0.28 * np.clip(d - 0.35, 0, 1)
        scan = np.where((yy % SCALE) == SCALE - 1, 0.80, 1.0)
        _VIGNETTE = (vig * scan)[..., None].astype(np.float32)
    big *= _VIGNETTE
    return np.clip(big, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- easing
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def seg(t, t0, t1):
    return clamp01((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in(x):
    return x ** 3


def ease_io(x):
    return 3 * x * x - 2 * x * x * x


def back_out(x):
    s = 1.70158
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
