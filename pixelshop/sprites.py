"""Original pixel sprites (ASCII art + a few procedural ones), returned as RGBA arrays."""
import numpy as np
from .gfx import PAL

KEY = {
    "k": (10, 6, 18), "w": (255, 244, 224), "l": (200, 206, 220), "g": (150, 150, 168),
    "G": (82, 82, 104), "y": (255, 204, 51), "Y": (255, 236, 140), "o": (214, 140, 28),
    "O": (255, 138, 36), "r": (255, 77, 90), "R": (150, 24, 48), "b": (52, 120, 230),
    "B": (20, 40, 120), "c": (95, 211, 232), "n": (160, 98, 48), "N": (96, 56, 26),
    "t": (222, 186, 120), "T": (176, 136, 80), "e": (86, 224, 122), "E": (34, 120, 70),
    "s": (241, 194, 125), "S": (200, 146, 92), "p": (142, 91, 214), "h": (92, 52, 28),
    "H": (190, 190, 200), "z": (255, 255, 255),
}


def ascii_sprite(rows, key=KEY):
    w = max(len(r) for r in rows)
    out = np.zeros((len(rows), w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in key:
                out[y, x, :3] = key[ch]
                out[y, x, 3] = 255
    return out


def recolor(spr, mapping):
    out = spr.copy()
    for src, dst in mapping.items():
        m = (out[..., 3] > 0) & np.all(out[..., :3] == np.array(KEY[src], np.uint8), axis=-1)
        out[m, :3] = KEY[dst] if isinstance(dst, str) else dst
    return out


COIN = [ascii_sprite(r) for r in (
    ["..kkkk..", ".kyyyyk.", "kyYyyyok", "kyYyyyok", "kyyyyyok", "kyyyyyok", ".kooook.", "..kkkk.."],
    ["..kkk...", ".kyyok..", ".kYyok..", ".kyyok..", ".kyyok..", ".kyyok..", ".koook..", "..kkk..."],
    ["...kk...", "...kok..", "...kok..", "...kok..", "...kok..", "...kok..", "...kok..", "...kk..."],
)]

MONEYBAG = ascii_sprite([
    ".....kkkk.....",
    "....kTttTk....",
    ".....kNNk.....",
    "....kttttk....",
    "...kttttttk...",
    "..kttttYtttk..",
    ".ktttkYYYkttk.",
    ".kttYtYtttttk.",
    "kttttkYYYktttk",
    "kttttttYtYtttk",
    "kttttkYYYktttk",
    "ktttttTYtttttk",
    ".kTtttttttttk.",
    "..kTTTTTTTTk..",
    "...kkkkkkkk...",
])

ROCKET = ascii_sprite([
    "....r....",
    "...kwk...",
    "...kwk...",
    "..kwwwk..",
    "..kwwwk..",
    "..kkkkk..",
    "..kwwwk..",
    "..kwwwk..",
    "..kwGwk..",
    "..kwwwk..",
    "..kkkkk..",
    ".kwwwwwk.",
    ".kwwwwwk.",
    ".kwwwwwk.",
    ".kkkkkkk.",
    ".kwwwwwk.",
    ".kwwGwwk.",
    ".kwwwwwk.",
    ".kwwwwwk.",
    ".kwwwwwk.",
    "kkwwwwwkk",
    "kwkwwwkwk",
    "kkkkkkkkk",
])
FLAME = [ascii_sprite(r) for r in (
    ["..kO.Ok..", "..OyOyO..", "...yYy...", "....Y...."],
    ["..kOOOk..", "...yOy...", "...OyO...", "....y...."],
)]

BURGER = ascii_sprite([
    "....kkkkkkkk....",
    "..kkooOOOOookk..",
    ".koOOYOOOOYOOOk.",
    "kOOOOOOOYOOOOOOk",
    "kOYOOOOOOOOOYOOk",
    "kkkkkkkkkkkkkkkk",
    "keEeEeEeEeEeEeEk",
    "krrrrrrrrrrrrrrk",
    "kNNNNNNNNNNNNNNk",
    "kNhNNNhNNNNhNNNk",
    "kyyyyyyyyyyyyyyk",
    "kOOOOOOOOOOOOOOk",
    ".koooooooooooook.",
    "..kkkkkkkkkkkk..",
])

FOOTBALL = ascii_sprite([
    ".....kkkkkkk.....",
    "...kknnnnnnnkk...",
    "..knnwnnnnnwnnk..",
    ".knnnwnnnnnwnnnk.",
    "knnnnwnwwwnwnnnnk" ,
    "knnnnwnnnnnwnnnnk",
    "knnnnwnwwwnwnnnnk",
    ".knnnwnnnnnwnnnk.",
    "..knnwnnnnnwnnk..",
    "...kknnnnnnnkk...",
    ".....kkkkkkk.....",
])

CASTLE = ascii_sprite([
    "...b.........b.........b...",
    "..kbk.......kbk.......kbk..",
    ".kbbbk.....kbbbk.....kbbbk.",
    "kbbbbbk...kbbbbbk...kbbbbbk",
    "kkkkkkk...kkkkkkk...kkkkkkk",
    ".kwwwk.....kwwwk.....kwwwk.",
    ".kwkwk.....kwkwk.....kwkwk.",
    ".kwwwkkkkkkkwwwkkkkkkkwwwk.",
    ".kwwwkwkwkwkwwwkwkwkwkwwwk.",
    ".kwwwwwwwwwwwwwwwwwwwwwwwk.",
    ".kwwwwkwwwwwwwwwwwwwkwwwwk.",
    ".kwwwwkwwwwwkkkwwwwwkwwwwk.",
    ".kwwwwwwwwwkbbbkwwwwwwwwwk.",
    ".kwwwwwwwwkbbbbbkwwwwwwwwk.",
    ".kwwwwwwwwkbbbbbkwwwwwwwwk.",
    ".kllllllllkbbbbbklllllllllk",
    ".kkkkkkkkkkkkkkkkkkkkkkkkk.",
])

BIRD = ascii_sprite([
    "........kkkk..",
    ".......kbbbbk.",
    "......kbbbwkbk",
    "k....kbbbbbbyy",
    "kbk.kbbbbbbk..",
    "kbbkbbbbbbbk..",
    ".kbbbbbbbbk...",
    "..kbbbbbbk....",
    "...kbbbbk.....",
    "....kkkk......",
])

CAR = ascii_sprite([
    "...........kkkkkkkkkk...........",
    "........kkkBBBBBBBBBBkkk........",
    "......kkBBBcccBBBcccBBBBkk......",
    "....kkBBBBcccckBkccccBBBBBkk....",
    "..kkbbbbbbbbbbkbkbbbbbbbbbbbkk..",
    ".kbbbbbbbbbbbbkbkbbbbbbbbbbbbbk.",
    "kyBBBBBBBBBBBBkbkBBBBBBBBBBBBBrk",
    "kBBBkkkkBBBBBBkbkBBBBBBkkkkBBBBk",
    "kBBkGGGGkBBBBBBBBBBBBBkGGGGkBBBk",
    ".kkGGlGGGkkkkkkkkkkkkkGGlGGGkkk.",
    "...kGGGGk.............kGGGGk....",
    "....kkkk...............kkkk.....",
])

DESK = ascii_sprite([
    "......kkkkkkkkkk..........",
    "......kGGGGGGGGk..........",
    "......kGccccccGk..........",
    "......kGcbcbccGk..........",
    "......kGccccccGk..........",
    "......kGGGGGGGGk..........",
    "........kkGGkk............",
    "kkkkkkkkkkkkkkkkkkkkkkkkkk",
    "knnnnnnnnnnnnnnnnnnnnnnnnk",
    "kNNNNNNNNNNNNNNNNNNNNNNNNk",
    ".kNk..................kNk.",
    ".kNk..................kNk.",
    ".kNk..................kNk.",
    ".kkk..................kkk.",
])

_WORKER = [
    "...kkkk...",
    "..khhhhk..",
    ".khhhhhhk.",
    ".khssssk..",
    ".kssksks..",
    ".kssssssk.",
    "..kssssk..",
    "..kbbbbk..",
    ".kbbwrwbbk",
    "kbbbwrwbbk",
    "ksbbbrbbsk",
    "ksbbbbbbsk",
    ".kkGGGGkk.",
    "..kGGkGGk.",
    "..kGGkGGk.",
    "..kGGkGGk.",
    "..kkk.kkk.",
]
WORKER = [ascii_sprite(_WORKER),
          ascii_sprite(_WORKER[:9] + ["kbbbwrwbsk", "kbbbbrbbbk", "ksbbbbbbbk"] + _WORKER[12:])]


def worker(age_frac, frame=0):
    """Hair goes brown -> gray -> white with age."""
    spr = WORKER[frame % 2]
    if age_frac > 0.75:
        return recolor(spr, {"h": "w"})
    if age_frac > 0.4:
        return recolor(spr, {"h": "H"})
    return spr


CALENDAR = ascii_sprite([
    "kkkkkkkkkkkkkk",
    "krrrrrrrrrrrrk",
    "krrkrrrrrrkrrk",
    "kwwwwwwwwwwwwk",
    "kwwwwwwwwwwwwk",
    "kwGwGwGwGwGwwk",
    "kwwwwwwwwwwwwk",
    "kwGwGwGwGwGwwk",
    "kwwwwwwwwwwwwk",
    "kwGwGwGwGwwwwk",
    "kwwwwwwwwwwwwk",
    "kkkkkkkkkkkkkk",
])

SUN = ascii_sprite([
    "...y..y...",
    "y..yyyy..y",
    "..yYYYYy..",
    ".yYYYYYYy.",
    "yyYYYYYYyy",
    "yyYYYYYYyy",
    ".yYYYYYYy.",
    "..yYYYYy..",
    "y..yyyy..y",
    "...y..y...",
])
MOON_SMALL = ascii_sprite([
    "...kkkk...",
    "..kllllk..",
    ".klllgllk.",
    "kllllllgk.",
    "klglllllk.",
    "kllllllk..",
    ".klllgk...",
    "..kkkk....",
])


def moon(r=20, seed=3):
    """Procedural shaded moon with craters."""
    d = 2 * r + 2
    out = np.zeros((d, d, 4), np.uint8)
    yy, xx = np.mgrid[0:d, 0:d]
    cx = cy = r + 0.5
    dist = np.hypot(xx - cx, yy - cy)
    inside = dist <= r
    edge = (dist <= r + 1) & ~inside
    shade = np.clip(0.55 + 0.6 * (-(xx - cx) - (yy - cy)) / (2 * r), 0, 1)
    levels = np.array([PAL["gray_d"], PAL["gray"], (200, 206, 220), (232, 236, 244)], np.uint8)
    bayer = np.array([[0, 2], [3, 1]]) / 4.0
    q = np.clip((shade * 3 + bayer[yy % 2, xx % 2] - 0.4).astype(int), 0, 3)
    rgb = levels[q]
    rng = np.random.default_rng(seed)
    for _ in range(9):
        a = rng.uniform(0, 6.28)
        rr = rng.uniform(0, r * 0.75)
        cr = rng.uniform(1.5, r * 0.22)
        mx, my = cx + rr * np.cos(a), cy + rr * np.sin(a)
        cm = (np.hypot(xx - mx, yy - my) <= cr) & inside
        rgb[cm] = levels[np.maximum(q[cm] - 1, 0)]
        rim = (np.hypot(xx - mx - 0.8, yy - my - 0.8) <= cr) & ~(np.hypot(xx - mx, yy - my) <= cr) & inside
        rgb[rim] = levels[np.minimum(q[rim] + 1, 3)]
    out[inside, :3] = rgb[inside]
    out[inside, 3] = 255
    out[edge, :3] = PAL["ink"]
    out[edge, 3] = 255
    return out


MOON = moon()

SPARK = ascii_sprite(["..Y..", "..Y..", "YYzYY", "..Y..", "..Y.."])
